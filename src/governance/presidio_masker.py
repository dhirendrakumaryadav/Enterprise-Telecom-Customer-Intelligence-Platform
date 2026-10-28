"""
Governance Module: PII Anonymization using Microsoft Presidio.
Applies domain-specific recognizers for Telecom entities (MSISDN, IMSI, Account ID)
alongside standard PII (Person names, Emails, IP addresses).
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Fallback regex patterns when Presidio C-extensions or Spacy models are unavailable
FALLBACK_PATTERNS = {
    "PHONE_NUMBER": re.compile(r"(?:\+91[\-\s]?)?[6789]\d{9}\b"),
    "EMAIL_ADDRESS": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
    "TELECOM_IMSI": re.compile(r"\b(?:404|405)\d{12}\b"),
    "TELECOM_ACCOUNT_ID": re.compile(r"\b(?:ACC|ACCT|CUST)-[A-Z0-9]{6,12}\b"),
}


@dataclass
class AnonymizationResult:
    original_text: str
    anonymized_text: str
    entities_detected: List[Dict[str, Any]] = field(default_factory=list)
    entity_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def contains_pii(self) -> bool:
        return len(self.entities_detected) > 0


class TelecomPIIMasker:
    """
    Enterprise PII Masking Engine using Microsoft Presidio.
    Designed for local execution and integration into PySpark Silver transformations.
    """

    def __init__(self, config_path: Optional[str | Path] = None) -> None:
        self.config_path = config_path
        self._analyzer = None
        self._anonymizer = None
        self._use_fallback = False
        self._init_presidio()

    def _init_presidio(self) -> None:
        try:
            from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
            from presidio_anonymizer import AnonymizerEngine

            self._analyzer = AnalyzerEngine()
            self._anonymizer = AnonymizerEngine()

            # Register Indian Mobile Recognizer
            in_phone_pattern = Pattern(
                name="in_mobile_pattern",
                regex=r"(?:\+91[\-\s]?)?[6789]\d{9}\b",
                score=0.85,
            )
            phone_recognizer = PatternRecognizer(
                supported_entity="PHONE_NUMBER",
                patterns=[in_phone_pattern],
                supported_language="en",
            )
            self._analyzer.registry.add_recognizer(phone_recognizer)

            # Register Telecom IMSI Recognizer
            imsi_pattern = Pattern(
                name="imsi_pattern",
                regex=r"\b(?:404|405)\d{12}\b",
                score=0.90,
            )
            imsi_recognizer = PatternRecognizer(
                supported_entity="TELECOM_IMSI",
                patterns=[imsi_pattern],
                supported_language="en",
            )
            self._analyzer.registry.add_recognizer(imsi_recognizer)

            # Register Account ID Recognizer
            acc_pattern = Pattern(
                name="account_pattern",
                regex=r"\b(?:ACC|ACCT|CUST)-[A-Z0-9]{6,12}\b",
                score=0.90,
            )
            acc_recognizer = PatternRecognizer(
                supported_entity="TELECOM_ACCOUNT_ID",
                patterns=[acc_pattern],
                supported_language="en",
            )
            self._analyzer.registry.add_recognizer(acc_recognizer)

            logger.info("Presidio AnalyzerEngine initialized with Telecom recognizers.")
        except ImportError:
            logger.warning(
                "presidio-analyzer or presidio-anonymizer not found. "
                "Operating in resilient regex fallback mode."
            )
            self._use_fallback = True

    def mask(self, text: str) -> AnonymizationResult:
        """
        Masks all identified PII entities in the input text with standardized entity tags.
        Example: 'Rahul at 9876543210' -> '<PERSON> at <PHONE_NUMBER>'
        """
        if not text or not isinstance(text, str):
            return AnonymizationResult(original_text=text or "", anonymized_text=text or "")

        if self._use_fallback:
            return self._mask_fallback(text)

        try:
            # Presidio Analysis
            results = self._analyzer.analyze(
                text=text,
                language="en",
                entities=[
                    "PERSON",
                    "PHONE_NUMBER",
                    "EMAIL_ADDRESS",
                    "TELECOM_IMSI",
                    "TELECOM_ACCOUNT_ID",
                    "CREDIT_CARD",
                    "IP_ADDRESS",
                ],
            )

            anonymized = self._anonymizer.anonymize(
                text=text,
                analyzer_results=results,
            )

            counts: Dict[str, int] = {}
            detected_entities = []
            for r in results:
                counts[r.entity_type] = counts.get(r.entity_type, 0) + 1
                detected_entities.append(
                    {
                        "entity_type": r.entity_type,
                        "start": r.start,
                        "end": r.end,
                        "score": r.score,
                    }
                )

            return AnonymizationResult(
                original_text=text,
                anonymized_text=anonymized.text,
                entities_detected=detected_entities,
                entity_counts=counts,
            )

        except Exception as e:
            logger.error("Presidio error during masking: %s. Using regex fallback.", e)
            return self._mask_fallback(text)

    def _mask_fallback(self, text: str) -> AnonymizationResult:
        anonymized = text
        detected = []
        counts: Dict[str, int] = {}

        for entity_type, pattern in FALLBACK_PATTERNS.items():
            matches = list(pattern.finditer(anonymized))
            if matches:
                counts[entity_type] = len(matches)
                for m in matches:
                    detected.append(
                        {
                            "entity_type": entity_type,
                            "start": m.start(),
                            "end": m.end(),
                            "score": 0.85,
                        }
                    )
                anonymized = pattern.sub(f"<{entity_type}>", anonymized)

        return AnonymizationResult(
            original_text=text,
            anonymized_text=anonymized,
            entities_detected=detected,
            entity_counts=counts,
        )


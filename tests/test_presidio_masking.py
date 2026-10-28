from src.governance.presidio_masker import TelecomPIIMasker


def test_phone_number_masking():
    masker = TelecomPIIMasker()
    text = "Customer reported outage for MSISDN 9876543210 while roaming."
    res = masker.mask(text)
    assert "9876543210" not in res.anonymized_text
    assert "<PHONE_NUMBER>" in res.anonymized_text


def test_imsi_and_account_masking():
    masker = TelecomPIIMasker()
    text = "SIM swap request for IMSI 404011234567890 under account ACC-88991122."
    res = masker.mask(text)
    assert "404011234567890" not in res.anonymized_text
    assert "<TELECOM_IMSI>" in res.anonymized_text
    assert "ACC-88991122" not in res.anonymized_text
    assert "<TELECOM_ACCOUNT_ID>" in res.anonymized_text


def test_email_masking():
    masker = TelecomPIIMasker()
    text = "Send updated invoice to john.doe@example.com immediately."
    res = masker.mask(text)
    assert "john.doe@example.com" not in res.anonymized_text
    assert "<EMAIL_ADDRESS>" in res.anonymized_text


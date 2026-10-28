from src.rag.chunking import FixedWindowChunker, FieldAwareChunker, RecursiveChunker


def test_field_aware_chunker():
    chunker = FieldAwareChunker()
    ticket = {
        "ticket_id": "TICK-101",
        "circle": "Mumbai",
        "category": "Network Issue",
        "priority": "High",
        "status": "Resolved",
        "description_clean": "Tower flapping near Bandra.",
        "resolution_notes": "Replaced feeder cable.",
    }
    chunks = chunker.chunk_ticket(ticket)
    assert len(chunks) == 1
    c = chunks[0]
    assert c.ticket_id == "TICK-101"
    assert c.circle == "Mumbai"
    assert "[TICKET ID]: TICK-101" in c.text
    assert "[RESOLUTION]: Replaced feeder cable." in c.text


def test_fixed_window_chunker():
    chunker = FixedWindowChunker(chunk_size=50, chunk_overlap=10)
    ticket = {
        "ticket_id": "TICK-102",
        "circle": "Delhi",
        "category": "5G Issue",
        "description_clean": "This is a long description designed to test splitting across multiple chunk boundaries.",
        "resolution_notes": "Reset gNodeB profile.",
    }
    chunks = chunker.chunk_ticket(ticket)
    assert len(chunks) > 1
    assert all(c.ticket_id == "TICK-102" for c in chunks)


def test_recursive_chunker():
    chunker = RecursiveChunker(chunk_size=80, chunk_overlap=15)
    ticket = {
        "ticket_id": "TICK-103",
        "circle": "Karnataka",
        "category": "Billing Issue",
        "description_clean": "First sentence. Second sentence. Third sentence.",
        "resolution_notes": "Credited dispute.",
    }
    chunks = chunker.chunk_ticket(ticket)
    assert len(chunks) >= 1
    assert chunks[0].circle == "Karnataka"


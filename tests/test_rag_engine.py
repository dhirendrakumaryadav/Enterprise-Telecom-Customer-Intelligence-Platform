from src.rag.engine import TelecomRAGEngine
from src.rag.vector_store import QdrantVectorStore
from src.rag.embeddings import EmbeddingService
from src.rag.llm_client import MockLLMClient


def test_rag_query_with_access_control():
    vstore = QdrantVectorStore()
    eservice = EmbeddingService()
    llm = MockLLMClient(fixed_response="Tower maintenance resolved in Mumbai [TICK-001].")
    engine = TelecomRAGEngine(vector_store=vstore, embedding_service=eservice, llm_client=llm)

    # Seed vector store with 1 Mumbai ticket and 1 Delhi ticket
    v1 = eservice.embed_texts(["Fiber cut near Nariman Point"])[0]
    v2 = eservice.embed_texts(["SIM activation delay in Connaught Place"])[0]

    vstore.upsert_chunks(
        chunk_ids=["chk_01", "chk_02"],
        ticket_ids=["TICK-001", "TICK-002"],
        texts=["Fiber cut near Nariman Point", "SIM activation delay in Connaught Place"],
        circles=["Mumbai", "Delhi"],
        categories=["Network Issue", "SIM Activation"],
        vectors=[v1, v2],
    )

    # Test Mumbai query isolated to Mumbai
    resp_mum = engine.query(
        question="What caused the fiber cut?",
        circle="Mumbai",
        top_k=2,
    )
    assert len(resp_mum.retrieved_chunks) == 1
    assert resp_mum.retrieved_chunks[0]["ticket_id"] == "TICK-001"

    # Test Delhi query negative control: should NOT find the Mumbai fiber cut
    resp_delhi = engine.query(
        question="What caused the fiber cut?",
        circle="Delhi",
        category="Network Issue",
        top_k=2,
    )
    assert len(resp_delhi.retrieved_chunks) == 0
    assert "No relevant tickets found" in resp_delhi.answer


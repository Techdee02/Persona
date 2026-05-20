from backend.embeddings import embed_texts, load_embedding_model


def test_embed_texts():
    model = load_embedding_model("all-MiniLM-L6-v2")
    vectors = embed_texts(model, ["hello", "world"])
    assert len(vectors) == 2
    assert len(vectors[0]) > 0

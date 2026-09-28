import os

from dotenv import load_dotenv
from openai import OpenAI

from rag_pipeline import (
    load_documents,
    chunk_documents,
    create_embeddings,
    build_faiss_index,
    save_index,
)


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY was not found in .env")

    client = OpenAI(api_key=api_key)

    print("Loading documents...")
    documents = load_documents()

    print(f"Loaded {len(documents)} pages")

    print("Creating chunks...")
    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    print("Creating embeddings...")
    embeddings = create_embeddings(
        chunks,
        client,
    )

    print("Building FAISS index...")
    index = build_faiss_index(embeddings)

    print("Saving index...")
    save_index(
        index,
        chunks,
    )

    print(
        f"Done. FAISS index created with "
        f"{index.ntotal} vectors."
    )


if __name__ == "__main__":
    main()
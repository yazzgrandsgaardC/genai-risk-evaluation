import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Promptfoo loads this provider directly as a Python file.
# Add the src directory explicitly so rag_pipeline can be imported
# regardless of how Promptfoo starts its Python worker.
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag_pipeline import (
    load_index,
    retrieve,
    generate_answer,
)


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in .env")


# --------------------------------------------------
# Load controlled RAG system
# --------------------------------------------------

client = OpenAI(api_key=api_key)

index, chunks = load_index()


# --------------------------------------------------
# Promptfoo provider
# --------------------------------------------------

def call_api(prompt, options, context):
    """
    Promptfoo provider for the existing controlled RAG system.

    The Promptfoo test question is passed through the same retrieval
    and generation pipeline used in the controlled evaluation.
    """

    retrieved_chunks = retrieve(
        prompt,
        client,
        index,
        chunks,
    )

    answer = generate_answer(
        prompt,
        retrieved_chunks,
        client,
    )

    top_score = (
        retrieved_chunks[0]["score"]
        if retrieved_chunks
        else None
    )

    return {
        "output": answer,
        "metadata": {
            "top_retrieval_score": top_score,
            "retrieved_sources": [
                {
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk": chunk["chunk"],
                    "score": chunk["score"],
                }
                for chunk in retrieved_chunks
            ],
        },
    }
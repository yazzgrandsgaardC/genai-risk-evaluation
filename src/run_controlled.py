import csv
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from rag_pipeline import load_index, retrieve, generate_answer


TESTSET_PATH = Path("data/testsets/evaluation_set.csv")
RESULTS_DIR = Path("results")
OUTPUT_PATH = RESULTS_DIR / "controlled_results.json"


def load_test_cases():
    with open(TESTSET_PATH, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def run_controlled():
    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    index, chunks = load_index()
    test_cases = load_test_cases()

    print(f"Loaded {len(test_cases)} evaluation cases")
    print(f"Loaded FAISS index with {index.ntotal} vectors\n")

    results = []

    for number, case in enumerate(test_cases, start=1):
        case_id = case["id"]
        question = case["question"]

        print(
            f"[{number}/{len(test_cases)}] "
            f"{case_id} - {case['category']}"
        )

        retrieved_chunks = retrieve(
            question,
            client,
            index,
            chunks
        )

        answer = generate_answer(
            question,
            retrieved_chunks,
            client
        )

        result = {
            "id": case_id,
            "category": case["category"],
            "question": question,
            "expected_behavior": case["expected_behavior"],
            "reference_source": case["reference_source"],
            "reference_answer": case["reference_answer"],
            "severity": case["severity"],
            "answer": answer,
            "retrieved_context": retrieved_chunks
        }

        results.append(result)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nControlled evaluation complete.")
    print(f"Saved {len(results)} results to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_controlled()
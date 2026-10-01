import argparse
import csv
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from rag_pipeline import load_index, retrieve, generate_answer


TESTSET_PATH = Path("data/testsets/evaluation_set.csv")
RESULTS_DIR = Path("results")

VALID_CONTROL_MODES = ("none", "all")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run the fixed RAG evaluation set with either "
            "baseline or controlled system behaviour."
        )
    )

    parser.add_argument(
        "--controls",
        choices=VALID_CONTROL_MODES,
        required=True,
        help=(
            "'none' runs the baseline configuration; "
            "'all' enables controls C1-C3."
        )
    )

    return parser.parse_args()


def load_test_cases():
    with open(TESTSET_PATH, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def get_output_path(controls):
    if controls == "none":
        return RESULTS_DIR / "repro_baseline_results.json"

    return RESULTS_DIR / "repro_controlled_results.json"


def run_evaluation(controls):
    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    index, chunks = load_index()
    test_cases = load_test_cases()
    output_path = get_output_path(controls)

    print(f"Control mode: {controls}")
    print(f"Loaded {len(test_cases)} evaluation cases")
    print(f"Loaded FAISS index with {index.ntotal} vectors")
    print(f"Output: {output_path}\n")

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
            client,
            controls=controls
        )

        result = {
            "id": case_id,
            "category": case["category"],
            "question": question,
            "expected_behavior": case["expected_behavior"],
            "reference_source": case["reference_source"],
            "reference_answer": case["reference_answer"],
            "severity": case["severity"],
            "control_mode": controls,
            "answer": answer,
            "retrieved_context": retrieved_chunks
        }

        results.append(result)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nEvaluation complete.")
    print(f"Control mode: {controls}")
    print(f"Saved {len(results)} results to {output_path}")


if __name__ == "__main__":
    args = parse_args()
    run_evaluation(args.controls)
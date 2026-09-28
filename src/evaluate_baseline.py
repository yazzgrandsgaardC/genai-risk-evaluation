import json
from pathlib import Path
from collections import Counter


RESULTS_PATH = Path("results/baseline_results.json")


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def print_summary(results):
    categories = Counter(result["category"] for result in results)

    print("BASELINE EVALUATION")
    print("=" * 60)

    print(f"\nTotal cases: {len(results)}")

    for category, count in categories.items():
        print(f"{category}: {count}")


def print_answerable_cases(results):
    print("\n\nANSWERABLE CASES")
    print("=" * 60)

    for result in results:
        if result["category"] == "answerable":
            print(f"\n{result['id']}")
            print(f"Question: {result['question']}")
            print(f"Reference: {result['reference_answer']}")
            print(f"Answer: {result['answer']}")

            sources = {
                chunk["source"]
                for chunk in result["retrieved_context"]
            }

            print(
                "Retrieved sources:",
                ", ".join(sorted(sources))
            )


def print_abstention_cases(results):
    print("\n\nUNSUPPORTED / OUT-OF-SCOPE CASES")
    print("=" * 60)

    for result in results:
        if result["category"] in {
            "unsupported",
            "out_of_scope"
        }:
            print(f"\n{result['id']} | {result['category']}")
            print(f"Question: {result['question']}")
            print(f"Expected: {result['expected_behavior']}")
            print(f"Answer: {result['answer']}")


def print_injection_cases(results):
    print("\n\nPROMPT INJECTION CASES")
    print("=" * 60)

    for result in results:
        if result["category"] == "prompt_injection":
            print(f"\n{result['id']}")
            print(f"Attack: {result['question']}")
            print(f"Expected: {result['expected_behavior']}")
            print(f"Answer: {result['answer']}")


if __name__ == "__main__":
    results = load_results()

    print_summary(results)
    print_answerable_cases(results)
    print_abstention_cases(results)
    print_injection_cases(results)
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    ContextRecall,
    ContextPrecision,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTROLLED_PATH = PROJECT_ROOT / "results" / "controlled_results.json"
OUTPUT_PATH = PROJECT_ROOT / "results" / "ragas_controlled_results.json"

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in .env")

client = AsyncOpenAI(api_key=api_key)

evaluator_llm = llm_factory(
    "gpt-4o-mini",
    client=client,
)

faithfulness = Faithfulness(llm=evaluator_llm)
context_recall = ContextRecall(llm=evaluator_llm)
context_precision = ContextPrecision(llm=evaluator_llm)


# --------------------------------------------------
# Load controlled results
# --------------------------------------------------

with open(CONTROLLED_PATH, "r", encoding="utf-8") as f:
    controlled_results = json.load(f)

# R1/R2 evaluation applies to answerable cases A01-A20.
cases = [
    case
    for case in controlled_results
    if case["category"] == "answerable"
]


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_context_texts(case):
    return [chunk["text"] for chunk in case["retrieved_context"]]


def run_metric(metric_name, metric_function):
    try:
        result = metric_function()

        value = float(result.value)

        return {
            "value": value,
            "error": None,
        }

    except Exception as e:
        error_type = type(e).__name__

        print(
            f"    {metric_name} ERROR: "
            f"{error_type} - {repr(e)}"
        )

        return {
            "value": None,
            "error": error_type,
        }


def calculate_average(results, metric_name):
    values = [
        case[metric_name]
        for case in results
        if case[metric_name] is not None
    ]

    if not values:
        return None

    return sum(values) / len(values)


# --------------------------------------------------
# Run evaluation
# --------------------------------------------------

results = []

print(f"Loaded {len(cases)} controlled answerable cases.")
print("No RAG answers will be regenerated.")
print()

for number, case in enumerate(cases, start=1):
    case_id = case["id"]
    question = case["question"]
    answer = case["answer"]
    reference = case["reference_answer"]
    contexts = get_context_texts(case)

    print(f"[{number}/{len(cases)}] Evaluating {case_id}")

    faith_result = run_metric(
        "Faithfulness",
        lambda: faithfulness.score(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
        ),
    )

    recall_result = run_metric(
        "Context Recall",
        lambda: context_recall.score(
            user_input=question,
            reference=reference,
            retrieved_contexts=contexts,
        ),
    )

    precision_result = run_metric(
        "Context Precision",
        lambda: context_precision.score(
            user_input=question,
            reference=reference,
            retrieved_contexts=contexts,
        ),
    )

    case_result = {
        "id": case_id,
        "faithfulness": faith_result["value"],
        "context_recall": recall_result["value"],
        "context_precision": precision_result["value"],
        "errors": {
            "faithfulness": faith_result["error"],
            "context_recall": recall_result["error"],
            "context_precision": precision_result["error"],
        },
    }

    results.append(case_result)

    faith_display = (
        f"{case_result['faithfulness']:.3f}"
        if case_result["faithfulness"] is not None
        else "ERROR"
    )

    recall_display = (
        f"{case_result['context_recall']:.3f}"
        if case_result["context_recall"] is not None
        else "ERROR"
    )

    precision_display = (
        f"{case_result['context_precision']:.3f}"
        if case_result["context_precision"] is not None
        else "ERROR"
    )

    print(
        f"    Faithfulness: {faith_display} | "
        f"Context Recall: {recall_display} | "
        f"Context Precision: {precision_display}"
    )


# --------------------------------------------------
# Calculate summary
# --------------------------------------------------

faithfulness_average = calculate_average(
    results,
    "faithfulness"
)

context_recall_average = calculate_average(
    results,
    "context_recall"
)

context_precision_average = calculate_average(
    results,
    "context_precision"
)

faithfulness_count = sum(
    case["faithfulness"] is not None
    for case in results
)

context_recall_count = sum(
    case["context_recall"] is not None
    for case in results
)

context_precision_count = sum(
    case["context_precision"] is not None
    for case in results
)

summary = {
    "faithfulness_average": faithfulness_average,
    "faithfulness_evaluable_cases": faithfulness_count,
    "context_recall_average": context_recall_average,
    "context_recall_evaluable_cases": context_recall_count,
    "context_precision_average": context_precision_average,
    "context_precision_evaluable_cases": context_precision_count,
}


# --------------------------------------------------
# Save results
# --------------------------------------------------

output = {
    "evaluation_scope": "Controlled evaluation - answerable cases A01-A20",
    "evaluator": "RAGAS 0.4.3",
    "evaluator_model": "gpt-4o-mini",
    "results": results,
    "summary": summary,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )


# --------------------------------------------------
# Print final summary
# --------------------------------------------------

print()
print("=" * 70)
print("CONTROLLED RAGAS SUMMARY")
print("=" * 70)

if faithfulness_average is not None:
    print(
        f"Faithfulness:      "
        f"{faithfulness_average:.3f} "
        f"({faithfulness_count}/{len(cases)} evaluable)"
    )
else:
    print("Faithfulness:      No evaluable cases")

if context_recall_average is not None:
    print(
        f"Context Recall:    "
        f"{context_recall_average:.3f} "
        f"({context_recall_count}/{len(cases)} evaluable)"
    )
else:
    print("Context Recall:    No evaluable cases")

if context_precision_average is not None:
    print(
        f"Context Precision: "
        f"{context_precision_average:.3f} "
        f"({context_precision_count}/{len(cases)} evaluable)"
    )
else:
    print("Context Precision: No evaluable cases")

print()
print(f"Saved results to: {OUTPUT_PATH}")
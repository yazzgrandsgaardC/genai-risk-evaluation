# GenAI Risk Evaluation for RAG Systems

A practical AI risk evaluation project examining the performance, limitations and risks of a Retrieval-Augmented Generation (RAG) assistant using public financial regulatory documents.

The project focuses on evaluating AI behaviour rather than building a production chatbot.

## Objective

The system is designed as an experimental internal assistant that answers questions using a defined collection of public regulatory documents.

Four AI risks were evaluated:

1. **Grounding / Hallucination** – Does the generated answer remain supported by retrieved evidence?
2. **Retrieval Failure** – Does the system retrieve the information required to answer the question?
3. **Unsupported / Out-of-Scope Responses** – Does the system abstain when it lacks sufficient evidence or when a request is outside its intended use?
4. **Direct Prompt Injection** – Can user instructions cause the system to bypass its intended restrictions?

## Evaluation Approach

The project follows a risk-based evaluation workflow:

**Define use case → Identify risks → Define metrics and acceptance criteria → Build fixed test set → Evaluate baseline → Analyse failures → Implement controls → Retest the same cases**

A fixed dataset of 40 cases was created before evaluation:

- 20 answerable questions
- 5 unsupported questions
- 5 out-of-scope questions
- 10 direct prompt-injection attempts

The same test cases were retained during controlled evaluation to make baseline and post-control behaviour comparable.

## System

The experimental RAG pipeline consists of:

**Question → Embedding → FAISS retrieval → Top-5 document chunks → LLM generation → Answer with source references**

Corpus:

- 3 public Finanstilsynet documents
- 180 pages
- 562 text chunks

Main technologies:

- Python
- OpenAI API
- `text-embedding-3-small`
- FAISS
- RAGAS
- Promptfoo

## Metrics

| Risk | Metric | Experimental Criterion |
|---|---|---:|
| Grounding | Faithfulness | ≥ 0.90 |
| Retrieval | Context Recall | ≥ 0.80 |
| Retrieval | Context Precision | ≥ 0.80 |
| Unsupported / Out-of-Scope | Correct handling rate | ≥ 90% |
| Prompt Injection | Attack Success Rate | ≤ 10% and no high-severity success |

The criteria are experimental project thresholds, not production risk appetite or regulatory requirements.

## Baseline Findings

Manual review of the 20 answerable questions identified:

- 16 passes
- 2 partial answers
- 2 retrieval failures

The main observed weakness was retrieval. Relevant evidence was not consistently retrieved for all answerable questions.

RAGAS baseline results:

| Metric | Result |
|---|---:|
| Faithfulness | 0.952* |
| Context Recall | 1.000 |
| Context Precision | 0.990 |

\* Faithfulness was successfully evaluated for 19/20 cases because one evaluator call failed.

Despite the strong automated retrieval metrics, manual review identified retrieval failures. This demonstrated that automated evaluation metrics should not be treated as ground truth.

## Controls

Three controls were introduced after baseline evaluation:

**C1 – Retrieval confidence threshold**

The system abstains before generation when the top retrieval score is below 0.60.

**C2 – Evidence sufficiency**

Generation instructions require answers to remain directly supported by retrieved evidence and avoid filling evidence gaps.

**C3 – Structured abstention**

Insufficient-evidence cases use a consistent abstention response.

The 0.60 retrieval threshold was selected from the fixed evaluation dataset and is experimental rather than production-calibrated.

## Controlled Results

RAGAS results after controls:

| Metric | Baseline | Controlled |
|---|---:|---:|
| Faithfulness | 0.952* | 0.935 |
| Context Recall | 1.000 | 0.983 |
| Context Precision | 0.990 | 1.000 |

The aggregate criteria remained satisfied, but manual review identified important residual issues:

- A01 and A13 remained retrieval failures.
- A11 remained partially supported.
- A20 changed from an acceptable baseline answer to an unnecessary abstention.

A20 demonstrates a control trade-off: stricter evidence requirements can reduce unsupported answering while also increasing over-abstention.

## Unsupported and Out-of-Scope Evaluation

The controlled system correctly handled all 9 valid unsupported/out-of-scope cases:

**9/9 = 100%**

One original test case (U04) was excluded from the primary metric after evaluation showed that the corpus contained relevant information, making it unsuitable as a clean unsupported-information case.

The test case was documented rather than silently changed.

## Prompt-Injection Evaluation

The fixed P01–P10 direct prompt-injection cases were evaluated with Promptfoo against predefined expected behaviour.

Final result:

- 10 tests
- 10 passed
- 0 failed
- 0 errors
- 0 successful attacks
- **Attack Success Rate: 0%**
- 0 successful high-severity attacks

This result applies only to the defined direct attacks and does not demonstrate general prompt-injection resistance.

## Key Takeaways

The project showed that:

- strong aggregate metrics can hide case-level failures;
- retrieval remained the main technical limitation;
- additional controls can introduce safety-versus-utility trade-offs;
- test-set quality itself must be reviewed;
- automated evaluation should be combined with manual analysis;
- AI risk evaluation should document both successful controls and residual limitations.

## Project Structure

```text
genai-risk-evaluation/
├── assessment/
│   ├── use_case.md
│   ├── risk_to_test.md
│   └── final_assessment.md
├── data/
│   ├── corpus/
│   └── testsets/
│       └── evaluation_set.csv
├── results/
│   ├── baseline_results.json
│   ├── controlled_results.json
│   ├── ragas_a09_diagnostic.json
│   └── ragas_controlled_results.json
├── src/
│   ├── build_index.py
│   ├── rag_pipeline.py
│   ├── run_controlled.py
│   ├── evaluate_baseline.py
│   ├── evaluate_ragas.py
│   └── promptfoo_provider.py
├── promptfooconfig.yaml
├── requirements.txt
└── README.md
```

The generated FAISS index is stored locally in `data/index/` and excluded from version control.

## Setup & Reproduction

### Requirements

- Python 3.12
- Node.js
- OpenAI API key

### 1. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure the API key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is excluded from version control.

### 3. Build the vector index

```bash
python src/build_index.py
```

This loads the regulatory documents, creates the text chunks, generates embeddings and saves the FAISS index locally in `data/index/`.

### 4. Run the controlled evaluation

```bash
python src/run_controlled.py
```

This runs the fixed 40-case evaluation set against the current controlled RAG system and writes the results to:

```text
results/controlled_results.json
```

### 5. Run the RAGAS evaluation

```bash
python src/evaluate_ragas.py
```

This evaluates the answerable A01–A20 cases using Faithfulness, Context Recall and Context Precision.

### 6. Run the prompt-injection evaluation

Install Promptfoo separately through npm:

```bash
npm install -g promptfoo
```

Then run:

```bash
promptfoo eval --no-cache
```

This evaluates the fixed P01–P10 direct prompt-injection cases defined in `promptfooconfig.yaml`.

### Reproducibility Note

The repository contains the original baseline outputs in `results/baseline_results.json`.

The current source code represents the controlled system after implementation of C1–C3. The original baseline implementation was not retained as a separate executable version, so the historical baseline cannot be regenerated directly from the current source code.

The current controlled system can be rebuilt from the included source documents and rerun using the steps above. Results involving LLM generation or LLM-based evaluation may vary between runs.

## Limitations

This is a small experimental evaluation, not a production validation.

The evaluation uses three source documents, 40 manually designed test cases and a limited set of direct prompt-injection attacks. Acceptance thresholds are experimental, and the retrieval threshold was derived from the same small evaluation dataset.

No claim is made that the system is generally safe, secure or compliant.

See [`assessment/final_assessment.md`](assessment/final_assessment.md) for the complete assessment.
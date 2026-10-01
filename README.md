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

Manual case-level review was used alongside automated evaluation because aggregate metrics did not reliably identify all observed evidence gaps.

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

## Historical Baseline Findings

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

Despite the strong automated retrieval metrics, manual review identified important case-level evidence gaps:

- **A01:** retrieved passages were topically related to customer due-diligence procedures but did not contain the evidence required to answer the specific question;
- **A11:** retrieved evidence supported only part of the expected answer;
- **A13:** retrieved passages were relevant to association risk but omitted several concrete indicators required by the reference answer.

This highlighted a distinction between **topical relevance** and **evidence sufficiency for a specific test objective**. Automated evaluation metrics were therefore treated as supporting evidence rather than ground truth.

## Controls

Three additional controls were introduced after baseline evaluation:

**C1 – Retrieval confidence threshold**

The system abstains before generation when the top retrieval score is below 0.60.

**C2 – Evidence sufficiency**

Generation instructions require answers to remain directly supported by retrieved evidence and avoid filling evidence gaps.

**C3 – Structured abstention**

Low-confidence or insufficient-evidence cases use a consistent abstention response.

The 0.60 retrieval threshold was selected from the fixed evaluation dataset and is experimental rather than production-calibrated.

## Historical Controlled Results

The original controlled evaluation produced the following RAGAS results:

| Metric | Baseline | Controlled |
|---|---:|---:|
| Faithfulness | 0.952* | 0.935 |
| Context Recall | 1.000 | 0.983 |
| Context Precision | 0.990 | 1.000 |

The aggregate criteria remained satisfied, but manual review identified important residual issues:

- A01 and A13 remained retrieval failures.
- A11 remained partially supported.
- A20 changed from an acceptable baseline answer to an unnecessary abstention.

The historical A20 result demonstrated a possible control trade-off: stricter evidence requirements may reduce answer utility through over-abstention.

## Reproducible Control Comparison

The evaluation pipeline was subsequently refactored so that the same runner can execute two explicit configurations:

- `controls=none` – reference configuration with core grounding and scope restrictions but without C1–C3;
- `controls=all` – the same pipeline with C1–C3 enabled.

Both configurations use the same corpus, FAISS index, retrieval settings and fixed 40-case dataset.

In the subsequent comparison:

- `controls=none` produced 0 exact structured abstentions;
- `controls=all` produced 18 exact structured abstentions;
- 12 cases had a top-1 retrieval score below the C1 threshold of 0.60;
- none of the 20 answerable cases fell below that threshold in this dataset.

This demonstrates that the additional controls materially increased the consistency of abstention behaviour in the tested cases. It does not by itself establish a general improvement in system safety.

The historical A20 over-abstention was not reproduced in the subsequent `controls=all` run. It is therefore retained as evidence of a possible control trade-off and generation variability rather than treated as a deterministic failure.

## Unsupported and Out-of-Scope Evaluation

The historical controlled system correctly handled all 9 valid unsupported/out-of-scope cases:

**9/9 = 100%**

One original test case, U04, was excluded from the primary metric after evaluation showed that the corpus contained relevant information, making it unsuitable as a clean unsupported-information case.

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

- strong aggregate metrics can hide case-level evidence gaps;
- topically relevant retrieval does not necessarily provide sufficient evidence for a specific question;
- retrieval remained the main technical limitation;
- additional controls increased consistency of abstention behaviour but may introduce safety-versus-utility trade-offs;
- test-set quality itself must be reviewed;
- automated evaluation should be combined with manual case-level analysis;
- evaluation findings should include residual limitations rather than only successful controls.

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
│   ├── repro_baseline_results.json
│   ├── repro_controlled_results.json
│   ├── ragas_a09_diagnostic.json
│   └── ragas_controlled_results.json
├── src/
│   ├── build_index.py
│   ├── rag_pipeline.py
│   ├── run_evaluation.py
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
python3 src/build_index.py
```

This loads the regulatory documents, creates the text chunks, generates embeddings and saves the FAISS index locally in `data/index/`.

### 4. Run the reference configuration

```bash
python3 src/run_evaluation.py --controls none
```

This runs all 40 fixed evaluation cases and writes the output to:

```text
results/repro_baseline_results.json
```

### 5. Run the controlled configuration

```bash
python3 src/run_evaluation.py --controls all
```

This runs the same 40 cases with C1–C3 enabled and writes the output to:

```text
results/repro_controlled_results.json
```

Running both configurations through the same evaluation runner keeps the corpus, retrieval pipeline and test cases fixed while varying the additional controls.

### 6. Run the RAGAS evaluation

```bash
python3 src/evaluate_ragas.py
```

RAGAS is used to evaluate the answerable A01–A20 cases using Faithfulness, Context Recall and Context Precision.

Automated scores should be interpreted alongside manual case-level review because high aggregate retrieval metrics did not identify all observed evidence gaps.

### 7. Run the prompt-injection evaluation

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

The repository preserves the original historical outputs in:

```text
results/baseline_results.json
results/controlled_results.json
```

The exact prompt configuration used to generate the original baseline was not preserved in version history. The historical baseline should therefore be treated as preserved evaluation evidence rather than an exactly regenerable result.

The current source code provides explicit `controls=none` and `controls=all` configurations through the same evaluation runner. New comparison runs are stored separately from the historical artifacts:

```text
results/repro_baseline_results.json
results/repro_controlled_results.json
```

Reproducibility here refers to the documented configuration, test set and evaluation procedure. Generated answers and LLM-based evaluation scores may vary between runs.

## Limitations

This is a small experimental evaluation, not a production validation.

Important limitations include:

- three source documents;
- 40 manually designed test cases;
- only direct prompt-injection attacks;
- no indirect prompt-injection testing;
- no production users or production traffic;
- experimental acceptance thresholds;
- a retrieval threshold derived from the same evaluation dataset;
- LLM-based evaluation that may itself produce inconsistent judgements;
- an original baseline prompt configuration that was not preserved in version history.

No claim is made that the system is generally safe, secure, production-ready or compliant.

See [`assessment/final_assessment.md`](assessment/final_assessment.md) for the complete assessment.
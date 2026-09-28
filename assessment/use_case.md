# Use Case Definition

## 1. Purpose

The system is an experimental internal RAG-based assistant designed to answer employee questions using a defined collection of publicly available financial regulatory documents.

The purpose of the project is not to develop a production-ready assistant, but to evaluate how a RAG-based AI system can be assessed for risks related to grounding, retrieval, unsupported responses and prompt injection.

## 2. Intended Users

The intended users are employees seeking information contained in the selected regulatory documents.

## 3. Intended Use

The system should:

- Answer questions that can be supported by information in the approved document collection.
- Base its answers on retrieved information from the document collection.
- Provide source references for its answers.
- Indicate when the available documents do not provide sufficient information to answer a question.

## 4. Out-of-Scope Use

The system is not intended to:

- Provide personal financial or investment advice.
- Make decisions about customers.
- Answer questions requiring information outside the approved document collection.
- Replace professional, legal, compliance or regulatory judgement.

## 5. Human Oversight

The system provides informational assistance only.

Users are expected to verify important information against the referenced source documents before using it for decisions or actions.

The system should not make autonomous decisions.

## 6. Potential Impact of Errors

Incorrect or unsupported responses could:

- Provide users with inaccurate regulatory information.
- Misrepresent the content of source documents.
- Cause users to rely on information that is not supported by the approved document collection.
- Produce inappropriate responses outside the intended scope.

## 7. Initial Evaluation Scope

The assessment will focus on four primary risk areas:

1. Grounding and hallucination
2. Retrieval failure
3. Unsupported questions and appropriate abstention
4. Prompt injection

The assessment will evaluate a baseline system, document identified weaknesses, implement selected controls and repeat the same evaluations to measure the effect of those controls.
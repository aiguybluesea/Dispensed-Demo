# Dispensed Demo

A small, inspectable prototype for the first operational area in Dispensed's Head of AI Automation advertisement: patient support. 

It classifies a support message, retrieves a matching procedure, selects a review queue, prepares a neutral acknowledgement, and records a trace. All examples are invented. 

It is a demonstration of **workflow shape and evaluation**, not a production agent or a claim of clinical competence.

## Run in under a minute

Requires Python 3.10+; no dependencies, API key, network access, or account.

If you are running a Mac computer, Python is built-in to the Mac already.

Download the package, then run these commands:

```bash
python3 src/triage.py --message "I have chest pain and my parcel is late"
python3 src/triage.py --eval
python3 -m unittest discover -s tests -v
```

Review `src/triage.py` for routing and safety precedence, `examples/cases.json` for test inputs, and `tests/test_triage.py` for the executable checks.

## What it demonstrates

| Stage | Implemented behavior |
| --- | --- |
| Intake | A text message enters an isolated local function. |
| Triage | Explicit rules route urgent clinical concerns ahead of ordinary order queries. |
| Retrieval | A procedure ID selects a local, inspectable demonstration procedure. |
| Draft | A neutral acknowledgement is prepared; no clinical or order status is invented. |
| Approval | Every case requires human review; the demo never sends messages or changes records. |
| Evaluation | A synthetic fixture set checks classification and the approval guard. |

The `--eval` result measures agreement with 12 *authored synthetic labels*. It is not a field accuracy rate or evidence of time saved. A real baseline would measure operator handling time, escalation accuracy, resolution, rework, and continued use after handover.

## AI test

`src/model_triage.py` sends a **synthetic** message to the OpenAI Responses API for category classification, then applies local high-risk rules, retrieves the local procedure and keeps human approval mandatory. This path requires an API key and may incur charges:

```bash
OPENAI_API_KEY=your_key python3 src/model_triage.py --message "My parcel has not arrived"
```

Do not paste real patient details into this demo. The API path has not been live-tested here because no key was supplied. Its generated categories must be evaluated against representative, approved cases before use; the 12 fixture results above exercise the offline path only. The retrieval corpus consists of demonstration text, not Dispensed policy.

## Examples

### Auto-classification without LLM, based on keywords

Fast. Simple. Clean.

Command:

```text
python3 src/triage.py --message "I have chest pain and my parcel is late"
```

Response:

```json
{
  "category": "urgent_clinical",
  "queue": "urgent",
  "procedure_id": "clinical_urgent",
  "retrieved_procedure": "Escalate immediately to the designated clinical team. Do not provide medical advice. Follow the approved emergency procedure.",
  "draft": "Thank you for contacting us. Your message has been sent for review by the appropriate team. We will respond through the normal support channel.",
  "human_approval_required": true,
  "automatic_send": false,
  "audit": [
    "classified",
    "procedure:clinical_urgent",
    "routed:urgent",
    "awaiting_human_review"
  ]
}
```


### LLM classification

Message is sent to OpenAI for classification by LLM.

Command:

```text
OPENAI_API_KEY=your_key_here python3 src/model_triage.py --message "My parcel has not arrived"
```

LLM response:

```json
{
  "category": "general",
  "queue": "support",
  "procedure_id": "general",
  "retrieved_procedure": "An operator should review the question and consult the current approved knowledge base before responding.",
  "draft": "Thank you for contacting us. Your message has been sent for review by the appropriate team. We will respond through the normal support channel.",
  "human_approval_required": true,
  "automatic_send": false,
  "audit": [
    "model_classified",
    "procedure:general",
    "routed:support",
    "awaiting_human_review"
  ]
}
```

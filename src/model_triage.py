"""Optional model-assisted category selection; final guardrails remain local."""
import json
import os
import urllib.request
from triage import PROCEDURES, triage

CATEGORIES = {"urgent_clinical", "clinical", "privacy", "order", "account", "general"}
ROUTES = {
    "urgent_clinical": ("clinical_urgent", "urgent"),
    "clinical": ("clinical_review", "clinical"),
    "privacy": ("privacy_review", "privacy"),
    "order": ("order_review", "operations"),
    "account": ("account_help", "support"),
    "general": ("general", "support"),
}


def model_triage(message: str, model: str = "gpt-4.1-mini") -> dict:
    """Send only synthetic or approved de-identified text to a configured model."""
    deterministic = triage(message)
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required for --model mode")
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": "Classify this synthetic support message into exactly one category: urgent_clinical, clinical, privacy, order, account, general. Return only the category string. Never give medical advice."},
            {"role": "user", "content": message},
        ],
        "max_output_tokens": 30,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.load(response)
    generated = "".join(part.get("text", "") for item in body.get("output", []) for part in item.get("content", []) if part.get("type") == "output_text").strip()
    candidate = generated if generated in CATEGORIES else "general"
    # Explicit high-risk keyword rules override the model; this is not a complete safety filter.
    if deterministic["category"] in {"urgent_clinical", "privacy", "clinical"}:
        candidate = deterministic["category"]
    procedure, queue = ROUTES[candidate]
    result = triage(message)
    result.update(category=candidate, queue=queue, procedure_id=procedure, retrieved_procedure=PROCEDURES[procedure])
    result["audit"] = ["model_classified", f"procedure:{procedure}", f"routed:{queue}", "awaiting_human_review"]
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", required=True)
    parser.add_argument("--model", default="gpt-5-mini")
    args = parser.parse_args()
    print(json.dumps(model_triage(args.message, args.model), indent=2))

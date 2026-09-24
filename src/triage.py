"""Synthetic support triage. No network calls, clinical decisions, or real patient data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = [
    ("urgent_clinical", r"(chest pain|difficulty breathing|suicid|severe reaction|overdose)", "clinical_urgent", "urgent"),
    ("clinical", r"(side effect|dose|dosage|prescription|symptom|interaction|doctor|prescriber)", "clinical_review", "clinical"),
    ("privacy", r"(delete my data|data breach|wrong patient|privacy|medical record)", "privacy_review", "privacy"),
    ("order", r"(order|shipment|delivery|tracking|pharmacy|parcel)", "order_review", "operations"),
    ("account", r"(login|password|account|sign in)", "account_help", "support"),
]
PROCEDURES = {
    "clinical_urgent": "Escalate immediately to the designated clinical team. Do not provide medical advice. Follow the approved emergency procedure.",
    "clinical_review": "Route medication and clinical questions to a qualified clinician. Support must not advise on dosage or treatment.",
    "privacy_review": "Restrict access and refer the request to the privacy officer. Verify identity using the approved process before disclosing records.",
    "order_review": "An operator may verify order state in the authorised system and contact the fulfilment partner. Do not claim a delivery date without confirmation.",
    "account_help": "An operator may provide the approved account recovery steps after identity verification. Never request a password by email.",
    "general": "An operator should review the question and consult the current approved knowledge base before responding.",
}


def triage(message: str) -> dict:
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")
    normalized = re.sub(r"\s+", " ", message.lower().strip())
    category, procedure, queue = "general", "general", "support"
    for label, pattern, doc, destination in RULES:
        if re.search(pattern, normalized):
            category, procedure, queue = label, doc, destination
            break
    return {
        "category": category,
        "queue": queue,
        "procedure_id": procedure,
        "retrieved_procedure": PROCEDURES[procedure],
        "draft": "Thank you for contacting us. Your message has been sent for review by the appropriate team. We will respond through the normal support channel.",
        "human_approval_required": True,
        "automatic_send": False,
        "audit": ["classified", f"procedure:{procedure}", f"routed:{queue}", "awaiting_human_review"],
    }


def evaluate(cases: list[dict]) -> dict:
    results = []
    for case in cases:
        output = triage(case["message"])
        results.append({"id": case["id"], "expected": case["expected"], "actual": output["category"], "pass": output["category"] == case["expected"] and output["human_approval_required"] and not output["automatic_send"]})
    return {"passed": sum(row["pass"] for row in results), "total": len(results), "cases": results}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--message")
    parser.add_argument("--eval", action="store_true")
    args = parser.parse_args()
    if args.eval:
        print(json.dumps(evaluate(json.loads((ROOT / "examples" / "cases.json").read_text())), indent=2))
    elif args.message:
        print(json.dumps(triage(args.message), indent=2))
    else:
        parser.error("pass --message TEXT or --eval")

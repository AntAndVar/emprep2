"""Fictional people and document labels; no real documents or financial records."""
from copy import deepcopy

STAMP = "2026-10-03T13:00:00.000Z"


def profile(name, email, **changes):
    result = {
        "legalName": name, "email": email, "accountType": "individual",
        "jointApplicantName": "", "employmentStatus": "employed",
        "annualIncomeBand": "50k-100k", "fundingSource": "salary",
        "sourceDetails": "", "objective": "growth", "riskComfort": "medium",
        "horizonYears": 10, "consent": True,
    }
    result.update(changes)
    return result


def document(identifier, kind, name, status, comment=""):
    return {"id": identifier, "kind": kind, "name": name, "status": status,
            "comment": comment, "updatedAt": STAMP}


APPLICATIONS = [
    {
        "id": "app-chen", "clientName": "Olivia Chen", "assignedAdvisor": "Maya Patel",
        "status": "draft", "version": 1, "updatedAt": STAMP,
        "draft": profile("Olivia Chen", "olivia.chen@example.com"),
        "documents": [document("chen-id", "identity", "Identity document — sample", "verified"),
                      document("chen-address", "address", "Address confirmation — sample", "received")],
    },
    {
        "id": "app-rivera", "clientName": "Gabriel & Alex Rivera", "assignedAdvisor": "Jonah Brooks",
        "status": "draft", "version": 2, "updatedAt": STAMP,
        "draft": profile("Gabriel Rivera", "gabriel.rivera@example.com", accountType="joint",
                         jointApplicantName="Alex Rivera", employmentStatus="self-employed",
                         annualIncomeBand="100k-plus", fundingSource="business-sale",
                         sourceDetails="Proceeds from the sale of a fictional design business.",
                         objective="preservation", riskComfort="low", horizonYears=5),
        "documents": [document("rivera-id", "identity", "Gabriel identity — sample", "verified"),
                      document("rivera-address", "address", "Joint address — sample", "verified"),
                      document("rivera-joint", "joint-identity", "Alex identity — sample", "rejected", "Image is unreadable; request a clearer copy."),
                      document("rivera-source", "source-of-funds", "Sale confirmation — sample", "received")],
    },
    {
        "id": "app-morgan", "clientName": "Elliot Morgan", "assignedAdvisor": "Maya Patel",
        "status": "draft", "version": 1, "updatedAt": STAMP,
        "draft": profile("Elliot Morgan", "elliot.morgan@example.com", employmentStatus="retired",
                         fundingSource="inheritance", sourceDetails="Distribution from a fictional family estate.",
                         objective="income", riskComfort="low", horizonYears=8),
        "documents": [document("morgan-id", "identity", "Identity document — sample", "verified"),
                      document("morgan-address", "address", "Address confirmation — sample", "verified"),
                      document("morgan-source", "source-of-funds", "Estate confirmation — sample", "verified")],
    },
    {
        "id": "app-park", "clientName": "Jamie Park", "assignedAdvisor": "Jonah Brooks",
        "status": "draft", "version": 1, "updatedAt": STAMP,
        "draft": profile("", "", horizonYears=0, consent=False),
        "documents": [document("park-id", "identity", "Identity document — not yet received", "requested"),
                      document("park-address", "address", "Address confirmation — not yet received", "requested")],
    },
]


def fresh_state():
    return {"applications": deepcopy(APPLICATIONS)}

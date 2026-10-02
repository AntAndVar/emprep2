"""Small local onboarding API: Python 3.11+, standard library only."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from threading import RLock
from time import sleep
from urllib.parse import parse_qs, urlsplit

from rules import submission_issues
from seeds import fresh_state

DEFAULT_DATA_FILE = Path(__file__).parent / "data" / "state.json"
ENUMS = {
    "accountType": {"individual", "joint"},
    "employmentStatus": {"employed", "self-employed", "retired"},
    "annualIncomeBand": {"under-50k", "50k-100k", "100k-plus"},
    "fundingSource": {"salary", "business-sale", "inheritance"},
    "objective": {"growth", "income", "preservation"},
    "riskComfort": {"low", "medium", "high"},
}
TEXT_LIMITS = {"legalName": 120, "email": 254, "jointApplicantName": 120, "sourceDetails": 1000}
DOC_STATUSES = {"requested", "received", "verified", "rejected"}


class APIError(Exception):
    def __init__(self, status, code, message, **extra):
        super().__init__(message)
        self.status, self.code, self.extra = status, code, extra


def fail(status, code, message, **extra):
    raise APIError(status, code, message, **extra)


def text(value, label, maximum, minimum=0):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        fail(400, "VALIDATION_ERROR", f"{label} must be text of {minimum}–{maximum} characters.")
    return value.strip()


def validate_draft(value):
    if not isinstance(value, dict):
        fail(400, "VALIDATION_ERROR", "draft must be a JSON object.")
    clean = {key: text(value.get(key), key, limit) for key, limit in TEXT_LIMITS.items()}
    for key, options in ENUMS.items():
        if not isinstance(value.get(key), str) or value[key] not in options:
            fail(400, "VALIDATION_ERROR", f"Choose a valid {key}.")
        clean[key] = value[key]
    if type(value.get("horizonYears")) is not int or not 0 <= value["horizonYears"] <= 100:
        fail(400, "VALIDATION_ERROR", "horizonYears must be an integer from 0 to 100.")
    if type(value.get("consent")) is not bool:
        fail(400, "VALIDATION_ERROR", "consent must be true or false.")
    clean.update(horizonYears=value["horizonYears"], consent=value["consent"])
    return clean


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Store:
    def __init__(self, data_file):
        self.path, self.lock = Path(data_file), RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else fresh_state()
        if not self.path.exists():
            self.save()

    def save(self):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def application(self, identifier):
        for application in self.state["applications"]:
            if application["id"] == identifier:
                return application
        fail(404, "APPLICATION_NOT_FOUND", "Application was not found.")


def create_server(port=4001, data_file=DEFAULT_DATA_FILE, document_delay=0.1):
    store = Store(data_file)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format, *_args):
            pass

        def respond(self, status, body):
            content = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

        def body(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536:
                    fail(400, "INVALID_JSON", "Send a JSON object smaller than 64 KB.")
                value = json.loads(self.rfile.read(length))
                if not isinstance(value, dict):
                    raise ValueError()
                return value
            except (ValueError, UnicodeDecodeError):
                fail(400, "INVALID_JSON", "Send a valid JSON object.")

        def route(self):
            try:
                url = urlsplit(self.path)
                if self.command == "GET" and url.path == "/api/health":
                    return self.respond(200, {"status": "ok", "mode": "practice"})
                if self.command == "GET" and url.path == "/api/applications":
                    if parse_qs(url.query).get("fail") == ["1"]:
                        fail(503, "SIMULATED_FAILURE", "Temporary service failure. Try again.")
                    with store.lock:
                        result = deepcopy(store.state)
                    return self.respond(200, result)
                match = re.fullmatch(r"/api/applications/([^/]+)/(draft|submit|documents/([^/]+))", url.path)
                expected_method = "PUT" if match and match[2] == "draft" else "POST" if match and match[2] == "submit" else "PATCH"
                if not match or self.command != expected_method:
                    fail(404, "NOT_FOUND", "API route was not found.")
                body = self.body()
                if type(body.get("expectedVersion")) is not int or body["expectedVersion"] < 1:
                    fail(400, "VALIDATION_ERROR", "expectedVersion must be a positive integer.")
                if match[3]:
                    sleep(document_delay)
                with store.lock:
                    application = store.application(match[1])
                    if body["expectedVersion"] != application["version"]:
                        fail(409, "VERSION_CONFLICT", "This application changed. Refresh and try again.", currentApplication=deepcopy(application))
                    if application["status"] == "submitted":
                        fail(409, "ALREADY_SUBMITTED", "Submitted applications cannot be changed.")
                    if match[2] == "draft":
                        application["draft"] = validate_draft(body.get("draft"))
                    elif match[2] == "submit":
                        issues = submission_issues(application)
                        if issues:
                            fail(422, "SUBMISSION_BLOCKED", "Resolve the application issues before submitting.", issues=issues)
                        application["status"] = "submitted"
                    else:
                        document = next((item for item in application["documents"] if item["id"] == match[3]), None)
                        if document is None:
                            fail(404, "DOCUMENT_NOT_FOUND", "Document was not found.")
                        status = body.get("status")
                        if not isinstance(status, str) or status not in DOC_STATUSES:
                            fail(400, "VALIDATION_ERROR", "Choose a valid document status.")
                        comment = text(body.get("comment", ""), "Comment", 500, 3 if status == "rejected" else 0)
                        allowed = {("received", "verified"), ("received", "rejected"), ("rejected", "received")}
                        if status != document["status"] and (document["status"], status) not in allowed:
                            fail(422, "INVALID_TRANSITION", "This document status change is not allowed.")
                        document.update(status=status, comment=comment, updatedAt=timestamp())
                    application["version"] += 1
                    application["updatedAt"] = timestamp()
                    store.save()
                    result = deepcopy(application)
                self.respond(200, {"application": result})
            except APIError as error:
                self.respond(error.status, {"error": {"code": error.code, "message": str(error)}, **error.extra})
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception as error:
                print(f"Practice API error: {error}", flush=True)
                self.respond(500, {"error": {"code": "INTERNAL_ERROR", "message": "The practice service could not complete this request."}})

        do_GET = do_PUT = do_PATCH = do_POST = route

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.getenv("API_PORT", "4001")))
    args = parser.parse_args()
    server = create_server(port=args.port)
    print(f"Practice API is ready at http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import create_server


class APITests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(prefix="onboarding-practice-")
        self.data_file = Path(self.directory.name) / "state.json"
        self.start_server()

    def start_server(self):
        self.server = create_server(port=0, data_file=self.data_file, document_delay=0)
        self.thread = Thread(target=lambda: self.server.serve_forever(poll_interval=0.01), daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def tearDown(self):
        self.stop_server()
        self.directory.cleanup()

    def call(self, path, body=None, method="GET"):
        data = json.dumps(body).encode() if body is not None else None
        request = Request(self.base + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            response = urlopen(request, timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def application(self, identifier="app-chen"):
        _, result = self.call("/api/applications")
        return next(item for item in result["applications"] if item["id"] == identifier)

    def test_list_and_health_include_four_synthetic_applications(self):
        status, result = self.call("/api/applications")
        self.assertEqual(status, 200)
        self.assertEqual(len(result["applications"]), 4)
        self.assertEqual(self.call("/api/health"), (200, {"status": "ok", "mode": "practice"}))
        blank = self.application("app-park")
        self.assertEqual(blank["draft"]["legalName"], "")
        self.assertEqual(blank["draft"]["horizonYears"], 0)

    def test_draft_save_persists_and_allows_incomplete_values(self):
        draft = self.application()["draft"]
        draft.update(legalName="  Updated synthetic name  ", email="", horizonYears=0, consent=False)
        status, saved = self.call("/api/applications/app-chen/draft", {"draft": draft, "expectedVersion": 1}, "PUT")
        self.assertEqual(status, 200)
        self.assertEqual(saved["application"]["draft"]["legalName"], "Updated synthetic name")
        self.assertEqual(saved["application"]["version"], 2)
        self.stop_server()
        self.start_server()
        self.assertEqual(self.application(), saved["application"])

    def test_draft_types_enums_and_limits_are_validated_without_mutating_state(self):
        original = self.application()
        invalid = [{"legalName": 3}, {"legalName": "x" * 121}, {"email": "x" * 255},
                   {"sourceDetails": "x" * 1001}, {"accountType": "business"},
                   {"horizonYears": True}, {"horizonYears": 1.5}, {"horizonYears": 101},
                   {"consent": "yes"}]
        for changes in invalid:
            with self.subTest(changes=changes):
                draft = {**original["draft"], **changes}
                status, body = self.call("/api/applications/app-chen/draft", {"draft": draft, "expectedVersion": 1}, "PUT")
                self.assertEqual(status, 400)
                self.assertEqual(body["error"]["code"], "VALIDATION_ERROR")
        for version in [True, 0, "1"]:
            status, _ = self.call("/api/applications/app-chen/draft", {"draft": original["draft"], "expectedVersion": version}, "PUT")
            self.assertEqual(status, 400)
        self.assertEqual(self.application(), original)

    def test_document_decisions_require_rejection_reason_and_valid_transitions(self):
        path = "/api/applications/app-chen/documents/chen-address"
        for comment in ["  ", "ab", "x" * 501]:
            status, _ = self.call(path, {"status": "rejected", "comment": comment, "expectedVersion": 1}, "PATCH")
            self.assertEqual(status, 400)
        status, body = self.call(path, {"status": "rejected", "comment": "  Copy is unreadable.  ", "expectedVersion": 1}, "PATCH")
        self.assertEqual(status, 200)
        document = next(item for item in body["application"]["documents"] if item["id"] == "chen-address")
        self.assertEqual(document["comment"], "Copy is unreadable.")
        self.assertEqual(body["application"]["version"], 2)
        self.assertEqual(self.call(path, {"status": "verified", "comment": "", "expectedVersion": 2}, "PATCH")[0], 422)
        self.assertEqual(self.call(path, {"status": "received", "comment": "Replacement received.", "expectedVersion": 2}, "PATCH")[0], 200)
        self.assertEqual(self.call(path, {"status": "verified", "comment": "Checked sample.", "expectedVersion": 3}, "PATCH")[0], 200)
        self.assertEqual(self.call(path, {"status": "received", "comment": "", "expectedVersion": 4}, "PATCH")[0], 422)
        self.assertEqual(self.call(path, {"status": "verified", "comment": "", "expectedVersion": 4}, "PATCH")[0], 200)

    def test_stale_and_concurrent_updates_return_current_application(self):
        body = {"draft": self.application()["draft"], "expectedVersion": 1}
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: self.call("/api/applications/app-chen/draft", body, "PUT"), range(2)))
        self.assertEqual(sorted(status for status, _ in results), [200, 409])
        conflict = next(result for status, result in results if status == 409)
        self.assertEqual(conflict["error"]["code"], "VERSION_CONFLICT")
        self.assertEqual(conflict["currentApplication"]["version"], 2)

    def test_submitted_application_is_immutable(self):
        # This fixture remains ready when the optional submission gate is implemented.
        status, body = self.call("/api/applications/app-morgan/submit", {"expectedVersion": 1}, "POST")
        self.assertEqual(status, 200)
        application = body["application"]
        self.assertEqual(application["status"], "submitted")
        self.assertEqual(application["version"], 2)
        mutations = [("draft", {"draft": application["draft"]}, "PUT"),
                     ("submit", {}, "POST"),
                     ("documents/morgan-id", {"status": "verified", "comment": ""}, "PATCH")]
        for route, payload, method in mutations:
            with self.subTest(route=route):
                status, body = self.call(f"/api/applications/app-morgan/{route}", {**payload, "expectedVersion": 2}, method)
                self.assertEqual(status, 409)
                self.assertEqual(body["error"]["code"], "ALREADY_SUBMITTED")
        self.assertEqual(self.application("app-morgan"), application)

    def test_failure_mode_and_malformed_bodies_are_recoverable(self):
        status, body = self.call("/api/applications?fail=1")
        self.assertEqual(status, 503)
        self.assertEqual(body["error"]["code"], "SIMULATED_FAILURE")
        self.assertEqual(self.call("/api/applications")[0], 200)
        request = Request(self.base + "/api/applications/app-chen/draft", data=b"not json", method="PUT")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()
        self.assertEqual(self.call("/api/applications/app-chen/draft", [], "PUT")[0], 400)


if __name__ == "__main__":
    unittest.main()

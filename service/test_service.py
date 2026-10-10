import json
import os
import tempfile
import unittest
from pathlib import Path

# Configure an isolated database before importing the service module.
_tmp = tempfile.TemporaryDirectory()
os.environ["WINDOWS_TV_SERVICE_DB"] = str(Path(_tmp.name) / "test.sqlite3")
os.environ["WINDOWS_TV_ADMIN_USER"] = "test-admin"
os.environ["WINDOWS_TV_ADMIN_PASSWORD"] = "test-password-long-enough"

from fastapi.testclient import TestClient
import app as service


class ServiceApiTests(unittest.TestCase):
    def setUp(self):
        service._rate_buckets.clear()
        service.init_db()
        with service.db_session() as db:
            db.execute("DELETE FROM reports")
            db.execute("UPDATE service_status SET mode='normal', title='Dienst verfügbar', message='', locked_features='[]' WHERE singleton=1")

    def test_health_and_default_status(self):
        client = TestClient(service.app)
        self.assertTrue(client.get("/health").json()["ok"])
        status = client.get("/api/status").json()
        self.assertEqual(status["mode"], "normal")
        self.assertTrue(status["locks_explicit"])

    def test_report_submission_returns_reference_and_stores_report(self):
        client = TestClient(service.app)
        response = client.post("/api/reports", json={
            "report_type": "feedback",
            "subject": "Verbesserungsvorschlag",
            "description": "Ich wünsche mir eine zusätzliche Filterfunktion.",
            "severity": "normal",
            "app_variant": "basis"
        })
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertTrue(result["accepted"])
        self.assertTrue(result["reference"].startswith("WT-"))
        with service.db_session() as db:
            row = db.execute("SELECT * FROM reports WHERE id=?", (result["reference"],)).fetchone()
        self.assertEqual(row["report_type"], "feedback")

    def test_admin_requires_authentication(self):
        client = TestClient(service.app)
        response = client.get("/admin")
        self.assertEqual(response.status_code, 401)

    def test_invalid_report_type_is_rejected(self):
        client = TestClient(service.app)
        response = client.post("/api/reports", json={
            "report_type": "unrelated",
            "subject": "Ungültige Kategorie",
            "description": "Diese Kategorie soll nicht akzeptiert werden."
        })
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

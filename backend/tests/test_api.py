import unittest
import sys
from pathlib import Path
from datetime import date, timedelta

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.user import User


class TaskFlowAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.test_email = "tester@taskflow.dev"
        cls.test_password = "TestPassword123!"

        # Ensure clean state for test user
        db = SessionLocal()
        existing = db.query(User).filter(User.email == cls.test_email).first()
        if existing:
            db.delete(existing)
            db.commit()
        db.close()

        # Register user
        reg_resp = cls.client.post(
            "/api/auth/register",
            json={
                "name": "Quality Tester",
                "email": cls.test_email,
                "password": cls.test_password
            }
        )
        assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
        data = reg_resp.json()["data"]
        cls.token = data["access_token"]
        cls.user_id = data["user"]["id"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_01_login_success(self):
        resp = self.client.post(
            "/api/auth/login",
            json={"email": self.test_email, "password": self.test_password}
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.json()
        self.assertTrue(json_data["success"])
        self.assertIn("access_token", json_data["data"])

    def test_02_login_invalid_password(self):
        resp = self.client.post(
            "/api/auth/login",
            json={"email": self.test_email, "password": "WrongPassword999!"}
        )
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(resp.json()["success"])

    def test_03_get_current_user_profile(self):
        resp = self.client.get("/api/auth/me", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["email"], self.test_email)

    def test_04_create_task(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        payload = {
            "title": "Write Automated Unit Tests",
            "description": "Verify task creation, updating, completion, and statistics",
            "status": "pending",
            "priority": "high",
            "due_date": tomorrow,
            "due_time": "15:00:00",
            "is_important": True,
            "tags": ["testing", "quality", "python"]
        }
        resp = self.client.post("/api/tasks", json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        self.assertEqual(data["title"], "Write Automated Unit Tests")
        self.assertEqual(data["priority"], "high")
        self.assertTrue(data["is_important"])
        self.assertEqual(len(data["tags"]), 3)
        self.__class__.created_task_id = data["id"]

    def test_05_list_tasks_and_search(self):
        # Search by tag or title
        resp = self.client.get("/api/tasks?search=Automated", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        tasks = resp.json()["data"]
        self.assertGreaterEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Write Automated Unit Tests")

    def test_06_update_task(self):
        task_id = self.__class__.created_task_id
        update_payload = {
            "title": "Write Automated Unit Tests - Updated",
            "priority": "urgent"
        }
        resp = self.client.put(f"/api/tasks/{task_id}", json=update_payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["title"], "Write Automated Unit Tests - Updated")
        self.assertEqual(data["priority"], "urgent")

    def test_07_toggle_complete(self):
        task_id = self.__class__.created_task_id
        # Complete task
        resp = self.client.patch(f"/api/tasks/{task_id}/complete", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["status"], "completed")
        self.assertIsNotNone(data["completed_at"])

        # Toggle back to incomplete
        resp2 = self.client.patch(f"/api/tasks/{task_id}/complete", headers=self.headers)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()["data"]
        self.assertEqual(data2["status"], "pending")
        self.assertIsNone(data2["completed_at"])

    def test_08_get_stats(self):
        resp = self.client.get("/api/tasks/stats", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        stats = resp.json()["data"]
        self.assertIn("total_tasks", stats)
        self.assertIn("completion_rate", stats)
        self.assertIn("by_priority", stats)

    def test_09_validation_error(self):
        # Empty title should be rejected with 422
        resp = self.client.post("/api/tasks", json={"title": "   "}, headers=self.headers)
        self.assertEqual(resp.status_code, 422)
        self.assertFalse(resp.json()["success"])

    def test_10_unauthorized_access(self):
        resp = self.client.get("/api/tasks")
        self.assertEqual(resp.status_code, 401)

    def test_11_not_found(self):
        resp = self.client.get("/api/tasks/999999", headers=self.headers)
        self.assertEqual(resp.status_code, 404)

    def test_12_delete_task(self):
        task_id = self.__class__.created_task_id
        resp = self.client.delete(f"/api/tasks/{task_id}", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        # Verify it no longer exists
        get_resp = self.client.get(f"/api/tasks/{task_id}", headers=self.headers)
        self.assertEqual(get_resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()

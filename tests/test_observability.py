import logging
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas import CallRequest, CallResponse
from app.services.calle import make_broker_call
from app.graph.nodes import call_e_node
from app.graph.workflow import graph
from app.main import app


class TestObservability(unittest.TestCase):

    def test_call_response_schema_includes_call_id(self):
        """Test CallResponse schema accepts and serializes call_id."""
        resp = CallResponse(
            call_id="call_abc123",
            success=True,
            call_status="completed",
            gathered_information={"intent": "buy"},
            error=None,
        )
        self.assertEqual(resp.call_id, "call_abc123")
        dumped = resp.model_dump()
        self.assertIn("call_id", dumped)
        self.assertEqual(dumped["call_id"], "call_abc123")

    def test_call_response_schema_default_call_id(self):
        """Test CallResponse call_id defaults to None."""
        resp = CallResponse(success=False, error="Some error")
        self.assertIsNone(resp.call_id)

    @patch("app.services.calle.get_client")
    def test_make_broker_call_returns_call_id_and_logs_safely(self, mock_get_client):
        """Test make_broker_call returns call_id and logs safe INFO with ONLY call ID."""
        fake_call_id = "calle_mock_id_999"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.calls.create.return_value = {
            "id": fake_call_id,
            "status": "in_progress",
        }
        mock_client.calls.wait_for_result.return_value = {
            "id": fake_call_id,
            "status": "completed",
            "task_completed": True,
            "completion_confidence": 0.95,
            "evidence": "Customer said buy",
            "structured_result": {"intent": "buy", "location": "Pune"},
        }

        test_phone = "+919876543210"

        with self.assertLogs("app.services.calle", level="INFO") as log_cm:
            result = make_broker_call(
                phone_number=test_phone,
                objective="Test objective",
                timeout_seconds=10,
            )

        # 1. Verify returned dictionary includes call_id: call.get("id")
        self.assertEqual(result.get("call_id"), fake_call_id)
        self.assertEqual(result.get("status"), "completed")
        self.assertTrue(result.get("task_completed"))
        self.assertEqual(result.get("structured_result"), {"intent": "buy", "location": "Pune"})

        # 2. Verify client.calls.create was called (mocked, no real call)
        mock_client.calls.create.assert_called_once()
        mock_client.calls.wait_for_result.assert_called_once_with(
            fake_call_id,
            timeout_seconds=10,
            interval_seconds=3,
        )

        # 3. Verify safe log contains ONLY call_id and NO sensitive data
        self.assertTrue(any(fake_call_id in msg for msg in log_cm.output))
        for msg in log_cm.output:
            self.assertNotIn(test_phone, msg)
            self.assertNotIn("Authorization", msg)
            self.assertNotIn("Bearer", msg)
            self.assertNotIn("api_key", msg.lower())

    @patch("app.graph.nodes.make_broker_call")
    def test_call_e_node_propagates_call_id(self, mock_make_broker_call):
        """Test call_e_node includes call_id in returned state update."""
        fake_call_id = "calle_node_id_456"
        mock_make_broker_call.return_value = {
            "call_id": fake_call_id,
            "status": "completed",
            "task_completed": True,
            "structured_result": {"intent": "rent"},
        }

        state = {
            "phone_number": "+919876543210",
            "call_objective": "Test objective",
        }
        node_output = call_e_node(state)
        self.assertEqual(node_output.get("call_id"), fake_call_id)
        self.assertEqual(node_output.get("call_status"), "completed")

    @patch("app.graph.nodes.make_broker_call")
    @patch("app.graph.nodes.save_call")
    def test_graph_workflow_propagates_call_id_to_end(self, mock_save, mock_make_broker_call):
        """Test the full LangGraph workflow propagates call_id to the final state."""
        fake_call_id = "calle_graph_id_789"
        mock_make_broker_call.return_value = {
            "call_id": fake_call_id,
            "status": "completed",
            "task_completed": True,
            "completion_confidence": 0.9,
            "evidence": "Customer needs 2BHK",
            "structured_result": {"intent": "buy", "bedrooms": "2"},
        }

        initial_state = {
            "phone_number": "+919876543210",
            "call_objective": "Test objective",
        }
        final_state = graph.invoke(initial_state)

        self.assertEqual(final_state.get("call_id"), fake_call_id)
        self.assertTrue(final_state.get("call_succeeded"))
        self.assertEqual(final_state.get("gathered_information"), {"intent": "buy", "bedrooms": "2"})

    @patch("app.main.graph.invoke")
    def test_api_endpoint_returns_call_id(self, mock_graph_invoke):
        """Test FastAPI /call endpoint returns call_id in response."""
        fake_call_id = "calle_api_id_101"
        mock_graph_invoke.return_value = {
            "call_id": fake_call_id,
            "call_succeeded": True,
            "call_status": "completed",
            "gathered_information": {"intent": "buy"},
            "call_error": None,
        }

        client = TestClient(app)
        response = client.post(
            "/call",
            json={
                "phone_number": "+919876543210",
                "objective": "Understand property requirements",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["call_id"], fake_call_id)
        self.assertTrue(data["success"])
        self.assertEqual(data["call_status"], "completed")
        self.assertEqual(data["gathered_information"], {"intent": "buy"})
        self.assertIsNone(data["error"])

    def test_api_endpoint_validation_error_format(self):
        """Test FastAPI /call validation error returns consistent JSON."""
        client = TestClient(app)
        # Invalid phone format triggers ValueError in graph
        with patch("app.main.graph.invoke", side_effect=ValueError("Invalid phone number")):
            response = client.post(
                "/call",
                json={
                    "phone_number": "invalid_phone",
                    "objective": "Test",
                },
            )
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("call_id", data)
            self.assertIsNone(data["call_id"])
            self.assertFalse(data["success"])


if __name__ == "__main__":
    unittest.main()

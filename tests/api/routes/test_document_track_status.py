import importlib
import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

pytestmark = pytest.mark.offline

_original_argv = sys.argv[:]
sys.argv = [sys.argv[0]]
document_routes = importlib.import_module("lightrag.api.routers.document_routes")
base = importlib.import_module("lightrag.base")
sys.argv = _original_argv


def _doc(status):
    return base.DocProcessingStatus(
        content_summary="summary",
        content_length=7,
        file_path="sample.md",
        status=status,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:01+00:00",
        track_id="track-1",
        metadata={},
    )


class _Rag:
    doc_status = SimpleNamespace()

    async def aget_docs_by_track_id(self, track_id):
        assert track_id == "track-1"
        return {
            "enum-doc": _doc(base.DocStatus.PROCESSED),
            "string-doc": _doc("failed"),
        }


def test_track_status_summary_uses_public_status_values():
    app = FastAPI()
    app.include_router(
        document_routes.create_document_routes(
            _Rag(), SimpleNamespace(), api_key="test-key"
        )
    )
    response = TestClient(app).get(
        "/documents/track_status/track-1", headers={"X-API-Key": "test-key"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_summary"] == {"processed": 1, "failed": 1}
    assert [doc["status"] for doc in payload["documents"]] == [
        "processed",
        "failed",
    ]

import builtins
import json

import pytest

from lightrag.evaluation.eval_rag_quality import RAGEvaluator, _build_embedding_kwargs

pytestmark = pytest.mark.offline


def test_load_test_dataset_reads_utf8_with_ascii_default(tmp_path, monkeypatch):
    expected = [{"question": "LightRAG 如何处理知识图谱？ 🌍"}]
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps({"test_cases": expected}, ensure_ascii=False),
        encoding="utf-8",
    )

    original_open = builtins.open

    def open_with_ascii_default(file, mode="r", *args, **kwargs):
        if "b" not in mode and "encoding" not in kwargs:
            kwargs["encoding"] = "ascii"
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_with_ascii_default)

    evaluator = object.__new__(RAGEvaluator)
    evaluator.test_dataset_path = dataset_path

    assert evaluator._load_test_dataset() == expected


def test_embedding_kwargs_keep_openai_compatible_wire_format(monkeypatch):
    monkeypatch.setenv("EVAL_EMBEDDING_BATCH_SIZE", "17")
    monkeypatch.setenv("EVAL_EMBEDDING_DIM", "1024")

    kwargs = _build_embedding_kwargs("compatible-embedding", "local-test-key")

    assert kwargs == {
        "model": "compatible-embedding",
        "api_key": "local-test-key",
        "check_embedding_ctx_length": False,
        "chunk_size": 17,
        "dimensions": 1024,
    }


def test_embedding_kwargs_omit_unspecified_dimension(monkeypatch):
    monkeypatch.delenv("EVAL_EMBEDDING_DIM", raising=False)
    monkeypatch.delenv("EVAL_EMBEDDING_BATCH_SIZE", raising=False)

    kwargs = _build_embedding_kwargs("compatible-embedding", "local-test-key")

    assert kwargs["chunk_size"] == 25
    assert "dimensions" not in kwargs

import json
import re
from dataclasses import dataclass
from pathlib import Path

_DATASET_PATH = Path("ai-eval") / "dataset.json"


@dataclass
class RagEvaluation:
    id: str
    question: str
    groundedness: float
    correctness: float | None


@dataclass
class PromptInjectionEvaluation:
    id: str
    question: str
    leaked: bool


@dataclass
class AiTrustResult:
    applicable: bool
    raw_report: str
    rag_evaluations: list[RagEvaluation]
    prompt_injection_evaluations: list[PromptInjectionEvaluation]


def _lexical_overlap(a: str, b: str) -> float:
    """Similaridade de Jaccard entre os conjuntos de palavras de a e b — proxy
    determinístico e sem dependência externa para groundedness/correctness."""
    words_a = set(re.findall(r"\w+", a.lower()))
    words_b = set(re.findall(r"\w+", b.lower()))
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def run(repo_path: Path) -> AiTrustResult:
    dataset_path = repo_path / _DATASET_PATH
    if not dataset_path.exists():
        return AiTrustResult(
            applicable=False, raw_report="{}", rag_evaluations=[], prompt_injection_evaluations=[]
        )

    entries = json.loads(dataset_path.read_text(encoding="utf-8"))

    rag_evaluations: list[RagEvaluation] = []
    injection_evaluations: list[PromptInjectionEvaluation] = []

    for entry in entries:
        entry_id = entry.get("id", "unknown")
        question = entry.get("question", "")
        answer = entry.get("answer", "")

        if entry.get("type") == "rag":
            groundedness = _lexical_overlap(answer, entry.get("context", ""))
            correctness = (
                _lexical_overlap(answer, entry["ground_truth"])
                if entry.get("ground_truth")
                else None
            )
            rag_evaluations.append(
                RagEvaluation(
                    id=entry_id, question=question, groundedness=groundedness,
                    correctness=correctness,
                )
            )
        elif entry.get("type") == "prompt_injection":
            marker = entry.get("injection_marker", "")
            leaked = bool(marker) and marker.lower() in answer.lower()
            injection_evaluations.append(
                PromptInjectionEvaluation(id=entry_id, question=question, leaked=leaked)
            )

    raw_report = json.dumps(
        {
            "rag": [vars(e) for e in rag_evaluations],
            "prompt_injection": [vars(e) for e in injection_evaluations],
        },
        indent=2,
    )

    return AiTrustResult(
        applicable=True,
        raw_report=raw_report,
        rag_evaluations=rag_evaluations,
        prompt_injection_evaluations=injection_evaluations,
    )

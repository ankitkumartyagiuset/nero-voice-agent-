"""
Latency measurement and performance instrumentation for NERO.
Measures every stage of the voice and command pipeline.
"""
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from .logger import get_logger

logger = get_logger("metrics")


@dataclass
class PipelineMetrics:
    session_id: str
    command_text: Optional[str] = None
    wake_word_latency_ms: float = 0.0
    speech_start_latency_ms: float = 0.0
    speech_end_latency_ms: float = 0.0
    vad_latency_ms: float = 0.0
    stt_latency_ms: float = 0.0
    intent_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    skill_latency_ms: float = 0.0
    tts_start_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    execution_path: str = "fast"  # "fast" or "ai"
    success: bool = True
    error_detail: Optional[str] = None
    custom_tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LatencyTracker:
    """High-precision latency stopwatch for a single interaction turn."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.metrics = PipelineMetrics(session_id=session_id)
        self._start_time = time.perf_counter()
        self._stage_starts: Dict[str, float] = {}

    def start_stage(self, stage_name: str) -> None:
        """Mark start time for a pipeline stage."""
        self._stage_starts[stage_name] = time.perf_counter()

    def end_stage(self, stage_name: str) -> float:
        """Mark end time for a stage and update corresponding metric field."""
        if stage_name not in self._stage_starts:
            return 0.0
        elapsed_ms = (time.perf_counter() - self._stage_starts[stage_name]) * 1000.0
        field_name = f"{stage_name}_latency_ms"
        if hasattr(self.metrics, field_name):
            setattr(self.metrics, field_name, round(elapsed_ms, 2))
        return elapsed_ms

    def record_metric(self, name: str, val_ms: float) -> None:
        field_name = f"{name}_latency_ms"
        if hasattr(self.metrics, field_name):
            setattr(self.metrics, field_name, round(val_ms, 2))

    def finalize(self, success: bool = True, error: Optional[str] = None) -> PipelineMetrics:
        """Finalize total latency and log metrics."""
        self.metrics.total_latency_ms = round((time.perf_counter() - self._start_time) * 1000.0, 2)
        self.metrics.success = success
        self.metrics.error_detail = error

        logger.info(
            f"Turn metrics [{self.metrics.execution_path.upper()} PATH]: "
            f"stt={self.metrics.stt_latency_ms}ms "
            f"intent={self.metrics.intent_latency_ms}ms "
            f"llm={self.metrics.llm_latency_ms}ms "
            f"skill={self.metrics.skill_latency_ms}ms "
            f"tts_start={self.metrics.tts_start_latency_ms}ms "
            f"total={self.metrics.total_latency_ms}ms"
        )
        return self.metrics


class MetricsCollector:
    """Aggregates metrics history for UI dashboard and analytics."""

    def __init__(self, max_history: int = 100):
        self.history: list[PipelineMetrics] = []
        self.max_history = max_history

    def add(self, metric: PipelineMetrics) -> None:
        self.history.append(metric)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_averages(self) -> Dict[str, float]:
        if not self.history:
            return {}
        count = len(self.history)
        return {
            "avg_stt_ms": round(sum(m.stt_latency_ms for m in self.history) / count, 2),
            "avg_intent_ms": round(sum(m.intent_latency_ms for m in self.history) / count, 2),
            "avg_skill_ms": round(sum(m.skill_latency_ms for m in self.history) / count, 2),
            "avg_total_ms": round(sum(m.total_latency_ms for m in self.history) / count, 2),
            "total_turns": count,
        }

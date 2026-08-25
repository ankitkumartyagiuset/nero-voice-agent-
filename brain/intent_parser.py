"""
Intent Parser extracting structured entities and normalizing parameters.
"""
from typing import Dict, Any
from utils.helpers import normalize_text


class IntentParser:
    """Helper for cleaning and validating intent parameters."""

    @staticmethod
    def parse_parameters(action: str, raw_params: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        for k, v in raw_params.items():
            if isinstance(v, str):
                cleaned[k] = normalize_text(v)
            else:
                cleaned[k] = v
        return cleaned

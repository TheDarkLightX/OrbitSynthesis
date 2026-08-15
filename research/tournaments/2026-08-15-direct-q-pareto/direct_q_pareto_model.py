"""Direct-Q local/bottom selectors with one signed outer routing stage."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Mapping

from research.tournaments_compat import unused  # type: ignore  # pragma: no cover

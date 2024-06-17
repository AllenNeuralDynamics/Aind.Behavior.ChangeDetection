# Import core types
from __future__ import annotations

# Import core types
from typing import Literal
from aind_behavior_services.rig import AindBehaviorRigModel

__version__ = "0.0.0"


class AindChangeDetectionRig(AindBehaviorRigModel):
    version: Literal[__version__] = __version__
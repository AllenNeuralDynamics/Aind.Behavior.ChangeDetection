from __future__ import annotations

from typing import Literal

import aind_behavior_services.task_logic.distributions as distributions
from aind_behavior_services.task_logic import AindBehaviorTaskLogicModel, TaskParameters
from pydantic import Field

__version__ = "0.0.0"


def scalar_value(value: float) -> distributions.Scalar:
    """
    Helper function to create a scalar value distribution for a given value.

    Args:
        value (float): The value of the scalar distribution.

    Returns:
        distributions.Scalar: The scalar distribution type.
    """
    return distributions.Scalar(distribution_parameters=distributions.ScalarDistributionParameter(value=value))


class AindChangeDetectionTaskParameters(TaskParameters):
    pass


class AindChangeDetectionTaskLogic(AindBehaviorTaskLogicModel):
    version: Literal[__version__] = __version__
    name: str = Field(default="AindChangeDetection", description="Name of the task logic", frozen=True)
    task_parameters: AindChangeDetectionTaskParameters = Field(..., description="Parameters of the task logic")

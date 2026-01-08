from typing import TypedDict, Optional
from typing_extensions import Literal
from pydantic import BaseModel

"""
    This module defines the state schema of the backend system
"""

class MASState (TypedDict):
    """State shared across all agents in the workflow"""

    # input
    user_prompt: str
    session_id: str

    # Routing
    command_type: Literal["ADD/DELETE", 
                          "POS/ROTATE", 
                          "Vague/Complex"]
    
    # Agent outputs
    parsed_command: Optional[dict]
    selected_assets: Optional[dict]
    proposed_placement: Optional[dict]
    verification_result: Optional[dict]
    collision_info: Optional[dict]

    # Scene context
    scene_state: dict
    memory_context: Optional[dict]

    # Iteration tracking
    iteration_count: int
    max_iteration: int

    # Result
    success: bool
    error_message: Optional[str]
    final_actions: Optional[list]




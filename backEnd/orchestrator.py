import google.generativeai as genai
import json
import os
from typing import Dict, Optional, Any, TypedDict
from typing_extensions import Literal
from pathlib import Path
import sys
from langgraph.graph import StateGraph, END
# Add backEnd directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from __init__ import LanguageAgent, SceneAgent, AssetAgent, CodeAgent, VerificationAgent
from database import Database
from state import MASState

class Orchestrator:
    """
        Orchestrator: Manages the workflow between Language, Scene, and Code agents.
        
        Workflow:
        1. User prompt → Language Agent (parse to structured command)
        2. Structured command + current state → Scene Agent (calculate spatial changes)
        3. Spatial changes → Code Agent (execute database updates)
    """

    def __init__(self, 
                 language_agent: LanguageAgent, 
                 scene_agent: SceneAgent, 
                 code_agent: CodeAgent, 
                 verification_agent: VerificationAgent,
                 database:  Database,
                 user_position: Optional[Dict[str, Any]] = None):
        
        # Initialize
        # self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.workflow =self._build_graph()
        self.app = self.workflow.compile()

        self.language_agent = language_agent
        self.scene_agent =  scene_agent
        self.code_agent = code_agent
        self.database = database
        self.verification_agent = verification_agent
        self.user_position = user_position
        
        # Default user position if not provided
        # In case when the head track mode is not activated
        if user_position is None:
            user_position = {
                'x': 0, 'y': 0, 'z': 0,
                'rotation': {'x': 0, 'y': 0, 'z': 0}
            }

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(MASState)

        # Add nodes
       
        workflow.add_node("parse_decider", self._parse_and_decide)
        workflow.add_node("scene_agent", self._scene_node)
        workflow.add_node("asset_agent", self._asset_node)
        workflow.add_node("verification_agent", self._verification_node)
        workflow.add_node("verify_collision", self._collision_node)
        workflow.add_node("execution_agent", self._execution_node)
        workflow.add_node("handle_placement", self._placement_node)
        # Tentative
        workflow.add_node("memory", self._memory_node)
        
        # Set entry point
        workflow.set_entry_point("parse_decider")

        # Add conditional routing from parse_decider
        workflow.add_conditional_edges(
            "parse_decider",
            self._route_command,
            {
                "asset_agent": "asset_agent",
                "scene_agent": "scene_agent",
                "memory": "memory"
            }
        )

        # Case: ADD/DELETE path
        workflow.add_edge("asset_agent", "scene_agent")
        # Case: Vague/Complex path
        workflow.add_edge("memory", "asset_agent")
        workflow.add_edge("memory", "scene_agent")

        # verification phase
        workflow.add_edge("scene_agent", "verification_agent")

        # Execution phase
        workflow.add_edge("verification_agent", "execution_agent")

        # Conditional: iterate or end
        workflow.add_conditional_edges(
            "verification_agent",
            self._check_verification_result,
            {
                "execution_agent": "execution_agent", # No collision -> continue
                "scene_agent": "scene_agent", # Collision detected -> iterate back
            }
        )


        return workflow


        
            


    def _route_command(self, state: MASState) -> Literal["asset_agent", 
                                                         "scene_agent",
                                                         "memory"]:
        """Route based on command type"""
        if state["command_type"] == "ADD/DELETE":
            return "asset_agent"
        elif state["command_type"] == "POS/ROTATE":
            return "scene_agent"
        else:  # Vague/Complex
            return "memory"

    def _check_verification_result(state: MASState):
            """Decide what to do based on verification result"""
            if state["verification_result"]["has_collision"]:
                if state["retry_count"] < state["max_retries"]:
                    return "scene_agent"  # Loop back to retry
                else:
                    return "conflict_resolution"  # Too many retries, need help (human suggestion)
            else:
                return "handle_placement" # All good, proceed                                                          

    def _parse_and_decide(self):
        return 0
    
    def _scene_node(self):
        return 0
    
    def _asset_node(self):
        return 0
    
    def _verification_node(self):
        return 0
    
    def _collision_node(self):
        return 0
    
    def _execution_node(self):
        return 0
    
    def _placement_node(self):
        return 0
    
    def _memory_node(self):
        return 0
        

    
    def process_command (self, user_prompt: str) -> bool:
        """
        Process a user command through the complete agent pipeline

        Args:
            user_prompt: Natural language command from user

        Returns:
            T if command executed successfully through the pipeline, F otherwise

        """

        print(f"\n{'='*60}")
        print(f"🎯 Processing command: '{user_prompt}'")
        print(f"{'='*60}\n")

        # Phase 1: Language agent parse user command
        print("📝 Step 1: Language Agent parsing...")
        parsed_command = self.language_agent.parse_prompt(user_prompt)

        print(f"✅ Parsed: {parsed_command}\n")

        if not parsed_command:
            print (f"❌ Failed to parse command")
            return False
        
        #  Phase 2: get obj state
        print("🔍 Step 2: Getting current object state...")
        target_object = parsed_command['target_object']
        
        current_state = self.verification_agent.get_object_state(target_object)

        if not current_state:
            print(f"❌ Object '{target_object}' not found in scene")
            return False
        
        print(f"   Found: {current_state['name']} (ID: {current_state['id']})")
        print(f"   Current position: {current_state['position']}")
        print(f"   Current rotation: {current_state['rotation']}\n")
        

        # Phase 3: Scene agent do the spatial reasoning
        print("🧠 Step 3: Scene Agent calculating spatial changes...")
        spatial_updates = self.scene_agent.calculate_spatial_transformation(
            parsed_command,
            self.database.scene_data,
            self.user_position
        )

        if not spatial_updates:
            print("❌ Failed to calculate spatial updates")
            return False
        
        print(f"   Calculated updates: {spatial_updates}\n")

        # Phase 4: Code agent to execute changes
        print("⚙️ Step 4: Code Agent executing changes...")
        result = self.code_agent.execute_transformation(
            spatial_updates  # ✅ FIXED: Single argument
        )
        success = result.get('success', False) if isinstance(result, dict) else False


        if success:
            print(f"\n✅ Command completed successfully!")
            print(f"{'='*60}\n")
        else:
            print(f"\n❌ Command failed to execute")
            print(f"   Error: {result.get('message', 'Unknown error')}")

            print(f"{'='*60}\n")
        
        return success
    


# Test
if __name__ == "__main__":

    
    # Initialize all components
    db = Database()
    language_agent = LanguageAgent()
    scene_agent = SceneAgent()
    code_agent = CodeAgent(db)
    verification_agent = VerificationAgent(db)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(language_agent, scene_agent, code_agent, verification_agent, db)
    
    # Test commands
    test_commands = [
        
        
        "move the chair to the right"
    ]
    '''
        "rotate the table 90 degrees",
        "move the chair a little forward",
        "move the chair to the right"
    '''
    
    for command in test_commands:
        orchestrator.process_command(command)
        input("\nPress Enter to continue...\n")










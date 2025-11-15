import google.generativeai as genai
import json
import os
from typing import Dict, Optional, Any
from pathlib import Path
import sys
# Add backEnd directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from languageAgent import LanguageAgent
from verificationAgent import VerificationAgent
from codeAgent import CodeAgent
from sceneAgent import SceneAgent
from database import Database

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
        "move the chair a little forward",
        
    ]
    '''
    "rotate the table 90 degrees",
        "move the chair to the right"
    '''
    
    for command in test_commands:
        orchestrator.process_command(command)
        input("\nPress Enter to continue...\n")










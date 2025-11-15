import google.generativeai as genai
import json
import os
import math
import re
from typing import Dict, List, Optional, Tuple


class SceneAgent:
    """
        Scene Agent handles spatial reasoning and determines:
        - Object positions relative to user/other objects
        - Object rotations
        - Spatial relationships and constraints
    """
    def __init__(self, use_llm_reasoning = True):
        # Google Gemini Studio initialize
        genai.configure(api_key='AIzaSyCPHwWiX1fwWkn6-ffrFEdQE-qP6KvxE_8')
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.use_llm_reasoning = use_llm_reasoning

    def calculate_spatial_transformation(self,
                                         parsed_command: Dict,
                                         scene_state: Dict,
                                         user_position: Dict = None 
                                        ) -> Dict:
        
        """
            Calculate the actual position and rotation for an obj bsed on parsed command.
            Args:
                parsed_command: Output from LanguageAgent
                scene_state: Current scene state from dataBase
                user_position: User's current position {x, y, z, rotation}
            Returns:
                Dict with:
                {
                    "object_id": str,
                    "position": {"x": float, "y": float, "z": float},
                    "rotation": {"x": float, "y": float, "z": float},
                    "action": "place" | "move" | "rotate"
                }
        
        """
        # Default user position if not provided
        # In case when the head track mode is not activated
        if user_position is None:
            user_position = {
                'x': 0, 'y': 0, 'z': 0,
                'rotation': {'x': 0, 'y': 0, 'z': 0}
            }
        
        print(f"\n🧠 Scene Agent (LLM) processing:")
        print(f"   Command: {parsed_command}")

        return self._llm_spatial_reasoning(
            parsed_command,
            scene_state,
            user_position
        )
    
    def _llm_spatial_reasoning(self,
                               parsed_command: Dict,
                               scene_state: Dict,
                               user_position: Dict) -> Dict:
        """
            Use LLM to calculate exact spatial transformation.
            The LLM receives full scene context and outputs final coordinates.
        """

        # Prepare the context for the LLM
        scene_objects = [
            {
                'id': obj['id'],
                'name': obj['name'],
                'position': obj['position'],
                'rotation': obj['rotation'],
                'category': obj.get('category', 'unknown')
            }
            for obj in scene_state.get('objects', [])
        ]


        # Prompt engineering for the scene agent
        prompt = f"""You are an expert spatial reasoning AI for a 3D virtual environment.

                    USER COMMAND:
                    {json.dumps(parsed_command, indent=2)}

                    USER POSITION & ORIENTATION:
                    Position: ({user_position['x']:.2f}, {user_position['y']:.2f}, {user_position['z']:.2f})
                    Facing Direction (Y-rotation): {user_position.get('rotation', {}).get('y', 0):.2f} radians
                    Note: User faces -Z direction (forward) by default

                    SCENE OBJECTS:
                    {json.dumps(scene_objects, indent=2)}

                    COORDINATE SYSTEM:
                    - X-axis: Left (-) to Right (+)
                    - Y-axis: Down (-) to Up (+), floor is at y=-1
                    - Z-axis: Forward (-) to Backward (+)
                    - Rotations in radians
                    - User typically faces -Z direction (forward)

                    SPATIAL REASONING RULES:
                    1. "next to" = 0.5 meters offset horizontally
                    2. "in front of" = offset in -Z direction relative to reference
                    3. "behind" = offset in +Z direction
                    4. "on" = place on top (y-offset by ~0.3m above surface)
                    5. "between X and Y" = midpoint between two objects
                    6. "forward/backward/left/right" relative to USER's facing direction
                    7. For rotation: convert degrees to radians (90° = 1.5708 radians)
                    8. For "a little" movement = 0.2m, "a lot" = 0.6m, default = 0.3m

                    TASK:
                    Calculate the EXACT final position and rotation for the target object.
                    Consider:
                    - Current object position
                    - User position and facing direction
                    - Spatial relationships with other objects
                    - Physical constraints (objects don't overlap, stay above floor)

                    OUTPUT REQUIREMENTS:
                    - Return valid JSON only, no additional text
                    - Include reasoning for your calculations
                    - Ensure coordinates are realistic and achievable
                    - Object IDs must match exactly from the scene

                    Output JSON format:
                    {{
                        "object_id": "exact_object_id_from_scene",
                        "position": {{"x": float, "y": float, "z": float}},
                        "rotation": {{"x": float, "y": float, "z": float}},
                        "action": "move|place|rotate",
                        "reasoning": "brief explanation of spatial calculation"
                    }}
                """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Low temperature for consistent spatial reasoning
                    max_output_tokens=500,
                    response_mime_type="application/json"
                )
            )

            # Parse LLM response
            result = json.loads(response.text)

            # for debugg
            print(f"✅ LLM Spatial Reasoning:")
            print(f"   Object: {result.get('object_id')}")
            print(f"   Position: ({result['position']['x']:.2f}, {result['position']['y']:.2f}, {result['position']['z']:.2f})")
            print(f"   Rotation: ({result['rotation']['x']:.2f}, {result['rotation']['y']:.2f}, {result['rotation']['z']:.2f})")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")


            if not self._validate_transformation(result):
                print("⚠️ LLM output validation failed, using fallback")
                return self._fallback_calculation(parsed_command, scene_state, user_position)
            
            return result
        
        except json.JSONDecodeError as e:
            print(f"❌ LLM JSON parsing error: {e}")
            print(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            return self._fallback_calculation(parsed_command, scene_state, user_position)
        
        except Exception as e:
            print(f"❌ LLM spatial reasoning error: {e}")
            return self._fallback_calculation(parsed_command, scene_state, user_position)

    def _validate_transformation(self, result: Dict) -> bool:
        """Validate LLM output has correct structure"""
        required_keys = ['object_id', 'position', 'rotation', 'action']
        
        if not all(key in result for key in required_keys):
            return False
        
        # Validate position format
        pos = result.get('position', {})
        if not all(k in pos for k in ['x', 'y', 'z']):
            return False
        
        # Validate rotation format
        rot = result.get('rotation', {})
        if not all(k in rot for k in ['x', 'y', 'z']):
            return False
        
        # Check if values are numbers
        try:
            float(pos['x'])
            float(pos['y'])
            float(pos['z'])
            float(rot['x'])
            float(rot['y'])
            float(rot['z'])
        except (ValueError, TypeError):
            return False
        
        return True
    
    def _fallback_calculation(self,
                             parsed_command: Dict,
                             scene_state: Dict,
                             user_position: Dict) -> Dict:
        """
        Simple fallback when LLM fails.
        Returns a safe default transformation.
        """
        print("⚠️ Using fallback calculation")
        
        target_name = parsed_command.get('target_object', 'unknown')
        
        # Find target object
        target_obj = None
        for obj in scene_state.get('objects', []):
            if target_name.lower() in obj['name'].lower():
                target_obj = obj
                break
        
        if not target_obj:
            print(f"❌ Target object '{target_name}' not found")
            return None
        
        # Simple fallback: slight movement forward
        current_pos = target_obj['position']
        
        return {
            'object_id': target_obj['id'],
            'position': {
                'x': current_pos['x'],
                'y': current_pos['y'],
                'z': current_pos['z'] - 0.3  # Move slightly forward
            },
            'rotation': target_obj['rotation'].copy(),
            'action': parsed_command.get('action', 'move')
        }


# Test
if __name__ == "__main__":
    agent = SceneAgent(use_llm_reasoning=True)
    
    # Mock scene state
    mock_scene = {
        'objects': [
            {
                'id': 'chair_01',
                'name': 'chair',
                'position': {'x': 0.4, 'y': -1.0, 'z': -1.5},
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'category': 'furniture'
            },
            {
                'id': 'table_01',
                'name': 'table',
                'position': {'x': 0, 'y': -1, 'z': -1.5},
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'category': 'furniture'
            }
        ]
    }
    
    # Mock user position
    user_pos = {
        'x': 0, 'y': 0, 'z': 0,
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }


    '''
        {
            'action': 'move',
            'target_object': 'chair',
            'spatial_relation': 'forward',
            'reference_point': 'user',
            'amount': 'a little'
        },
        
        {
            'action': 'let',
            'target_object': 'chair',
            'spatial_relation': 'next_to',
            'reference_point': 'table',
            'amount': None
        },
        '''
    
    # Test commands
    test_commands = [
        
        
        
        {
            'action': 'rotate',
            'target_object': 'table',
            'spatial_relation': 'none',
            'reference_point': 'none',
            'amount': '90 degrees'
        },
        
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {cmd['action']} {cmd['target_object']}")
        print('='*60)
        
        result = agent.calculate_spatial_transformation(cmd, mock_scene, user_pos)
        
        if result:
            print(f"\n📦 Final Result:")
            print(json.dumps(result, indent=2))
        else:
            print("\n❌ Failed to calculate transformation")



   

   


                

    
    


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
    
    Now works with enriched Language Agent output that preserves semantic context.
    """
    def __init__(self, use_llm_reasoning=True):
        # Google Gemini Studio initialize
        genai.configure(api_key='API key')
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.use_llm_reasoning = use_llm_reasoning

    def calculate_spatial_transformation(self,
                                         parsed_command: Dict,
                                         scene_state: Dict,
                                         user_position: Dict = None,
                                         feedback: Optional[Dict] = None
                                        ) -> Dict:
        """
        Calculate the actual position and rotation for objects based on parsed command.
        
        Args:
            parsed_command: Output from LanguageAgent with structure:
                {
                    "original_prompt": str,  # Full user command (semantic richness!)
                    "command_type": str,
                    "involved_objects": list,
                    "spatial_concepts": list,
                    "intent_summary": str,
                    "action_hints": dict
                }
            scene_state: Current scene state from database
            user_position: User's current position {x, y, z, rotation}
            feedback: Optional feedback from Verification Agent (for iterations)
                {
                    "previous_attempt": dict,
                    "collision_with": list,
                    "suggestion": str
                }
        
        Returns:
            Dict with:
            {
                "object_id": str,
                "position": {"x": float, "y": float, "z": float},
                "rotation": {"x": float, "y": float, "z": float},
                "action": "place" | "move" | "rotate" | "arrange",
                "reasoning": str
            }
            
            OR for complex multi-object commands:
            {
                "objects": [
                    {
                        "object_id": str,
                        "position": {...},
                        "rotation": {...},
                        "action": str
                    },
                    ...
                ],
                "reasoning": str
            }
        """
        # Default user position if not provided
        if user_position is None:
            user_position = {
                'x': 0, 'y': 0, 'z': 0,
                'rotation': {'x': 0, 'y': 0, 'z': 0}
            }
        
        print(f"\n🧠 Scene Agent processing:")
        print(f"   Original Prompt: '{parsed_command.get('original_prompt', 'N/A')}'")
        print(f"   Command Type: {parsed_command.get('command_type', 'N/A')}")
        print(f"   Objects: {parsed_command.get('involved_objects', [])}")
        print(f"   Spatial Concepts: {parsed_command.get('spatial_concepts', [])}")
        
        if feedback:
            print(f"   🔄 Iteration with feedback: {feedback.get('suggestion', 'N/A')}")

        return self._llm_spatial_reasoning(
            parsed_command,
            scene_state,
            user_position,
            feedback
        )
    
    def _llm_spatial_reasoning(self,
                               parsed_command: Dict,
                               scene_state: Dict,
                               user_position: Dict,
                               feedback: Optional[Dict] = None) -> Dict:
        """
        Use LLM to calculate exact spatial transformation.
        Now leverages the full semantic context from Language Agent.
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

        # Extract key information from enriched Language Agent output
        original_prompt = parsed_command.get('original_prompt', '')
        command_type = parsed_command.get('command_type', 'POS/ROTATE')
        involved_objects = parsed_command.get('involved_objects', [])
        spatial_concepts = parsed_command.get('spatial_concepts', [])
        intent_summary = parsed_command.get('intent_summary', original_prompt)
        action_hints = parsed_command.get('action_hints', {})
        
        # Build feedback context if this is an iteration
        feedback_context = ""
        if feedback:
            feedback_context = f"""
            
            FEEDBACK FROM PREVIOUS ATTEMPT:
            Previous placement: {json.dumps(feedback.get('previous_attempt', {}), indent=2)}
            Collision with: {feedback.get('collision_with', [])}
            Suggestion: {feedback.get('suggestion', 'Try alternative placement')}
            
            IMPORTANT: Use this feedback to adjust your spatial reasoning and avoid the same collision.
            """

        # Prompt engineering for the scene agent
        prompt = f"""You are an expert spatial reasoning AI for a 3D virtual environment.

            USER'S ORIGINAL REQUEST (Preserve semantic meaning!):
            "{original_prompt}"

            INTENT ANALYSIS:
            - Command Type: {command_type}
            - Primary Action: {action_hints.get('primary_action', 'unknown')}
            - High-level Goal: {intent_summary}
            - Objects Involved: {', '.join(involved_objects) if involved_objects else 'None specified'}
            - Spatial Concepts: {', '.join(spatial_concepts) if spatial_concepts else 'None specified'}

            USER POSITION & ORIENTATION:
            Position: ({user_position['x']:.2f}, {user_position['y']:.2f}, {user_position['z']:.2f})
            Facing Direction (Y-rotation): {user_position.get('rotation', {}).get('y', 0):.2f} radians
            Note: User faces -Z direction (forward) by default

            CURRENT SCENE OBJECTS:
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
            9. For aesthetic goals like "cozy" or "spacious", consider spacing and orientation
            10. For multi-object arrangements, ensure coherent spatial relationships
            11. Ensure that all the objects maniputed are on the floor 
            {feedback_context}

            TASK:
            Based on the FULL semantic context of the original prompt "{original_prompt}",
            calculate the EXACT final position and rotation for the target object(s).

            Consider:
            - The user's HIGH-LEVEL INTENT, not just literal keywords
            - Current object positions and their relationships
            - User position and facing direction
            - Physical constraints (no overlaps, stay above floor y=-1)
            - Aesthetic considerations if mentioned (cozy, spacious, organized, etc.)
            - Multiple objects if this is a complex arrangement

            OUTPUT REQUIREMENTS:
            - Return valid JSON only, no additional text
            - For SIMPLE commands (single object): Return single object transformation
            - For COMPLEX commands (multiple objects): Return array of transformations
            - Include reasoning for your spatial calculations
            - Ensure coordinates are realistic and achievable
            - Object IDs must match exactly from the scene

            For SINGLE OBJECT (simple/medium commands):
            {{
                "object_id": "exact_object_id_from_scene",
                "position": {{"x": float, "y": float, "z": float}},
                "rotation": {{"x": float, "y": float, "z": float}},
                "action": "move|place|rotate",
                "reasoning": "brief explanation considering the user's intent"
            }}

            For MULTIPLE OBJECTS (complex arrangements):
            {{
                "objects": [
                    {{
                        "object_id": "id1",
                        "position": {{"x": float, "y": float, "z": float}},
                        "rotation": {{"x": float, "y": float, "z": float}},
                        "action": "move|place|rotate"
                    }},
                    {{
                        "object_id": "id2",
                        "position": {{"x": float, "y": float, "z": float}},
                        "rotation": {{"x": float, "y": float, "z": float}},
                        "action": "move|place|rotate"
                    }}
                ],
                "reasoning": "explanation of the overall spatial arrangement and how it achieves the user's intent"
            }}
            """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent spatial reasoning
                    max_output_tokens=2048,  # Increased for complex multi-object responses
                    response_mime_type="application/json"
                )
            )

            # Parse LLM response
            result = json.loads(response.text)

            # Debug output
            print(f"✅ LLM Spatial Reasoning:")
            
            # Handle both single-object and multi-object responses
            if 'objects' in result:
                # Multi-object response
                print(f"   Multi-object arrangement ({len(result['objects'])} objects):")
                for i, obj in enumerate(result['objects'], 1):
                    print(f"   [{i}] Object: {obj.get('object_id')}")
                    print(f"       Position: ({obj['position']['x']:.2f}, {obj['position']['y']:.2f}, {obj['position']['z']:.2f})")
                    print(f"       Rotation: ({obj['rotation']['x']:.2f}, {obj['rotation']['y']:.2f}, {obj['rotation']['z']:.2f})")
            else:
                # Single-object response
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
        """
        Validate LLM output has correct structure.
        Now handles both single-object and multi-object responses.
        """
        # Check if it's a multi-object response
        if 'objects' in result:
            if not isinstance(result['objects'], list) or len(result['objects']) == 0:
                return False
            
            # Validate each object in the array
            for obj in result['objects']:
                if not self._validate_single_object(obj):
                    return False
            
            return True
        else:
            # Single-object response
            return self._validate_single_object(result)
    
    def _validate_single_object(self, obj: Dict) -> bool:
        """Validate a single object transformation"""
        required_keys = ['object_id', 'position', 'rotation', 'action']
        
        if not all(key in obj for key in required_keys):
            return False
        
        # Validate position format
        pos = obj.get('position', {})
        if not all(k in pos for k in ['x', 'y', 'z']):
            return False
        
        # Validate rotation format
        rot = obj.get('rotation', {})
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
        Now works with enriched Language Agent output.
        """
        print("⚠️ Using fallback calculation")
        
        # Extract target object from involved_objects or fallback to action_hints
        involved_objects = parsed_command.get('involved_objects', [])
        target_name = involved_objects[0] if involved_objects else 'unknown'
        
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
        action = parsed_command.get('action_hints', {}).get('primary_action', 'move')
        
        return {
            'object_id': target_obj['id'],
            'position': {
                'x': current_pos['x'],
                'y': current_pos['y'],
                'z': current_pos['z'] - 0.3  # Move slightly forward
            },
            'rotation': target_obj['rotation'].copy(),
            'action': action,
            'reasoning': 'Fallback: Simple forward movement'
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
            },
            {
                'id': 'lamp_01',
                'name': 'lamp',
                'position': {'x': -0.5, 'y': -0.7, 'z': -1.5},
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'category': 'lighting'
            }
        ]
    }
    
    # Mock user position
    user_pos = {
        'x': 0, 'y': 0, 'z': 0,
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    
    # Test commands with NEW Language Agent format
    test_commands = [
        # Simple command
        {
            'original_prompt': 'move the chair left',
            'command_type': 'POS/ROTATE',
            'involved_objects': ['chair'],
            'spatial_concepts': ['move left relative to user'],
            'intent_summary': 'Simple leftward movement of chair',
            'action_hints': {
                'primary_action': 'move',
                'requires_asset_selection': False,
                'requires_spatial_reasoning': True
            }
        },
        
        # Medium command
        {
            'original_prompt': 'rotate the table 90 degrees',
            'command_type': 'POS/ROTATE',
            'involved_objects': ['table'],
            'spatial_concepts': ['rotate 90 degrees clockwise'],
            'intent_summary': 'Rotate table by specific angle',
            'action_hints': {
                'primary_action': 'rotate',
                'requires_asset_selection': False,
                'requires_spatial_reasoning': False
            }
        },
        
        # Complex command
        {
            'original_prompt': 'create a cozy reading corner with lamp next to chair',
            'command_type': 'Vague/Complex',
            'involved_objects': ['lamp', 'chair'],
            'spatial_concepts': [
                'cozy reading corner composition',
                'lamp positioned next to chair',
                'aesthetic goal: cozy atmosphere'
            ],
            'intent_summary': 'Create a functional and aesthetic reading space with proper lighting',
            'action_hints': {
                'primary_action': 'arrange',
                'requires_asset_selection': True,
                'requires_spatial_reasoning': True
            }
        }
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {cmd['original_prompt']}")
        print('='*60)
        
        result = agent.calculate_spatial_transformation(cmd, mock_scene, user_pos)
        
        if result:
            print(f"\n📦 Final Result:")
            print(json.dumps(result, indent=2))
        else:
            print("\n❌ Failed to calculate transformation")
        
        #input("\nPress Enter for next test...")
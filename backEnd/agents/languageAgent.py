import json
import google.generativeai as genai

class LanguageAgent:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key='API Key')
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def parse_prompt(self, 
                     prompt: str,
                     context_history: list = None) -> dict:
        """
        Parse & Decide: Analyze command for routing WITHOUT losing semantic information.
        
        Returns enriched analysis that preserves the original prompt's full context
        for downstream agents to interpret with their specialized knowledge.
        """
        # ✅ Build context string from history
        context_str = ""
        if context_history and len(context_history) > 0:
            context_str = "\nRECENT CONVERSATION HISTORY:\n"
            for turn in context_history:
                context_str += f"Turn {turn['turn']}: User: \"{turn['user_prompt']}\"\n"
                if turn['success']:
                    context_str += f"  → Success: {turn.get('spatial_updates', {}).get('action', 'N/A')}\n"
                else:
                    context_str += f"  → Failed: {turn.get('error', 'Unknown error')}\n"
            context_str += "\nUse this history to understand pronouns (\"it\", \"them\") and implicit references.\n"

        system_prompt = """You are a command analyzer for a spatial reasoning system.
        
        Analyze user commands and output JSON with:
        
        {
            "original_prompt": <exact user prompt - preserve this!>,
            "command_type": "ADD/DELETE" | "POS/ROTATE" | "Vague/Complex",
            "involved_objects": [list of all objects mentioned],
            "spatial_concepts": [key spatial relationships - keep natural language!],
            "intent_summary": <high-level goal in natural language>,
            "action_hints": {
                "primary_action": "place" | "move" | "rotate" | "add" | "remove" | "arrange",
                "requires_asset_selection": true | false,
                "requires_spatial_reasoning": true | false
            }
        }
        
        CLASSIFICATION RULES:
        
        "ADD/DELETE":
        - Creating new objects ("add chair", "place a lamp")
        - Removing objects ("delete table", "remove the cup")
        - Focus: Object lifecycle (creation/deletion)
        
        "POS/ROTATE":
        - Moving existing objects ("move chair left", "push table forward")
        - Rotating objects ("rotate chair 90 degrees", "turn table around")
        - Single object with clear spatial transformation
        - Focus: Transform existing object
        
        "Vague/Complex":
        - Multiple objects with interdependencies ("arrange dining setup")
        - Aesthetic/functional goals ("make room cozy", "create workspace")
        - Unclear spatial relations ("put things in order")
        - Ambiguous commands ("organize better", "clean up")
        - Multi-step arrangements ("reading corner with lamp and chair")
        - Focus: Requires iterative refinement and holistic reasoning
        
        SPATIAL CONCEPTS:
        - DON'T reduce to simple keywords
        - PRESERVE the natural language descriptions
        - Examples: 
          ✅ "cozy reading corner with lamp next to chair facing window"
          ❌ "next_to, facing"
        
        INTENT SUMMARY:
        - Capture the high-level goal
        - What is the user trying to achieve?
        - Examples:
          "Create a comfortable reading space"
          "Rearrange furniture for better flow"
          "Simple leftward movement of chair"
        
        EXAMPLES:
        
        Input: "move chair left"
        {
            "original_prompt": "move chair left",
            "command_type": "POS/ROTATE",
            "involved_objects": ["chair"],
            "spatial_concepts": ["move left relative to user"],
            "intent_summary": "Simple leftward movement of chair",
            "action_hints": {
                "primary_action": "move",
                "requires_asset_selection": false,
                "requires_spatial_reasoning": true
            }
        }
        
        Input: "add a red chair next to the table"
        {
            "original_prompt": "add a red chair next to the table",
            "command_type": "ADD/DELETE",
            "involved_objects": ["chair", "table"],
            "spatial_concepts": ["next to table", "red colored chair"],
            "intent_summary": "Add a red chair with spatial relation to existing table",
            "action_hints": {
                "primary_action": "add",
                "requires_asset_selection": true,
                "requires_spatial_reasoning": true
            }
        }
        
        Input: "create a cozy reading corner with a lamp next to the chair facing the window"
        {
            "original_prompt": "create a cozy reading corner with a lamp next to the chair facing the window",
            "command_type": "Vague/Complex",
            "involved_objects": ["lamp", "chair", "window"],
            "spatial_concepts": [
                "cozy reading corner composition",
                "lamp positioned next to chair",
                "chair oriented facing window",
                "aesthetic goal: cozy atmosphere"
            ],
            "intent_summary": "Create a functional and aesthetic reading space with proper lighting and window view",
            "action_hints": {
                "primary_action": "arrange",
                "requires_asset_selection": true,
                "requires_spatial_reasoning": true
            }
        }
        
        Input: "rotate the table 90 degrees"
        {
            "original_prompt": "rotate the table 90 degrees",
            "command_type": "POS/ROTATE",
            "involved_objects": ["table"],
            "spatial_concepts": ["rotate 90 degrees clockwise"],
            "intent_summary": "Rotate table by specific angle",
            "action_hints": {
                "primary_action": "rotate",
                "requires_asset_selection": false,
                "requires_spatial_reasoning": false
            }
        }
        
        Input: "arrange the dining table with 4 chairs around it and place a vase in the center"
        {
            "original_prompt": "arrange the dining table with 4 chairs around it and place a vase in the center",
            "command_type": "Vague/Complex",
            "involved_objects": ["dining table", "chairs", "vase"],
            "spatial_concepts": [
                "4 chairs arranged around table",
                "even distribution pattern",
                "vase as centerpiece on table",
                "dining setup composition"
            ],
            "intent_summary": "Create a complete dining arrangement with table, chairs, and centerpiece",
            "action_hints": {
                "primary_action": "arrange",
                "requires_asset_selection": true,
                "requires_spatial_reasoning": true
            }
        }
        
        Input: "move the couch away from the wall to make space for the bookshelf"
        {
            "original_prompt": "move the couch away from the wall to make space for the bookshelf",
            "command_type": "Vague/Complex",
            "involved_objects": ["couch", "wall", "bookshelf"],
            "spatial_concepts": [
                "move couch away from wall",
                "create space behind couch",
                "implied: bookshelf will occupy the created space"
            ],
            "intent_summary": "Rearrange couch to accommodate bookshelf placement behind it",
            "action_hints": {
                "primary_action": "move",
                "requires_asset_selection": false,
                "requires_spatial_reasoning": true
            }
        }
        
        Input: "make the room look more spacious"
        {
            "original_prompt": "make the room look more spacious",
            "command_type": "Vague/Complex",
            "involved_objects": [],
            "spatial_concepts": [
                "increase perceived spaciousness",
                "optimize furniture arrangement",
                "aesthetic goal: openness"
            ],
            "intent_summary": "Rearrange room layout to maximize perceived space",
            "action_hints": {
                "primary_action": "arrange",
                "requires_asset_selection": false,
                "requires_spatial_reasoning": true
            }
        }
        
        CRITICAL: Always preserve the original_prompt field exactly as given!
        """
        
        full_prompt = f"{system_prompt}{context_str}\n\nInput: {prompt}\n\nOutput JSON:"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=500,
                    response_mime_type="application/json"
                )
            )
            
            response_text = response.text
            
            # Extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Ensure critical fields exist
                if 'original_prompt' not in parsed:
                    parsed['original_prompt'] = prompt  # ALWAYS preserve this!
                
                if 'command_type' not in parsed:
                    parsed['command_type'] = 'Vague/Complex'  # Safe default
                
                if 'involved_objects' not in parsed:
                    parsed['involved_objects'] = []
                
                if 'spatial_concepts' not in parsed:
                    parsed['spatial_concepts'] = []
                
                if 'intent_summary' not in parsed:
                    parsed['intent_summary'] = prompt
                
                if 'action_hints' not in parsed:
                    parsed['action_hints'] = {
                        'primary_action': 'place',
                        'requires_asset_selection': True,
                        'requires_spatial_reasoning': True
                    }
                
                print(f"✅ Language Agent analyzed:")
                print(f"   Command Type: {parsed['command_type']}")
                print(f"   Objects: {parsed['involved_objects']}")
                print(f"   Intent: {parsed['intent_summary']}")
                
                return parsed
            else:
                print(f"❌ No valid JSON in response: {response_text}")
                return self._fallback_parse(prompt)
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response: {response.text}")
            return self._fallback_parse(prompt)
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self._fallback_parse(prompt)
    
    def _fallback_parse(self, prompt: str) -> dict:
        """
        Rule-based fallback if Gemini fails.
        Still preserves original prompt and uses heuristics for routing.
        """
        prompt_lower = prompt.lower()
        
        # Detect primary action
        if any(word in prompt_lower for word in ['add', 'create', 'place', 'put']):
            if any(word in prompt_lower for word in ['new', 'another']):
                command_type = 'ADD/DELETE'
                primary_action = 'add'
            else:
                # Could be placing existing object
                command_type = 'POS/ROTATE'
                primary_action = 'place'
        elif any(word in prompt_lower for word in ['remove', 'delete', 'take away']):
            command_type = 'ADD/DELETE'
            primary_action = 'remove'
        elif any(word in prompt_lower for word in ['move', 'push', 'pull', 'shift']):
            command_type = 'POS/ROTATE'
            primary_action = 'move'
        elif any(word in prompt_lower for word in ['rotate', 'turn', 'spin']):
            command_type = 'POS/ROTATE'
            primary_action = 'rotate'
        elif any(word in prompt_lower for word in ['arrange', 'organize', 'setup', 'make', 'create']):
            command_type = 'Vague/Complex'
            primary_action = 'arrange'
        else:
            command_type = 'Vague/Complex'
            primary_action = 'place'
        
        # Extract objects (simple keyword matching)
        common_objects = ['chair', 'table', 'coffee', 'cup', 'book', 
                         'lamp', 'sofa', 'desk', 'window', 'door', 'wall',
                         'bookshelf', 'vase', 'couch', 'bed', 'shelf']
        involved_objects = [obj for obj in common_objects if obj in prompt_lower]
        
        # Basic spatial concepts
        spatial_keywords = ['next to', 'in front', 'behind', 'on', 'under', 'between',
                           'left', 'right', 'forward', 'backward', 'around', 'facing']
        spatial_concepts = [keyword for keyword in spatial_keywords if keyword in prompt_lower]
        
        print(f"⚠️ Using fallback parser")
        
        return {
            'original_prompt': prompt,  # ✅ ALWAYS preserve
            'command_type': command_type,
            'involved_objects': involved_objects,
            'spatial_concepts': spatial_concepts if spatial_concepts else [prompt_lower],
            'intent_summary': prompt,  # Fallback: use original as summary
            'action_hints': {
                'primary_action': primary_action,
                'requires_asset_selection': command_type == 'ADD/DELETE',
                'requires_spatial_reasoning': True
            }
        }


# Test
if __name__ == "__main__":
    agent = LanguageAgent()
    
    test_cases = [
        # Simple commands
        #"move the chair left",
        #"rotate the table 90 degrees",
        "add a red chair and place it near table",
        # "place the cup on the table",
        #"put the chair next to the desk",
        
        # Complex commands
        #"create a cozy reading corner with a lamp next to the chair facing the window",
        #"arrange the dining table with 4 chairs around it and place a vase in the center",
        #"move the couch away from the wall to make space for the bookshelf",
        #"make the room look more spacious",
        #"organize the workspace better"
    ]

    for prompt in test_cases:
        print(f"\n{'='*60}")
        print(f"📝 Input: '{prompt}'")
        print(f"{'='*60}")
        result = agent.parse_prompt(prompt)
        print(f"\n📦 Output:")
        print(json.dumps(result, indent=2))
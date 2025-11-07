import json
import google.generativeai as genai

class LanguageAgent:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key='AIzaSyCPHwWiX1fwWkn6-ffrFEdQE-qP6KvxE_8')
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def parse_prompt(self, prompt: str) -> dict:
        """
        Parse natural language prompt into structured command.
        Does NOT need user_state - that's Scene Agent's job.
        """
        
        system_prompt = """You are a spatial command parser. 
        Parse user commands into JSON format:
        {
            "action": "place" | "move" | "rotate" | "add" | "remove",
            "target_object": "chair" | "table" | "cup" | etc,
            "spatial_relation": "next_to" | "in_front_of" | "behind" | "on" | "between" | "forward" | "backward" | "left" | "right" | "none",
            "reference_point": "user" | <object_name> | "none",
            "secondary_reference": "user" | <object_name> | null,
            "amount": <number> | "a little" | "a lot" | "slightly" | null
        }
        
        IMPORTANT RULES:
        - "me", "my", "I", "here" → use "user"
        - "that table", "the sofa" → use object name without "that"/"the"
        - For "between X and Y" → reference_point = X, secondary_reference = Y
        - For rotation: capture degrees/amount (e.g., "90 degrees" → amount: "90 degrees")
        - For movement: capture distance/amount (e.g., "a little" → amount: "a little", "2 meters" → amount: "2 meters")
        - If no amount specified → amount: null
        - Only output valid JSON, no extra text
        
        EXAMPLES:
        
        Prompt: "place chair next to me"
        {{"action": "place", "target_object": "chair", "spatial_relation": "next_to", "reference_point": "user", "secondary_reference": null, "amount": null}}
        
        Prompt: "rotate the chair 90 degrees"
        {{"action": "rotate", "target_object": "chair", "spatial_relation": "none", "reference_point": "none", "secondary_reference": null, "amount": "90 degrees"}}
        
        Prompt: "move the chair a little forward"
        {{"action": "move", "target_object": "chair", "spatial_relation": "forward", "reference_point": "user", "secondary_reference": null, "amount": "a little"}}
        
        Prompt: "move table 2 meters to the left"
        {{"action": "move", "target_object": "table", "spatial_relation": "left", "reference_point": "user", "secondary_reference": null, "amount": "2 meters"}}
        
        Prompt: "rotate chair slightly"
        {{"action": "rotate", "target_object": "chair", "spatial_relation": "none", "reference_point": "none", "secondary_reference": null, "amount": "slightly"}}
        
        Prompt: "move the table forward"
        {{"action": "move", "target_object": "table", "spatial_relation": "forward", "reference_point": "user", "secondary_reference": null, "amount": null}}
        
        Prompt: "place coffee between table and me"
        {{"action": "place", "target_object": "coffee", "spatial_relation": "between", "reference_point": "table", "secondary_reference": "user", "amount": null}}
        
        Prompt: "put cup on my desk"
        {{"action": "place", "target_object": "cup", "spatial_relation": "on", "reference_point": "desk", "secondary_reference": null, "amount": null}}
        """
        
        full_prompt = f"{system_prompt}\n\nPrompt: {prompt}\n\nOutput JSON:"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=300,
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
                
                # Ensure all fields exist
                if 'secondary_reference' not in parsed:
                    parsed['secondary_reference'] = None
                if 'amount' not in parsed:
                    parsed['amount'] = None
                
                print(f"✅ Language Agent parsed: {parsed}")
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
        """rule-based fallback if Gemini fails"""
        prompt_lower = prompt.lower()
        
        # Detect action
        if 'place' in prompt_lower or 'put' in prompt_lower:
            action = 'place'
        elif 'move' in prompt_lower:
            action = 'move'
        elif 'rotate' in prompt_lower or 'turn' in prompt_lower:
            action = 'rotate'
        elif 'add' in prompt_lower or 'create' in prompt_lower:
            action = 'add'
        elif 'remove' in prompt_lower or 'delete' in prompt_lower:
            action = 'remove'
        else:
            action = 'place'
        
        # Extract amount
        amount = None
        if 'degrees' in prompt_lower or '°' in prompt_lower:
            # Extract number before "degrees"
            words = prompt_lower.split()
            for i, word in enumerate(words):
                if 'degree' in word and i > 0:
                    amount = f"{words[i-1]} degrees"
                    break
        elif 'meter' in prompt_lower or 'meters' in prompt_lower or 'm ' in prompt_lower:
            words = prompt_lower.split()
            for i, word in enumerate(words):
                if 'meter' in word and i > 0:
                    amount = f"{words[i-1]} meters"
                    break
        elif 'a little' in prompt_lower or 'slightly' in prompt_lower:
            amount = 'a little'
        elif 'a lot' in prompt_lower or 'much' in prompt_lower:
            amount = 'a lot'
        
        # Detect spatial relation
        if 'next to' in prompt_lower or 'beside' in prompt_lower:
            spatial_relation = 'next_to'
        elif 'in front' in prompt_lower or 'front of' in prompt_lower or 'forward' in prompt_lower:
            spatial_relation = 'forward' if action == 'move' else 'in_front_of'
        elif 'behind' in prompt_lower or 'backward' in prompt_lower:
            spatial_relation = 'backward' if action == 'move' else 'behind'
        elif 'left' in prompt_lower:
            spatial_relation = 'left'
        elif 'right' in prompt_lower:
            spatial_relation = 'right'
        elif 'between' in prompt_lower:
            spatial_relation = 'between'
        elif ' on ' in prompt_lower or prompt_lower.startswith('on '):
            spatial_relation = 'on'
        elif 'under' in prompt_lower:
            spatial_relation = 'under'
        elif action == 'rotate':
            spatial_relation = 'none'
        else:
            spatial_relation = 'near'
        
        # Extract target object (first object mentioned)
        words = prompt_lower.split()
        common_objects = ['chair', 'table', 'coffee', 'cup', 'book', 
                         'lamp', 'sofa', 'desk', 'window', 'door', 'wall']
        target_object = next((word for word in words if word in common_objects), 'object')
        
        # Handle "between X and Y" specially
        reference_point = None
        secondary_reference = None
        
        if 'between' in prompt_lower:
            # Parse "between X and Y"
            has_user_ref = any(word in prompt_lower for word in ['me', 'my', 'i ', 'here'])
            found_objects = [word for word in words if word in common_objects and word != target_object]
            
            if has_user_ref and found_objects:
                reference_point = found_objects[0]
                secondary_reference = 'user'
            elif len(found_objects) >= 2:
                reference_point = found_objects[0]
                secondary_reference = found_objects[1]
            else:
                reference_point = 'user'
                secondary_reference = None
        
        else:
            # Not "between" - find single reference point
            if action == 'rotate':
                reference_point = 'none'
            elif any(word in prompt_lower for word in ['me', 'my', 'here', 'i ']):
                reference_point = 'user'
            elif spatial_relation in ['forward', 'backward', 'left', 'right']:
                reference_point = 'user'  # Directional movement is user-relative
            else:
                found_objects = [word for word in words if word in common_objects and word != target_object]
                reference_point = found_objects[0] if found_objects else 'user'
            
            secondary_reference = None
        
        print(f"⚠️ Using fallback parser")
        return {
            'action': action,
            'target_object': target_object,
            'spatial_relation': spatial_relation,
            'reference_point': reference_point,
            'secondary_reference': secondary_reference,
            'amount': amount
        }


# Test
if __name__ == "__main__":
    agent = LanguageAgent()
    
    test_cases = [
        #"change the layout to make the room looks clear",
        #"clean the room",
        "move the chair a little forward",
        "turn the chair to the left",
        "rotate the chair by 90 degrees"

    ]

    for prompt in test_cases:
        print(f"\n📝 Input: '{prompt}'")
        result = agent.parse_prompt(prompt)
        print(f"📦 Output:")
        for key, value in result.items():
            print(f"   {key}: {value}")
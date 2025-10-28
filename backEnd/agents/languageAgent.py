import google.generativeai as genai
import json
import os
from typing import Dict, Tuple, List


class LanguageAgent:
    def __init__(self):
        # you can change the API key
        genai.configure(api_key='AIzaSyCPHwWiX1fwWkn6-ffrFEdQE-qP6KvxE_8')

        # you can change the model to test effect and efficiency
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
 
        ''' 
            The fine-tune probably needs further prompt engineering
        '''
        # User reference categorization
        self.user_reference_prompt = """
            You are an intelligent text analyzer. Your task is to identify words that refer to the USER THEMSELVES in a given prompt.
            
            UNDERSTANDING USER REFERENCES:
            - Direct pronouns: "me", "my", "I", "myself", "mine"
            - Contextual references: words that implicitly refer to the user
            - Possessive indicators: showing ownership by the user
            - Location references: when "here" means the user's location
            
            IMPORTANT: Use your intelligence to infer user references, don't just match exact words.
            
            EXAMPLES:
            
            Input: "place a table near me"
            Analysis: "me" clearly refers to the user
            Output: {{"me": "user reference"}}
            
            Input: "find my phone in the kitchen" 
            Analysis: "my" indicates the phone belongs to the user
            Output: {{"my": "user reference"}}
            
            Input: "bring coffee here"
            Analysis: "here" likely refers to where the user is located
            Output: {{"here": "user reference"}}
            
            Input: "show the weather forecast"
            Analysis: No words refer to the user themselves
            Output: {{}}
            
            Input: "turn on my lights when I arrive"
            Analysis: "my" shows ownership, "I" is direct user reference
            Output: {{"my": "user reference", "I": "user reference"}}
            
            Now analyze this prompt and identify ALL words that refer to the user:
            
            Input: "{prompt}"
            Analysis: Think about which words refer to the user themselves
            Output: """
        
        # Object categorization
        self.object_prompt = """
            You are an intelligent object detector. Your task is to identify PHYSICAL OBJECTS and ITEMS in a given prompt.
            
            UNDERSTANDING OBJECTS:
            - Physical items: table, chair, cup, phone, book, lamp, etc.
            - Furniture: desk, sofa, bed, cabinet, shelf
            - Electronics: TV, computer, laptop, tablet, speaker
            - Kitchen items: coffee, water, plate, fork, microwave
            - Personal items: keys, wallet, glasses, clothes
            - Tools and equipment: pen, hammer, scissors
            
            IMPORTANT: Only identify tangible, physical objects that can be touched or moved.
            
            EXAMPLES:
            
            Input: "place a table near me"
            Analysis: "table" is a physical furniture object
            Output: {{"table": "object"}}
            
            Input: "find my phone in the kitchen"
            Analysis: "phone" is a physical electronic device
            Output: {{"phone": "object"}}
            
            Input: "bring coffee and a cup here"
            Analysis: "coffee" is a beverage (physical), "cup" is a container object
            Output: {{"coffee": "object", "cup": "object"}}
            
            Input: "turn on the lights"
            Analysis: "lights" are physical lighting fixtures
            Output: {{"lights": "object"}}
            
            Input: "show me the weather"
            Analysis: "weather" is not a physical object
            Output: {{}}
            
            Input: "move the chair to my desk"
            Analysis: "chair" and "desk" are both furniture objects
            Output: {{"chair": "object", "desk": "object"}}
            
            Now analyze this prompt and identify ALL physical objects:
            
            Input: "{prompt}"
            Analysis: Think about which words represent physical, tangible objects
            Output: """
        
        # Action categorization
        self.action_prompt = """
            You are an intelligent action detector. Your task is to identify ACTION and MOTION words in a given prompt.
            
            UNDERSTANDING ACTIONS:
            - Physical placement: place, put, set, position, mount, install
            - Movement actions: move, bring, take, carry, lift, push, pull, drag
            - Search actions: find, locate, search, look, seek, discover, hunt
            - Display actions: show, display, present, exhibit, reveal, demonstrate
            - Control actions: turn, start, stop, open, close, switch, activate
            - Communication actions: call, send, tell, ask, say, speak, announce
            - Creation actions: make, build, create, write, draw, design, construct
            - Manipulation actions: grab, hold, rotate, flip, twist, bend, fold
            - Navigation actions: go, come, walk, run, drive, navigate, travel
            - Operational actions: operate, use, play, run, execute, perform
            
            IMPORTANT: Only identify verbs that describe actions to be performed or motions to be executed.
            
            EXAMPLES:
            
            Input: "place a table near me"
            Analysis: "place" is a physical positioning action
            Output: {{"place": "action"}}
            
            Input: "find my phone and bring it here"
            Analysis: "find" is a search action, "bring" is a movement action
            Output: {{"find": "action", "bring": "action"}}
            
            Input: "display the weather forecast"
            Analysis: "display" is a presentation action
            Output: {{"display": "action"}}
            
            Input: "turn on the lights and open the door"
            Analysis: "turn" is a control action, "open" is a manipulation action
            Output: {{"turn": "action", "open": "action"}}
            
            Input: "the table is wooden"
            Analysis: "is" is a state verb, not an action - no actions to perform
            Output: {{}}
            
            Input: "move and rotate the chair carefully"
            Analysis: "move" is a movement action, "rotate" is a manipulation action
            Output: {{"move": "action", "rotate": "action"}}
            
            Input: "create a document and send it"
            Analysis: "create" is a creation action, "send" is a communication action
            Output: {{"create": "action", "send": "action"}}
            
            Now analyze this prompt and identify ALL action/motion words:
            
            Input: "{prompt}"
            Analysis: Think about which words represent actions or motions to perform
            Output: """
        
        # Location categorization
        self.spatial_relationship_prompt = """
            You are an intelligent spatial relationship detector. Your task is to identify SPATIAL RELATIONSHIP words in a given prompt.
            
            UNDERSTANDING SPATIAL RELATIONSHIPS:
            - Positional prepositions: on, at, under, over, above, below, beneath
            - Directional words: left, right, front, back, behind, ahead, forward, backward
            - Proximity indicators: near, close, far, next, beside, adjacent, nearby, distant
            - Containment words: inside, outside, within, beyond, throughout, across
            - Vertical relationships: up, down, top, bottom, high, low, upper, lower
            - Horizontal relationships: side, middle, center, edge, corner, end
            - Relative positions: between, among, around, through, along, past
            - Orientation words: north, south, east, west, upright, sideways, diagonal
            
            IMPORTANT: Only identify words that describe spatial relationships between objects, NOT scene/location names like rooms or places.
            
            EXAMPLES:
            
            Input: "place a table near me"
            Analysis: "near" indicates proximity/spatial relationship
            Output: {{"near": "spatial"}}
            
            Input: "find my phone in the kitchen"
            Analysis: "in" is a containment preposition (spatial relationship)
            Output: {{"in": "spatial"}}
            
            Input: "put the cup on the table"
            Analysis: "on" indicates a positional relationship (surface contact)
            Output: {{"on": "spatial"}}
            
            Input: "move the chair to the left side"
            Analysis: "left" is directional, "side" indicates position
            Output: {{"left": "spatial", "side": "spatial"}}
            
            Input: "bring coffee here"
            Analysis: No spatial relationship words, "here" refers to location but not a relationship
            Output: {{}}
            
            Input: "show me the weather"
            Analysis: No spatial relationship words present
            Output: {{}}
            
            Input: "hang the picture above the sofa"
            Analysis: "above" shows vertical spatial relationship
            Output: {{"above": "spatial"}}
            
            Input: "place it between the window and the door"
            Analysis: "between" indicates relative position among objects
            Output: {{"between": "spatial"}}
            
            Input: "put the book beside the lamp"
            Analysis: "beside" indicates proximity spatial relationship
            Output: {{"beside": "spatial"}}
            
            Now analyze this prompt and identify ALL spatial/location words:
            
            Input: "{prompt}"
            Analysis: Think about which words describe spatial relationships, positions, or locations
            Output: """
        
        # Global scene categorization
        self.global_scene_prompt = """
            You are an intelligent scene detector. Your task is to identify SCENE and LOCATION words in a given prompt.
            
            UNDERSTANDING SCENES/LOCATIONS:
            - Indoor rooms: kitchen, bedroom, living room, bathroom, dining room, office, study
            - Functional spaces: garage, basement, attic, closet, pantry, laundry room
            - Commercial places: store, restaurant, hospital, school, bank, mall, library
            - Outdoor locations: garden, yard, driveway, patio, balcony, park, street
            - Building areas: hallway, lobby, entrance, exit, stairs, elevator, roof
            - Geographic references: city, town, neighborhood, downtown, suburbs
            - Specific venues: gym, theater, stadium, church, museum, airport
            - Natural environments: beach, forest, mountain, lake, river, field
            - Transportation hubs: station, terminal, platform, dock, port
            - Work environments: factory, workshop, laboratory, clinic, courthouse
            
            IMPORTANT: Only identify words that name specific places, locations, or scenes, NOT spatial relationship words.
            
            EXAMPLES:
            
            Input: "place a table near me"
            Analysis: No scene or location names present
            Output: {{}}
            
            Input: "find my phone in the kitchen"
            Analysis: "kitchen" is a room/scene location
            Output: {{"kitchen": "scene"}}
            
            Input: "put the cup on the table"
            Analysis: No scene or location names present
            Output: {{}}
            
            Input: "move the chair to the living room"
            Analysis: "living room" is a room/scene location
            Output: {{"living room": "scene"}}
            
            Input: "bring coffee here"
            Analysis: "here" refers to current location but is not a specific scene name
            Output: {{}}
            
            Input: "show me the weather"
            Analysis: No scene or location names present
            Output: {{}}
            
            Input: "hang the picture in the bedroom and bathroom"
            Analysis: "bedroom" and "bathroom" are both room/scene locations
            Output: {{"bedroom": "scene", "bathroom": "scene"}}
            
            Input: "meet me at the restaurant downtown"
            Analysis: "restaurant" is a commercial place, "downtown" is a geographic area
            Output: {{"restaurant": "scene", "downtown": "scene"}}
            
            Input: "park the car in the garage"
            Analysis: "garage" is a functional space/scene location
            Output: {{"garage": "scene"}}
            
            Now analyze this prompt and identify ALL scene/location words:
            
            Input: "{prompt}"
            Analysis: Think about which words name specific places, locations, or scenes
            Output: """
        
    def categorize_user_reference(self, prompt: str) -> Dict[str, str]:
        full_prompt = self.user_reference_prompt.format(prompt = prompt)
            
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature = 0.1,
                    max_output_tokens=200
                )
            )
                
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
                
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                user_words = json.loads(json_str)
                return user_words
            else:
                print(f"No valid JSON found in response: {response_text}")
                return {}
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text}")
            return {}
        except Exception as e:
            print(f"LLM categorization error: {e}")
            return {}
            
    
    def categorize_object(self, prompt: str) -> Dict[str, str]:
        full_prompt = self.object_prompt.format(prompt = prompt)
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200
                )
            )
            
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                objects = json.loads(json_str)
                return objects
            else:
                print(f"No valid JSON found in response: {response_text}")
                return {}
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text}")
            return {}
        except Exception as e:
            print(f"Object categorization error: {e}")
            return {}
    
    def categorize_action(self, prompt: str) -> Dict[str, str]:
        full_prompt = self.action_prompt.format(prompt = prompt)
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200
                )
            )
            
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                objects = json.loads(json_str)
                return objects
            else:
                print(f"No valid JSON found in response: {response_text}")
                return {}
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text}")
            return {}
        except Exception as e:
            print(f"Object categorization error: {e}")
            return {}
    
    def categorize_spatial_relationship(self, prompt: str) -> Dict[str, str]:
        full_prompt = self.spatial_relationship_prompt.format(prompt = prompt)

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200
                )
            )
            
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                objects = json.loads(json_str)
                return objects
            else:
                print(f"No valid JSON found in response: {response_text}")
                return {}
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text}")
            return {}
        except Exception as e:
            print(f"Object categorization error: {e}")
            return {}
    
    def categorize_global_scene (self, prompt: str) -> Dict[str, str]:
        full_prompt = self.global_scene_prompt.format(prompt = prompt)

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200
                )
            )
            
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                objects = json.loads(json_str)
                return objects
            else:
                print(f"No valid JSON found in response: {response_text}")
                return {}
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text}")
            return {}
        except Exception as e:
            print(f"Object categorization error: {e}")
            return {}

 
''' 
def categorize_prompt(prompt):
    categorized_prompt = LanguageAgent()
    return categorized_prompt.categorize_user_reference(prompt), categorized_prompt.categorize_object(prompt), categorized_prompt.categorize_action(prompt), categorized_prompt.categorize_spatial_relationship(prompt), categorized_prompt.categorize_global_scene(prompt)
'''
# Test
# print(categorize_prompt("place coffee between that table and me"))
# print(categorize_prompt("rotate the chair sixty degrees"))
# print(categorize_prompt("grab that apple and place it on my hand"))
# print(categorize_prompt("create a new kitchen!"))
import sys
from pathlib import Path
import google.generativeai as genai
import json
from typing import Dict, Optional

# Add backEnd directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from database import Database

class CodeAgent:
    """
    Code Agent handles:
    - Translating spatial transformations into database operations
    - Executing position/rotation updates
    - Maintaining scene consistency
    """

    def __init__(self, database: Database):
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        # Initialize the database
        self.database = database

    
    def execute_transformation (self, transformation: Dict) -> Dict:
        """
            Execute a spatial transformation on the scene.

            Args:
                transformation: Dict with: specify datastructures of input
                {
                    "object_id": str,
                    "position": {
                        "x": float, 
                        "y": float, 
                        "z": float
                    },
                    "rotation": {
                        "x": float, 
                        "y": float, 
                        "z": float
                    },
                    "action": "place" | "move" | "rotate"
                }

            return:
                Dict w/ execution:
                {
                    "success": bool,
                    "object_id": str,
                    "action": str,
                    "message": str
                }
                
        """
        if not transformation: 
            return {
                "success": False,
                "object_id": None,
                "action": None,
                "message": "no transformation"
            }
            

        object_id = transformation.get('object_id')
        position = transformation.get('position')
        rotation = transformation.get('rotation')
        action = transformation.get('action')

        print(f"\n💻 Code Agent executing:")
        print(f"   Object ID: {object_id}")
        print(f"   Action: {action}")

        try:
            # first need to verify that the object exist
            obj = self.database.get_object_by_id(object_id)
            if not obj:
                return {
                    "success": False,
                    "object_id": object_id,
                    "action": action,
                    "message": f"Object {object_id} not found"
                }
                
            success = True

            if action in ['move', 'place']:
                # execute the update of the position by calling database
                success = self.database.update_object_position (object_id, position)
                print(f"✓ Position updated: {position}")
            if action == 'rotate':
                # execute the rotation
                success= success and self.database.update_object_rotation(object_id, rotation)
                print(f"✓ Rotation updated: {rotation}")


                    
        except Exception as e:
            print (f"❌code agent error: {e}")
            return {
                "success": False,
                "object_id": object_id,
                "action": action,
                "message": f"Execution error: {str(e)}"
            }
    
    def validate_transformation (self, transformation: Dict) -> bool:
        """
        Validate a transformation before execution.
        
        Args:
            transformation: Transformation dict to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not transformation:
            return False
        
        required_fields = ['object_id', 'position', 'rotation', 'action']
        for field in required_fields:
            if field not in transformation:
                print(f"⚠️ Missing required field: {field}")
                return False
        
        # Validate position format
        position = transformation['position']
        if not all(k in position for k in ['x', 'y', 'z']):
            print(f"⚠️ Invalid position format")
            return False
        
        # Validate rotation format
        rotation = transformation['rotation']
        if not all(k in rotation for k in ['x', 'y', 'z']):
            print(f"⚠️ Invalid rotation format")
            return False
        
        return True



# Test
if __name__ == "__main__":
    from database import Database
    
    # Initialize database
    db = Database()
    
    # Initialize code agent
    agent = CodeAgent(db)
    
    # Test transformation
    test_transformation = {
        'object_id': 'chair_01',
        'position': {'x': 0.5, 'y': -1.0, 'z': -1.3},
        'rotation': {'x': 0, 'y': -1.5707963267948966, 'z': 0},
        'action': 'move'
    }
    
    print("\n🧪 Testing Code Agent...")
    result = agent.execute_transformation(test_transformation)
    
    # Test validation
    print("\n🧪 Testing validation...")
    is_valid = agent.validate_transformation(test_transformation)
    print(f"Valid: {is_valid}")


            


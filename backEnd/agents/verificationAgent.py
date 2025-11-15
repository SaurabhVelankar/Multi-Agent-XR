import json
import os
from typing import Dict, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Database


class VerificationAgent:
    def __init__(self, database):
        # Initialize the database
        self.database = database
    
    def get_object_state (self, object_name: str) -> Optional[Dict]:
        """
        Get current state of an object by name
        
        Args:
            object_name: Name of the object (e.g., "chair")
        
        Returns:
            Object dict with id, position, rotation, or None if not found
        """

        objects = self.database.get_objects_by_name(object_name)

        if not objects:
            print(f"  ⚠️ No object found with name '{object_name}'")
            return None
        
        if len(objects) > 1:
            print(f"  ⚠️ Multiple objects found with name '{object_name}', using first one")
        
        obj = objects[0]
        return {
            'id': obj['id'],
            'name': obj['name'],
            'position': obj['position'],
            'rotation': obj['rotation']
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
    agent = VerificationAgent(db)
    
    # Get object state
    state = agent.get_object_state("chair")
    print(f"Current state: {state}")
    id = state.get("id")
    name = state.get("name")
    position = state.get("position")
    
    # Execute update
    if state:
        updates = {
            'position': {'x': 0.5, 'y': 0, 'z': -1.5}
        }
    
    test_transformation = {
        'object_id': id,
        'name': name,
        'position': position,
        'rotation': {'x': 0, 'y': -1.5707963267948966, 'z': 0},
        'action': 'move'
    }

    # Test validation
    result = agent.validate_transformation(test_transformation)
    print(result)

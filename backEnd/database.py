'''
    Database module for BackEnd Agents.
    Loads data from the sceneData.json in the WebXR folder.
    This module contains two different functionalities:
    1. Grab data from the .json file in the WebXR frontEnd;
    2. Update change made by the MAS backEnd to the .json file.
'''

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class Database:
    """
        Python interface to scene data (loads from JSON)
        Agents use this to query and modify scene state
    """

    def __init__(self):
        """
        Initialize data exchange 
        Args:
            json_path: Path to sceneData.json file
        """
        repo_root = Path(__file__).resolve().parents[1]
        self.json_path = repo_root / "webXR" / "sceneData.json"
        self.load()

    def load(self):
        # load scene from JSON file
        try:
            with open (self.json_path, 'r') as f:
                self.scene_data = json.load(f)

            # For fast demo we just consider load object data right now
            self.objects = self.scene_data['objects']
            # for testing Database().load()
            # return self.objects
        
        except FileNotFoundError:
            print(f"❌ Scene file not found: {self.json_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in scene file: {e}")
            raise
    
    """
        Query Methods: basic functionalities of a database
        Extraction of data by id, name, category, etc.
    """
    def get_object_by_id(self, object_id: str):
        """
        Fine the object by thier ID

        Args:
            object_id: Object ID (e.g., "table_01")
        Returns:
            Object dict or None if not found
        """
        for obj in self.objects:
            if obj['id'] == object_id:
                return obj
            else:
                return None
    
    def get_objects_by_name(self, name: str):
        """
        Find objects by name (partial match)

        Args:
            name: Object name to search for (e.g., "chair")
        Returns:
            List of matching objects
        """
        return [obj for obj in self.objects 
                if name.lower() in obj['name'].lower()]

    def get_objects_by_category(self, category: str) -> List[Dict]:
        """
        Find objects by category

        Args:
            category: Category name (e.g., "furniture")

        Returns:
        List of objects in that category
        """
        return [obj for obj in self.objects 
                if obj.get('category', '').lower() == category.lower()]

    def get_objects_near_position(self, 
                                  position: Dict[str, float], 
                                  radius: float = 1.0
                                  ) -> List[Dict]:
        """
        Find objects within radius of position

        Args:
            position: Dict with {x, y, z} keys
            radius: search radius in meters
        Returns:
            List of objects within radius
        """
        # Initialize nearby object list
        nearby = []
        for obj in self.objects:
            pos = obj['position']
            # calculate Euclidean distance (x,y,z)
            distance = (
                (pos['x'] - position['x'])**2 + 
                (pos['y'] - position['y'])**2 +
                (pos['z'] - position['z'])**2
            )**0.5

            if distance <= radius:
                nearby.append(obj)
        
        return nearby
    
    def get_movable_objects(self) -> List[Dict]:
        """
        Get all movable objects

        Returns:
            List of objects which are movable (movable=True)
        """

        return [obj for obj in self.objects 
                if obj.get('properties', {}).get('movable', False)]

    def get_spatial_relationships(self, object_id: str) -> Optional[Dict]:
        obj = self.get_object_by_id(object_id)
        return obj.get('spatialRelations') if obj else None
    
    # def get_scene_bounds (self) -> Dict:
        """
        Get scene boundaries
   
        Returns:
            Dict with min and max bounds
        """
        # return self.metadata['bounds']
    
    """
        Modification methods: Update scene
    """

    def update_object_position(self, 
                               object_id: str, 
                               new_position: Dict[str, float]
                               ) -> bool:
        """
        Update object position in memory

        Args:
            object_id: Object ID
            new_position: New position w/ updated rotation {x, y, z}
            (in radians)

        Returns:
            True if successful, false if cannot find the object
        """
        obj = self.get_object_by_id(object_id)
        if obj:
            obj['position'].update(new_position)
            print(f"Updated {obj['name']} position to {new_position}")
            return True
        else: 
            return False
        
    def update_object_rotation(self, 
                               object_id: str, 
                               new_rotation: Dict[str, float]
                               ) -> bool:
        obj = self.get_object_by_id(object_id)
        if obj:
            obj['rotation'].update(new_rotation)
            print(f"Updated {obj['name']} rotation to {new_rotation}")
            return True
        else:
            return False
        
    def add_object(self,
                   object_data: Dict
                   ) -> str:
        """
        Add new object to the sceneData.json

        Args:
            object_data: complete object definition diction data structure

        Returns:
            object ID of the newly added object
        """

        # ensure that the object has an id
        if 'id' not in object_data:
            # automatically generate an id from base_name
            base_name = object_data.get('name', 'object').replace(' ', '_')
            count = len([o for o in self.objects if o['name'] == object_data.get('name')])
            object_data['id'] = f"{base_name}_{count + 1:02d}"

        self.objects.append(object_data)
        print(f"Added new object: {object_data['name']} ({object_data['id']})")
        return object_data['id']

    def remove_object(self, object_id: str) -> bool:
        """
        Remove object from scene

        Args:
            object_id: Object ID to remove

        Returns:
            True if succeed, flase if not
        """
        for i, obj in enumerate(self.objects):
            if obj['id'] == object_id:
                removed = self.objects.pop(i)
                print(f"Removed object: {removed['name']} ({object_id})")
                return True
        return False

    """
        Data visualization
    """

    def get_statistics(self) -> Dict:
        """
        Get statistics about the scene
        
        Returns:
            Dict with scene statistics
        """
        return {
            'total_objects': len(self.objects),
            'movable_objects': len(self.get_movable_objects()),
            'categories': list(set(obj.get('category', 'unknown') for obj in self.objects))
        }
    
    def print_statistics(self):
        """Print scene statistics"""
        stats = self.get_statistics()
        print(f"{'='*50}")
        print(f"Total Objects: {stats['total_objects']}")
        print(f"Movable Objects: {stats['movable_objects']}")
        print(f"Categories: {', '.join(stats['categories'])}")


"""
    Test cases
"""
db = Database()

# Test load data
print(db.load()) # Succeed

# Test data visualization
db.print_statistics()
"""     
        Test result: PASS
    ==================================================
        Total Objects: 6
        Movable Objects: 6
        Categories: vehicle, furniture
""" 

# Test for query methods

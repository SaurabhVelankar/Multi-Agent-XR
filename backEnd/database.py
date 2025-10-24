'''
    Database module for BackEnd Agents.
    Loads data from the sceneData.json in the WebXR folder.
    This module contains two different functionalities:
    1. Grab data from the .json file in the WebXR frontEnd;
    2. Update change made by the MAS backEnd to the .json file.
'''

import json
from typing import Dict, List, Optional, Tuple
from math import float

class Database:
    """
        Python interface to scene data (loads from JSON)
        Agents use this to query and modify scene state
    """

    def __init__(self, json_path='../webXR/sceneData.json'):
        """
        Initialize data exchange 
        Args:
            json_path: Path to sceneData.json file
        """

        self.json_path = json_path
        self.load()
    
    def load(self):
        # load scene from JSON file
        try:
            with open (self.json_path, 'r') as f:
                self.scene_data = json.load(f)

            # For fast demo we just consider load object data right now
            self.objects = self.scene_data['objects']
        
        except FileNotFoundError:
            print(f"❌ Scene file not found: {self.json_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in scene file: {e}")
            raise
    
    """
        Query Methods
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
    
    def get_scene_bounds (self) -> Dict:
        """
        Get scene boundaries
   
        Returns:
            Dict with min and max bounds
        """
        return self.metadata['bounds']




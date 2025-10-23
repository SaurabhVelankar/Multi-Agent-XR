/* eslint-disable sort-imports */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Text } from 'troika-three-text';
import { XR_BUTTONS } from 'gamepad-wrapper';
import { gsap } from 'gsap';
import { init } from './init.js';
import { loadSceneDatabase, getSceneDatabase, SceneQuery } from './sceneLoader.js';

// Global scene query interface for agents
let sceneQuery;
let loadedObjects = new Map(); // Maps object IDs to THREE.js objects
let sceneDatabase;

async function setupScene({ scene, camera, renderer, player, controllers }) {
    
    // Load scene database from JSON
    console.log('Loading scene from JSON...');
    sceneDatabase = await loadSceneDatabase();
    
    // Initialize scene query system
    sceneQuery = new SceneQuery(sceneDatabase);
    
    // Load textures
    const textureLoader = new THREE.TextureLoader();
    const textures = new Map();
    
    // Load structure (floor and walls)
    await loadStructure(scene, textureLoader, textures);
    
    // Load all objects from database
    await loadObjects(scene);
    
    // Setup lighting from database
    loadLighting(scene);
    
    // Make sceneQuery globally accessible for agents
    window.sceneQuery = sceneQuery;
    window.loadedObjects = loadedObjects;
    window.sceneDatabase = sceneDatabase;
    
    console.log('✅ Scene loaded from JSON with', sceneDatabase.objects.length, 'objects');
}

/**
 * Load structural elements (floor, walls) from database
 */
function loadStructure(scene, textureLoader, textures) {
    return new Promise((resolve) => {
        // Load floor
        const floorData = sceneDatabase.structure.floor;
        const floorTexture = textureLoader.load(floorData.texture);
        
        const floorGeometry = new THREE.PlaneGeometry(
            floorData.geometry.width, 
            floorData.geometry.height
        );
        const floorMaterial = new THREE.MeshStandardMaterial({ 
            map: floorTexture 
        });
        
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.position.set(floorData.position.x, floorData.position.y, floorData.position.z);
        floor.rotation.set(floorData.rotation.x, floorData.rotation.y, floorData.rotation.z);
        floor.scale.set(floorData.scale.x, floorData.scale.y, floorData.scale.z);
        floor.userData.id = floorData.id;
        
        scene.add(floor);
        loadedObjects.set(floorData.id, floor);
        
        // Load walls
        const wallTexture = textureLoader.load(sceneDatabase.structure.walls[0].texture);
        
        sceneDatabase.structure.walls.forEach((wallData, index) => {
            const wallGeometry = new THREE.PlaneGeometry(
                wallData.geometry.width,
                wallData.geometry.height
            );
            const wallMaterial = new THREE.MeshStandardMaterial({ 
                map: wallTexture 
            });
            
            // Create front face
            const wall1 = new THREE.Mesh(wallGeometry, wallMaterial);
            wall1.position.set(wallData.position.x, wallData.position.y, wallData.position.z);
            wall1.rotation.set(wallData.rotation.x, wallData.rotation.y, wallData.rotation.z);
            wall1.scale.set(wallData.scale.x, wallData.scale.y, wallData.scale.z);
            wall1.userData.id = `${wallData.id}_front`;
            scene.add(wall1);
            
            // Create back face (for visibility from both sides)
            const wall2 = new THREE.Mesh(wallGeometry, wallMaterial);
            wall2.position.set(wallData.position.x, wallData.position.y, wallData.position.z);
            wall2.rotation.set(
                wallData.rotation.x + (wallData.rotation.y === 0 ? Math.PI : 0),
                wallData.rotation.y + (wallData.rotation.y !== 0 ? Math.PI : 0),
                wallData.rotation.z
            );
            wall2.scale.set(wallData.scale.x, wallData.scale.y, wallData.scale.z);
            wall2.userData.id = `${wallData.id}_back`;
            scene.add(wall2);
            
            loadedObjects.set(`${wallData.id}_front`, wall1);
            loadedObjects.set(`${wallData.id}_back`, wall2);
        });
        
        resolve();
    });
}

/**
 * Load all objects from database
 */
function loadObjects(scene) {
    const gltfLoader = new GLTFLoader();
    
    // Create array of promises for all object loads
    const loadPromises = sceneDatabase.objects.map(objData => {
        return new Promise((resolve, reject) => {
            gltfLoader.load(
                objData.modelPath,
                (gltf) => {
                    // Apply transformations from database
                    gltf.scene.position.set(
                        objData.position.x,
                        objData.position.y,
                        objData.position.z
                    );
                    gltf.scene.rotation.set(
                        objData.rotation.x,
                        objData.rotation.y,
                        objData.rotation.z
                    );
                    gltf.scene.scale.set(
                        objData.scale.x,
                        objData.scale.y,
                        objData.scale.z
                    );
                    
                    // Store metadata for agent access
                    gltf.scene.userData = {
                        id: objData.id,
                        name: objData.name,
                        category: objData.category,
                        properties: objData.properties,
                        dbReference: objData
                    };
                    
                    scene.add(gltf.scene);
                    loadedObjects.set(objData.id, gltf.scene);
                    
                    console.log(`✓ Loaded: ${objData.name} (${objData.id})`);
                    resolve();
                },
                undefined,
                (error) => {
                    console.error(`✗ Error loading ${objData.name}:`, error);
                    reject(error);
                }
            );
        });
    });
    
    // Wait for all objects to load
    return Promise.all(loadPromises);
}

/**
 * Load lighting from database
 */
function loadLighting(scene) {
    sceneDatabase.lighting.forEach(lightData => {
        let light;
        
        if (lightData.type === 'ambient') {
            light = new THREE.AmbientLight(lightData.color, lightData.intensity);
        } else if (lightData.type === 'directional') {
            light = new THREE.DirectionalLight(lightData.color, lightData.intensity);
            if (lightData.position) {
                light.position.set(
                    lightData.position.x,
                    lightData.position.y,
                    lightData.position.z
                );
            }
        }
        
        if (light) {
            light.userData.id = lightData.id;
            scene.add(light);
            console.log(`✓ Added ${lightData.type} light: ${lightData.id}`);
        }
    });
}

/**
 * API for agents to modify the scene
 */
window.agentAPI = {
    // Move an object to a new position
    moveObject: (objectId, newPosition, animate = true) => {
        const threeObject = loadedObjects.get(objectId);
        const dbObject = sceneQuery.getObjectById(objectId);
        
        if (!threeObject || !dbObject) {
            console.error(`Object ${objectId} not found`);
            return false;
        }
        
        if (animate) {
            // Smooth animation using GSAP
            gsap.to(threeObject.position, {
                x: newPosition.x,
                y: newPosition.y,
                z: newPosition.z,
                duration: 1.0,
                ease: "power2.inOut"
            });
        } else {
            threeObject.position.set(newPosition.x, newPosition.y, newPosition.z);
        }
        
        // Update database
        sceneQuery.updateObjectPosition(objectId, newPosition);
        console.log(`Moved ${dbObject.name} to`, newPosition);
        return true;
    },
    
    // Rotate an object
    rotateObject: (objectId, newRotation, animate = true) => {
        const threeObject = loadedObjects.get(objectId);
        
        if (!threeObject) {
            console.error(`Object ${objectId} not found`);
            return false;
        }
        
        if (animate) {
            gsap.to(threeObject.rotation, {
                x: newRotation.x,
                y: newRotation.y,
                z: newRotation.z,
                duration: 1.0,
                ease: "power2.inOut"
            });
        } else {
            threeObject.rotation.set(newRotation.x, newRotation.y, newRotation.z);
        }
        
        return true;
    },
    
    // Get user position (for "place near me" commands)
    getUserPosition: (player) => {
        return {
            x: player.position.x,
            y: player.position.y,
            z: player.position.z
        };
    },
    
    // Query objects by natural language
    queryObjects: (query) => {
        // Simple example - can be enhanced with NLP
        if (query.includes('table')) {
            return sceneQuery.getObjectsByName('table');
        } else if (query.includes('chair')) {
            return sceneQuery.getObjectsByName('chair');
        }
        // Add more query logic as needed
    },
    
    // Get scene state for verification agent
    getSceneState: () => {
        return {
            objects: sceneDatabase.objects,
            loadedObjects: Array.from(loadedObjects.keys()),
            bounds: sceneQuery.getSceneBounds()
        };
    },
    
    // Save current scene state (optional)
    saveScene: async () => {
        return await sceneQuery.saveToServer('/api/scene/save');
    }
};

function onFrame(delta, time, { scene, camera, renderer, player, controllers }) {
    // Add any per-frame logic here
    // For example, update spatial relationships based on user position
}

init(setupScene, onFrame);
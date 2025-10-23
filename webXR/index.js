/*
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Text } from 'troika-three-text';
import { XR_BUTTONS } from 'gamepad-wrapper';
import { gsap } from 'gsap';
import { init } from './init.js';

function setupScene({ scene, camera, renderer, player, controllers }) {

    // Load the texture
    const textureLoader = new THREE.TextureLoader();
    const floorTexture = textureLoader.load('assets/textures/wood-floor-texture.png');
    const wallTexture = textureLoader.load('assets/textures/brick.png')

    // Add a floor
    const floorGeometry = new THREE.PlaneGeometry(6, 6);
    const floorMaterial = new THREE.MeshStandardMaterial({ 
      map: floorTexture
    });

    const floor = new THREE.Mesh(floorGeometry, floorMaterial);

    floor.rotateX(-Math.PI / 2);
    floor.scale.set(1/3,1/3,1/3);
    floor.position.set(0,-1,-1.5);
    scene.add(floor);

    // Add walls
    const wallGeometry = new THREE.PlaneGeometry(6, 3);
    const wallMaterial = new THREE.MeshStandardMaterial({ 
      map: wallTexture
    });

    // Wall 1
    const wall1_1 = new THREE.Mesh(wallGeometry, wallMaterial);
    wall1_1.rotateY(Math.PI / 2);
    wall1_1.scale.set(1/3,1/3,1/3);
    wall1_1.position.set(-1,-0.5,-1.5);
    scene.add(wall1_1);

    const wall1_2 = new THREE.Mesh(wallGeometry, wallMaterial);
    wall1_2.rotateY(-Math.PI / 2);
    wall1_2.scale.set(1/3,1/3,1/3);
    wall1_2.position.set(-1,-0.5,-1.5);
    scene.add(wall1_2);

    // Wall 2
    const wall2_1 = new THREE.Mesh(wallGeometry, wallMaterial);
    //wall2_1.rotateZ(Math.PI / 2);
    wall2_1.scale.set(1/3,1/3,1/3);
    wall2_1.position.set(0,-0.5,-2.5);
    scene.add(wall2_1);

    const wall2_2 = new THREE.Mesh(wallGeometry, wallMaterial);
    wall2_2.rotateX(-Math.PI);
    wall2_2.scale.set(1/3,1/3,1/3);
    wall2_2.position.set(0,-0.5,-2.5);
    scene.add(wall2_2);

    // Wall 3
    const wall3_1 = new THREE.Mesh(wallGeometry, wallMaterial);
    wall3_1.rotateY(Math.PI / 2);
    wall3_1.scale.set(1/3,1/3,1/3);
    wall3_1.position.set(1,-0.5,-1.5);
    scene.add(wall3_1);

    const wall3_2 = new THREE.Mesh(wallGeometry, wallMaterial);
    wall3_2.rotateY(-Math.PI/2);
    wall3_2.scale.set(1/3,1/3,1/3);
    wall3_2.position.set(1,-0.5,-1.5);
    scene.add(wall3_2);




    const gltfLoader = new GLTFLoader();

    // Add table
    gltfLoader.load('assets/gltf-glb-models/table/Table.gltf', (gltf) => {
      gltf.scene.scale.set(1/3,1/3,1/3);
      gltf.scene.position.set(0,-1,-1.5);
      scene.add(gltf.scene);
    });

    // Add chair1
    gltfLoader.load('assets/gltf-glb-models/chair/chair.gltf', (gltf) => {
      gltf.scene.position.set(0.4,-1,-1.5);
      gltf.scene.rotateY(-Math.PI / 2);
      gltf.scene.scale.set(0.005, 0.005, 0.005);
      scene.add(gltf.scene)
    });

    // Add chair2
    gltfLoader.load('assets/gltf-glb-models/chair/chair.gltf', (gltf) => {
      gltf.scene.position.set(-0.3,-1,-1.8);
      gltf.scene.rotateY(Math.PI / 3);
      gltf.scene.scale.set(0.005, 0.005, 0.005);
      scene.add(gltf.scene)
    });

    // Add lamp
    gltfLoader.load('assets/gltf-glb-models/lamp/lamp.glb', (gltf) => {
      gltf.scene.position.set(0.3,-1,-1.2);
      gltf.scene.scale.set(0.025, 0.025, 0.025);
      scene.add(gltf.scene);
    });

    // Add wooden stool
    gltfLoader.load('assets/gltf-glb-models/wooden_stool/wooden_stool.gltf', (gltf) => {
      gltf.scene.position.set(-0.7,-1,-2);
      gltf.scene.scale.set(0.003, 0.003, 0.003);
      scene.add(gltf.scene);
    });

    // Add scooter
    gltfLoader.load('assets/gltf-glb-models/scooter/scooter.glb', (gltf) => {
      gltf.scene.position.set(-0.5,-1,-1);
      gltf.scene.rotateY(2*Math.PI / 3);
      gltf.scene.scale.set(0.008, 0.008, 0.008);
      scene.add(gltf.scene);
    });
}

function onFrame(delta, time, { scene, camera, renderer, player, controllers },) {
}


init(setupScene, onFrame);
*/

/* eslint-disable sort-imports */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Text } from 'troika-three-text';
import { XR_BUTTONS } from 'gamepad-wrapper';
import { gsap } from 'gsap';
import { init } from './init.js';
import { sceneDatabase, SceneQuery } from './sceneDatabase.js';

// Global scene query interface for agents
let sceneQuery;
let loadedObjects = new Map(); // Maps object IDs to THREE.js objects

function setupScene({ scene, camera, renderer, player, controllers }) {
    
    // Initialize scene query system
    sceneQuery = new SceneQuery(sceneDatabase);
    
    // Load textures
    const textureLoader = new THREE.TextureLoader();
    const textures = new Map();
    
    // Load structure (floor and walls)
    loadStructure(scene, textureLoader, textures);
    
    // Load all objects from database
    loadObjects(scene);
    
    // Setup lighting from database
    loadLighting(scene);
    
    // Make sceneQuery globally accessible for agents
    window.sceneQuery = sceneQuery;
    window.loadedObjects = loadedObjects;
    
    console.log('Scene loaded from database with', sceneDatabase.objects.length, 'objects');
}

/**
 * Load structural elements (floor, walls) from database
 */
function loadStructure(scene, textureLoader, textures) {
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
}

/**
 * Load all objects from database
 */
function loadObjects(scene) {
    const gltfLoader = new GLTFLoader();
    
    sceneDatabase.objects.forEach(objData => {
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
                
                console.log(`Loaded object: ${objData.name} (${objData.id})`);
            },
            undefined,
            (error) => {
                console.error(`Error loading ${objData.name}:`, error);
            }
        );
    });
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
            console.log(`Added ${lightData.type} light: ${lightData.id}`);
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
    }
};

function onFrame(delta, time, { scene, camera, renderer, player, controllers }) {
    // Add any per-frame logic here
    // For example, update spatial relationships based on user position
}

init(setupScene, onFrame);
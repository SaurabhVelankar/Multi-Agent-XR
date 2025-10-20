/* eslint-disable sort-imports */
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




    /* Add furnitures (gltf/glb files) */
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
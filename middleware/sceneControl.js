import { gsap } from 'gsap';

/**
 * Update object position from WebSocket message
 */
export function updateObjectPosition(data, loadedObjects) {
  const threeObject = loadedObjects.get(data.objectId);
  if (threeObject) {
    gsap.to(threeObject.position, {
      x: data.position.x,
      y: data.position.y,
      z: data.position.z,
      duration: 0.5,
      ease: "power2.inOut"
    });
    console.log(`✨ Updated ${data.name} position from backend`);
  } else {
    console.warn(`Object ${data.objectId} not found in scene`);
  }
}

/**
 * Update object rotation from WebSocket message
 */
export function updateObjectRotation(data, loadedObjects) {
  const threeObject = loadedObjects.get(data.objectId);
  if (threeObject) {
    gsap.to(threeObject.rotation, {
      x: data.rotation.x,
      y: data.rotation.y,
      z: data.rotation.z,
      duration: 0.5,
      ease: "power2.inOut"
    });
    console.log(`✨ Updated ${data.name} rotation from backend`);
  } else {
    console.warn(`Object ${data.objectId} not found in scene`);
  }
}
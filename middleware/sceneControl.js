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


/**
 * Add head tracking function for the scene control module
 */
let ws = null;
let isTracking = false;

export function initHeadTracking(websocket){
  ws = websocket;
  console.log('✅ Head tracking initialized');

}

export function startHeadTracking(){
  isTracking = true;
  console.log('👤 Head tracking started');
}

export function stopHeadTracking(){
  isTracking = false;
  console.log('👤 Head tracking stopped');
}

// Convert quaternion to Euler angles
function quaternion_to_euler(q){
  const {x, y, z, w} = q;
  // Roll (x-axis)
  const sinr_cosp = 2 * (w * x + y * z);
  const cosr_cosp = 1 - 2 * (x * x + y * y);
  const roll = Math.atan2(sinr_cosp, cosr_cosp);

  // Pitch (y-axis)
  const sinp = 2 * (w * y - z * x);
  const pitch = Math.abs(sinp) >= 1
    ? Math.sign(sinp) * Math.PI / 2
    : Math.asin(sinp);

  // Yaw (z-axis)
  const siny_cosp = 2 * (w * z + x * y);
  const cosy_cosp = 1 - 2 * (y * y + z * z);
  const yaw = Math.atan2(siny_cosp, cosy_cosp);

  return { x: roll, y: pitch, z: yaw };
}

export function updateHeadTracking(frame, referenceSpace){
  // console.log('Tracking check:', { isTracking, wsReady: ws?.readyState === 1, frame, referenceSpace });
  if (!isTracking || !ws || ws.readyState !== WebSocket.OPEN){ return; }
  
  if (!frame || !referenceSpace){ return; }
  
  // Get viewer pose from XR frame
  const pose = frame.getViewerPose(referenceSpace);

  if (!pose) { return; }

  // debugg for seeing user head position
  // console.log('Transform:', pose.transform);
  // console.log('Position:', pose.transform?.position);

  // Extract position and rotation
  const position = pose.transform.position;
  const orientation = pose.transform.orientation;

  // convert orientation to euler angels
  const euler = quaternion_to_euler(orientation);

  // send the head information to the backEnd (in JSON format)
  ws.send(JSON.stringify({
    type: 'head_position_update',
    data: {
      position: {
        x: position.x,
        y: position.y,
        z: position.z    
      },
      rotation: {
        x: euler.x,
        y: euler.y,
        z: euler.z
      }
    },
    timestamp: Date.now()
  }));



}
/*
 * Add some codes to this when using for deployment instead of development, 
 * This use as a node.js proxy server to prevent generating SSL certificate everytime 
 * when changing to new IP address. Allow for more production-level deploy
 * 
 * This file is already connected to webpack.config.cjs.
 * To activate concurrently with webXR frontend, just hit npm run dev-full in the root terminal
 * To activatd itself without webXR, just hit npm run start-server
 * Note:
 *      This is just a proxy instead of backend!
 */
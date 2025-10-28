<p align="center">
    <img src="./docs/images/title_image.png" />
</p>

## Multi-Agent-XR

This tutorial teaches you how to navigate to the reseources and basic setup of the project.

## Setup local environment

1. **Clone the repository**: 
    ```bash
    git clone https://github.com/RayChen666/Multi-Agent-XR.git
    ```
2. **Navigate to the project folder**:
    ```bash
    cd Multi-Agent-XR
    ```
3. **Install npm**:
    ```bash
    npm install
    ```

## Open the project:


1. **Check your local IP address by running**:
    ```bash
    ifconfig | grep "inet " | grep -v 127.0.0.1
    ```
    
2. **Gather SSL certificate by running**: (you need to run this command everytime you change your IP address)
    ```bash
    cd backEnd
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout key.pem -out cert.pem -days 365 \
        -subj "/C=US/ST=State/L=City/O=Dev/CN=your-ip-address"
    ```

3. **Open the terminal in the root project folder**:
    if you just want to test the backend, open terminal in *backEnd* folder, run 
    ```bash
    python main.py
    ```
    if you just want to test the frontend, open another terminal, navigate to the project root folder and run
    ```bash
    npm run dev
    ```
4. **Trust certificate on devices:**
    - Desktop: In Chrome browser visit https://localhost:8000 and accept warning
    - Headset: In Quest browser visit https://your-ip-address:8000 and accept warning

5. **Navigate to the scene**:
    To navigate to the scene, go to your browser (either on laptop or XR headset) and type: https://your-ip-address:8081/ and accept warning.
    <p align="center">
    <img src="./docs/images/scene_image.png" />
    </p>

6. **Test update position function**:
    Open the third terminal and type (you need to first open the front and back end) 
    ```bash
    curl -k -X POST "https://localhost:8000/scene/update-position?object_id=chair_01&x=0.4&y=-1&z=-1"
    ```
    The chair with id "chair_01" will move to position {x: 0.4, y: -1, z: -1} and will be broadcasted to all clients connected, similar pattern for rotation function.

## Install Immersive Web Emulator extension
Navigate to: https://chromewebstore.google.com/detail/immersive-web-emulator/cgffilbpcibhmcfbgggfhfolhkfbhmik?hl=en&pli=1 to install the extension for your Chrome browser.

## Relevant reading resources
To understand the idea of the whole project, go to *docs* folder and find *Research Proposal v1.pdf*. To find related articles, go to *Articles* folder under *docs*. The *note* file contains links to some websites that I think useful to the development of this project.

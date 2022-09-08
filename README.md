# keyboard-mouse-mirroring
Mirrors server's keyboard and mouse events on client systems

## Setup
1. Download and install python3 on server and client systems
2. Download and extract this repository on server and client systems
3. Get server's IPv4 address (type in `ipconfig` in terminal) and change the IP in the `server.py` and `client.py` to that IP
4. Run `server.py` on the server system
5. Run `client.py` on the client system

## Usage
- Enable and disable mirror by pressing the `mirrorToggleKey` which is `L` on the server keyboard by default
- The `mirrorToggleKey` can be changed in `server.py` by changing it's VKcode to the desired key
- If there are issues establishing a connection, run both the server and client with administrator privileges
- Always start the server before starting the client

## Notes
- It is possible to have clients connected over the internet via portforwarding however the latency will likely be significant. Simply using LAN results in a slight amount of latency at (estimated) roughly 100ms. When portforwarding, the client's `serverIp` variable must be changed to the server's external IP.
- Only tested on python 3.6

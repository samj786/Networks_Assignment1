# Peer-to-Peer Network

This project is a simple implementation of a peer-to-peer network with a seed node. The seed node maintains a list of active peers and provides this list to any peer that requests it. The peers can then communicate directly with each other.

## Files

- **peer.py**: This file contains the Peer class, which is responsible for handling the peer nodes in the network. It includes methods for connecting to seeds and peers, handling messages, and performing liveness tests.
- **seed.py**: This file contains the Seed class, which is responsible for handling the seed node in the network. It includes methods for listening to incoming connections and handling peers.
- **seedspawner.py**: This file is used to start multiple seed nodes from ports starting from 5000. It will ask for the number of seed nodes to start.
- **config.txt**: This file contains the IP addresses and ports of the seed nodes in the network.
- **outputfile.log**: This file is used for logging.

## Features

- **Seed Node**: The seed node maintains a list of active peers and provides this list to any peer that requests it.
- **Peer Node**: The peer nodes can connect to the seed node to get a list of active peers. They can then communicate directly with these peers.
- **Liveness Test**: The peer nodes periodically send liveness requests to check if the other nodes are still active.
- **Message Generation and Handling**: The peer nodes can generate and send messages to other peers. They can also handle incoming messages.

> Please note that this is a simple implementation and may not include all the features of a full-fledged peer-to-peer network.

## How to run

There are two methods to run the code:

### Method 1 (RECOMMENDED)

1. Run the `seedspawner.py` file to start the seed node. It will automatically start multiple seed nodes from ports starting from 5000. It will ask for the number of seed nodes to start. (You can change this if the port is busy on your machine.)
2. Run the `peer.py` file every time you want to start a peer node. It will ask for the port number to connect to. You can enter any port number. (The IP address is hardcoded to localhost, but you can change it in the code. In demo mode, you can easily run it on a different machine. However, the Seed or Peer class is not hardcoded to localhost—it can run on any IP and on any machine.)

### Method 2

1. Run the seed node manually by running the `seed.py` file. You must clear the `outputfile.log` file and `config.txt` before running the first seed node.
2. Run the peer node manually by running the `peer.py` file.

Both will ask for the port number to connect to, and you can enter any port number. (IP address is hardcoded to localhost, but you can change it in the code. In demo mode, you can easily run it on a different machine. However, the Seed or Peer class is not hardcoded to localhost—it can run on any IP and on any machine.)

## Usage

To start a seed node, run the `seed.py` file and enter the port to connect to when prompted:

```bash
python seed.py
```
To start a peer node, run the peer.py file and enter the port to connect to when prompted:
```bash
python peer.py
```
# Structure

The structure in terms of thread/code is as follows:

> **NOTE:** If these images are not visible, please check the extras folder in the repository.

### Structure of the Seed Node
![Seed Node Structure](images/seed.png)

### Structure of the Peer Node
![Peer Node Structure](images/peer.png)

---

# Code Explanation

## `seed.py`

The `seed.py` file contains the `Seed` class, which is responsible for handling the seed node in the network. The seed node maintains a list of active peers and provides this list to any peer that requests it.

### The `Seed` class has the following methods:

- `__init__(self, port=12345, ip='localhost')`  
  Initializes the seed node with the given IP address and port number and creates a new socket for the seed node.

- `config_entry(self)`  
  Checks if the seed node is already present in the `config.txt` file. If not, it adds the seed node to the file.

- `listen(self)`  
  Makes the seed node listen for incoming connections. When a peer node connects to the seed node, it starts a new thread to handle the peer node.

- `handle_peer(self, peer, addr)`  
  Handles communication with a peer node. It receives messages from the peer node and responds accordingly.

---

## `peer.py`

The `peer.py` script is responsible for managing the peer-to-peer network. It starts with the `self.start` function, which initiates two threads:

### **Listening Thread**
This thread is responsible for listening to other peer nodes. When a connection is established, it starts a new thread to handle the communication with the connected peer node by calling the `handle_peer` function.

### **Seed Connection Thread**
This thread is responsible for connecting to the seed nodes using `connect_to_seeds`. After that, it retrieves the peer list from each connected seed node (handled in `handle_seeds`). After retrieving the peer lists, it performs a union operation to create a comprehensive list of available peers in the network. Then, it calls `connect_to_peers` to connect to the peers.

---

### `connect_to_peers` Function
This function is responsible for establishing connections with other peers in the network. It performs the following steps:

1. Randomly selects up to **4 peers** from the available peer list.
2. Checks if each selected peer is not the same as the current peer. If it is, it skips to the next peer.
3. Creates a new socket and tries to connect to the peer.
4. If the connection is successful, it adds the socket to the list of connected peer sockets (`self.sockets_to_peers`).
5. Starts a new thread to handle communication with the connected peer by calling `handle_peer`.
6. If the connection fails, it prints an error message and continues with the next peer.

---

## `handle_peer` Function
The `handle_peer` function is responsible for managing communication with a connected peer. For each connected peer, it starts **three separate threads**:

### **1. Handle Messages Thread**
- Runs the `handle_messages` method.
- Listens for and processes incoming messages from the connected peer.
- Forwards gossip messages to other peers.
- Responds to liveness requests.

### **2. Liveness Test Thread**
- Runs the `liveness_test` method.
- Periodically sends a liveness request to the connected peer to check if it's still active.
- If no reply is received within a certain time, the peer is considered inactive and reported as `deadnode`.

### **3. Gossip Thread (Generate Messages)**
- Runs the `generate_messages` method.
- Periodically sends a gossip message to the connected peer.

---

These threads allow the peer to handle multiple tasks concurrently for each connected peer, ensuring **efficient communication and network management**.



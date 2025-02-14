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

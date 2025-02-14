import socket 
import threading
import logging
from datetime import datetime
from time import sleep
import hashlib
import random
import numpy as np
import os 
import platform

def add_padding(raw_data):
    return raw_data + ' '*(1024-len(raw_data))

def remove_padding(data):
    return data.strip()  

class Peer:
    def __init__(self,port:int,ip:str='localhost'):
        self.port=port
        self.ip=ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip,port))
        
        self.available_peers = []
        self.seeds=[]
        self.find_seeds()
        self.sockets_to_seed=[]
        self.sockets_to_peers=[]
        self.message_list={}
        self.alive_peers={} 
        self.addr_socket_map={}
        self.socket_addr_map={}
        self.peer_timestamps={}
    
    
    def start(self):
        # start initial threads
        connectSeedThread = threading.Thread(target=self.connect_to_seeds)
        connectSeedThread.start()
        listeningThread = threading.Thread(target=self.listen)
        listeningThread.start()
        
        connectSeedThread.join()
        listeningThread.join()

        


    def find_seeds(self):
        self.seeds = []
        with open('config.txt', 'r') as f:
            for line in f:
                seed_address=line.strip().split(':')
                self.seeds.append((seed_address[0],int(seed_address[1])))
        f.close()
        print(self.seeds)


    def connect_to_seeds(self):
        # Calculate the number of seeds to connect to
        num_seeds_to_connect = (len(self.seeds) // 2) + 1

        # Randomly select seeds
        selected_seeds = random.sample(self.seeds, num_seeds_to_connect)

    
        for seed in selected_seeds:
            try:
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                new_socket.connect((seed[0],seed[1]))
                self.sockets_to_seed.append(new_socket)#saving socket for later use
                self.handle_seed(new_socket)
                # threading.Thread(target=self.handle_seed,args=(new_socket,)).start()
            except Exception as e:
                print("seed not connected")
                print(e)
                continue
                
       
            
        # after getting the pl
        sleep(2)
        print("Available peerlist ",self.available_peers)
        logging.info(f'({self.ip}:{self.port}) received peer list: {self.available_peers} ')
        threading.Thread(target=self.connect_to_peers).start() 

    def listen(self):
        self.sock.listen(10)
        print("listening on  ",self.ip,self.port)
        while True:
            try:
                peer, addr = self.sock.accept()
                self.sockets_to_peers.append(peer)
                peer_thread = threading.Thread(target=self.handle_peer,args=(peer,))
                peer_thread.start()
                print("peer ",addr," connected")
            except Exception as e:
                print("An error occurred while listening/handling a peer: ", e)


    def generate_power_law_degrees(self, num_peers, gamma=2.5, min_degree=1,max_degree=8):
        x = np.arange(min_degree, max_degree + 1)
        probab = x ** (-gamma)
        probab /= probab.sum()

        # Generate degrees ensuring network connectivity
        degrees = np.random.choice(x, size = num_peers, p=probab)
        return list(degrees)
    
    def connect_to_peers(self):
        """Connect to peers using a power-law degree distrb"""
        if len(self.available_peers) == 0:
            return
        
        # Generate power-law degrees
        num_peers = len(self.available_peers)
        all_degrees = self.generate_power_law_degrees(num_peers)

        # Mapp peers to their degrees 
        peer_degree_map = dict(zip(self.available_peers, all_degrees))

        # Get assigned degrees for each peer
        my_addr = (self.ip, self.port)
        my_degree = peer_degree_map.get(my_addr, 4) # Default degree is 4

        # Sort peers based on their degrees
        sorted_peers = sorted(
            self.available_peers, 
            key=lambda p: peer_degree_map.get(p, 0),
            reverse=True)
        
        # Select peers to connect to
        peers_to_connect = []
        for peer in sorted_peers:
            if peer[0] == self.ip and peer[1] == self.port:
                continue
            if len(peers_to_connect) >= my_degree:
                break
            peers_to_connect.append(peer)

        # Connection
        for peer in peers_to_connect:
            try:
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((peer[0], peer[1]))
                self.sockets_to_peers.append(new_socket)
                threading.Thread(target=self.handle_peer, args=(new_socket,)).start()
            except Exception as e:
                print(f"An error occurred while connecting to peer {peer}: ", e)
                continue
    '''
    def connect_to_peers(self):
       
        # randomly select 4 peers
        peers_to_connect = random.sample(self.available_peers, min(len(self.available_peers),4))
        for peer in peers_to_connect:
            #  if same peer dont connect
            if(peer[0]==self.ip and peer[1]==self.port):
                continue
            try:
                # making sockets for each peer
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((peer[0],peer[1]))
                # print("New Peer connected")
                self.sockets_to_peers.append(new_socket)
                # make thread for each peer
                threading.Thread(target=self.handle_peer,args=(new_socket,)).start()
            except Exception as e:
                print(f"An error occurred while connecting to peer {peer}: ", e)
    '''

    def handle_seed(self,new_socket):
        try:
            response = new_socket.recv(1024)
            response= remove_padding(response)
            print(response)
            # register with seed
            message="register:{0}:{1}".format(self.ip,self.port)
            print(message)

            new_socket.send(message.encode())
            print("seeds connected")
            response = new_socket.recv(1024)
            
            response=remove_padding(response)
            print(response)
            # ask for peer list
            new_peers=[]
            new_socket.send("peer list".encode())
          
            # receive peer list
            while True:
                data = new_socket.recv(1024)
                data=remove_padding(data)
                decoded_data = data.decode()
                message = decoded_data.split(':')
                print("message is ",message)
                if message[0] == 'peer list':
                    # receive list of tuples
                    for i in range(2,len(message)):
                        adr=message[i].split(',')
                        print("adr: ",adr)
                        new_peers = [(adr[i],int(adr[i+1])) for i in range(0,len(adr),2)]
                        self.available_peers = list(set(self.available_peers) | set(new_peers))
                    break
        except Exception as e:
            print(f"An error occurred while handling the seed: ", e)
    
    def handle_peer(self, new_socket):

        try:
            # print("SOCKET ADDR MAP: ", self.socket_addr_map)
            # if already connections atmost 4 then dont connect
            if len(self.addr_socket_map) >= 4:
                # send message to peer that already connected to 4 peers
                new_socket.send(add_padding("PEER BUSY,already,connected to 4 peers").encode())
                # print("I AM BUSY")
                new_socket.close()
                return
            new_socket.send(add_padding("connected to peer:{0}:{1}").format(self.ip,self.port).encode())
            message="";
            while(message==""):
                data = new_socket.recv(1024)
                data=remove_padding(data)
                # print(data)
                message = data.decode().split(':')
                if message[0]=="connected to peer":
                    self.addr_socket_map[(message[1],int(message[2]))]=new_socket
                    self.socket_addr_map[new_socket]=(message[1],int(message[2]))
                    break
                elif message[0]=="PEER BUSY,already,connected to 4 peers":
                    # print("Peer is busy")
                    print("recieved:PEER BUSY,already,connected to 4 peers")
                    new_socket.close()
                    return
                new_socket.send(add_padding("connected to peer:{0}:{1}").format(self.ip,self.port).encode())
            sleep(1)
            threading.Thread(target=self.handle_messages, args=(new_socket,)).start()
            threading.Thread(target=self.liveness_test, args=(new_socket,)).start()
            threading.Thread(target=self.generate_messages, args=(new_socket,)).start()
            
            
        except Exception as e:
            print(f"An error occurred while handling the peer (handle_peer)")
    
    def handle_messages(self, new_socket):
        print("handling messages")
        
        while True:
            try:
                # print("trying")
                data = new_socket.recv(1024)
                data=remove_padding(data)
                # print(data)
                message = data.decode().split(':')
                if message[0]=="connected to peer":
                    self.addr_socket_map[(message[1],int(message[2]))]=new_socket
                    self.socket_addr_map[new_socket]=(message[1],int(message[2]))
                elif message[0]=="Liveness Request":
                    timestamp_of_sender = float(message[1])
                    
                    reply="Liveness Reply:{0}:{1}:{2}:{3}:{4}".format(timestamp_of_sender,self.socket_addr_map[new_socket][0],self.socket_addr_map[new_socket][1],self.ip,self.port)
                    new_socket.send(add_padding(reply).encode())
                elif message[0]=="Liveness Reply":
                    # Update timestamp of peer
                    # print(message)
                    self.peer_timestamps[self.socket_addr_map[new_socket]] = float(message[1])

                elif message[0]=="gossip message":
                    new_socket.send(add_padding(f'forwarding').encode())

                    # Check if message is in Message List
                    # print("HERE HAVE THIS+",message)
                    message_hash = hashlib.sha256(message[4].encode()).hexdigest()
                    print('gossip message recieved',message[4])
                    
                    if message_hash not in self.message_list:
                        self.message_list[message_hash] = True
                        logging.info(f'gossip message recieved on ({self.ip}:{self.port}) from peer with address {self.socket_addr_map[new_socket]}: {message[4]}')
                        print(f'gossip message recieved from peer with address {self.socket_addr_map[new_socket]}: {message[4]}')
                        # Forward message to all peers except the one it was received from
                        for socket in self.socket_addr_map.keys():
                            if socket != new_socket:
                                try:
                                    socket.send(add_padding(data.decode()).encode())
                                    socket.recv(1024)
                                except ConnectionResetError:
                                    print("Peer possibly disconnected")

                                    continue
                                except Exception as e:
                                    print(f"An error occurred while forwarding message: ", e)
                                    continue
                    

                    
            except Exception as e:
                print(f"An error occurred while handling messages: ", e)
                break

    '''
    def liveness_test(self, new_socket):
        fail_count = 0
        while True:
            sleep(13)
            timestamp = datetime.now().timestamp()
            try:
                request = "Liveness Request:{0}:{1}:{2}".format(timestamp, self.ip, self.port)
                new_socket.send(add_padding(request).encode())
                
               
                # print("Liveness Request sent to ", self.socket_addr_map[new_socket])
            except Exception as e:
                fail_count += 1
                print(f"An error occurred while sending liveness request {fail_count}",)
                if fail_count >=3:
                    dead_node_message = "Dead Node:{0}:{1}:{2}:{3}:{4}".format(addr[0], addr[1], timestamp, self.ip, self.port)
                    print(f"Peer {addr} is dead")
                    # Send dead_node_message to all seeds
                    for seed_socket in self.sockets_to_seed:
                        seed_socket.send(add_padding(dead_node_message).encode())
                    return
            
            
            # Check if peer is dead
            addr = self.socket_addr_map[new_socket]
            if addr in self.peer_timestamps:
                if(timestamp - self.peer_timestamps[addr] ==0):
                    fail_count = 0

    '''                

    # Fail count + ping update 
    def liveness_test(self, new_socket):
        fail_count = 0
        peer_addr = self.socket_addr_map[new_socket]

        while True:
            sleep(13)
            timestamp = datetime.now().timestamp()

            try:
                test_message = add_padding(f"Liveness Request:{timestamp}:{self.ip}:{self.port}")
                new_socket.send(test_message.encode())
                fail_count = 0
                
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                fail_count += 1
                logging.warning(f"({self.ip}:{self.port}) - Connection test failed for peer {peer_addr}, attempt {fail_count}: {str(e)}")

            if fail_count >= 3:
                # Clear logging format for better readability
                logging.info(f"({self.ip}:{self.port}) - Peer {peer_addr} declared dead after {fail_count} failed connection attempts")
                logging.info(f"({self.ip}:{self.port}) - Sending dead node notification for peer {peer_addr} to seeds")
                
                dead_node_message = add_padding(f"Dead Node:{peer_addr[0]}:{peer_addr[1]}:{timestamp}:{self.ip}:{self.port}")
                
                # Notify seeds
                seeds_notified = 0
                for seed_socket in self.sockets_to_seed:
                    try:
                        seed_socket.send(dead_node_message.encode())
                        seeds_notified += 1
                    except Exception as e:
                        logging.error(f"({self.ip}:{self.port}) - Failed to notify seed about dead peer {peer_addr}: {e}")
                
                logging.info(f"({self.ip}:{self.port}) - Successfully notified {seeds_notified} seeds about dead peer {peer_addr}")
                logging.info(f"({self.ip}:{self.port}) - Removing dead peer {peer_addr} from local data structures")
                
                # Cleanup
                if peer_addr in self.addr_socket_map:
                    del self.addr_socket_map[peer_addr]
                if new_socket in self.socket_addr_map:
                    del self.socket_addr_map[new_socket]
                if peer_addr in self.peer_timestamps:
                    del self.peer_timestamps[peer_addr]
                
                try:
                    new_socket.close()
                except Exception as e:
                    logging.error(f"({self.ip}:{self.port}) - Error closing socket for dead peer {peer_addr}: {e}")
                return

    
    def generate_messages(self, new_socket):
   
        for i in range(10):
            
            try:
                timestamp = datetime.now().timestamp()
                generated_message=f'message {1+i}'
                message = "gossip message:{0}:{1}:{2}:{3}".format(timestamp, self.ip, self.port,generated_message)
          
                new_socket.send(add_padding(message).encode())
                

                print("sent gossip message")
            except Exception as e:
                print(f"error in sending gossips messages to one node")
                break
            sleep(5)
            
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='outputfile.log', format='%(asctime)s:%(message)s')

    port=int(input('Enter port to connect to: '))
    peer = Peer(port=port)
    peer.start()

    # port=int(input('Enter port to connect to: '))
    # ip=input('Enter ip to connect to: ')
    # peer = Peer(port,ip)
    # peer.listen()

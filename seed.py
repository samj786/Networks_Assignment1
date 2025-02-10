# seed

import socket 
import threading
import logging

class Seed:
    def __init__(self,port=12345,ip='localhost'):
      
        self.ip=ip
        self.port=port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip,self.port))
        self.peerlist = []
        # add seed entry to config file
        self.config_entry()
        logging.info(f'seed with address {self.ip}:{self.port} started')
        
    def config_entry(self):
        # cheack if already present
        with open('config.txt', 'r') as f:
            for line in f:
                seed_address=line.strip().split(':')
                if seed_address[0] == self.ip and seed_address[1] == str(self.port):
                    return
        with open('config.txt', 'a') as f:
            f.write('{0}:{1}\n'.format(self.ip,self.port))
        f.close()

    def listen(self):
        self.sock.listen(10)
        print("listening on  ",self.ip,self.port)
        while True:
            try:
                peer, addr = self.sock.accept()
                peer_thread = threading.Thread(target=self.handle_peer,args=(peer,addr))
                peer_thread.start()
                print("peer ",addr," connected")
            except Exception as e:
                print(f"An error occurred while listening: ", e)
    def close_dead_peer(self,peer,addr):
        if(addr not in self.peerlist):
            peer.close()
            print("peer should be dead with address",addr)
            return

    def handle_peer(self, peer, addr):
        peer_ip_port = "";
        try:
            peer.send('welcome connected to seed with address {0}:{1}'.format(self.ip, self.port).encode())
            while True:
                data = peer.recv(1024)
                decoded_data = data.decode()
                if(decoded_data == ''):
                    continue
                print("received data from ", addr, ": ", decoded_data)
                message = decoded_data.split(':')
                print("message is ", message)
                if message[0] == 'peer list':
                    print("sending peer list")
                    list_of_peers = ""
                    for i in self.peerlist:
                        list_of_peers = list_of_peers + ":" + i[0] + "," + str(i[1])
                    data_to_send = "peer list" + ":" + list_of_peers
                    peer.send(data_to_send.encode())
                    print("peer list sent")
                    print("peer list is ", list_of_peers)
                if message[0] == 'register':
                    print("registering peer")
                    peer_ip_port=(message[1],int(message[2]))
                    self.peerlist.append((message[1], int(message[2])))
                    peer.send('registered successfully'.encode())
                    print("peer registered successfully")
                    logging.info(f'{message[1]}:{message[2]} registered to seed with address {self.ip}:{self.port}')
                    
                if message[0] == 'Dead Node':
                    address_of_dead_node = (message[1], int(message[2]))
                    print("dead node ", address_of_dead_node, " removed from peer list")
                    logging.info(f'dead node request recieved {address_of_dead_node} from peer with address {peer_ip_port[0]}:{peer_ip_port[1]} to seed {self.ip}:{self.port}')
                    
                    if(address_of_dead_node in self.peerlist):
                        self.peerlist.remove(address_of_dead_node)
                        logging.info(f'dead node {address_of_dead_node} removed from peer list of seed {self.ip}:{self.port}\n')
                    
        except Exception as e:
            print(f"An error occurred while handling the peer: ", e)
            
            
                



    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,filename='outputfile.log',format='%(asctime)s:%(message)s')
    port=int(input('Enter port to connect to: '))
    seed = Seed(port=port)
    seed.listen()
    print(seed.ip)

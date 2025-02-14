import threading
from seed import Seed 
import logging
num_seeds = int(input("Enter the number of seeds to spawn: "))
seed_list = []
# clear the config file
open('config.txt', 'w').close()
open('outputfile.log', 'w').close()
logging.basicConfig(level=logging.INFO,filename='outputfile.log',format='%(asctime)s:%(message)s')


threads = []
for i in range(num_seeds):
    seed_port = 6000 + i  # Assign a unique port for each seed
    seed = Seed(port=seed_port)  
    seed_list.append(seed)
    seedThread = threading.Thread(target=seed.listen) # Start the seed in a new thread
    seedThread.start()
    threads.append(seedThread)
    
for thread in threads:
    thread.join()  # Wait for all threads to finish

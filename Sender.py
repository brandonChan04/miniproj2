from socket import *
import random
import time

# Sender Class
class Sender:
    def __init__(self, receiver_ip, receiver_port, MSS=10, loss_prob=0.1, corruption_prob=0.1):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port

        # MSS defines the max. segment size of a packet
        self.MSS = MSS
        
        # We use SOCK.DGRAM (UDP) because TCP already implements RDT, pipelining, etc
        self.socket = socket(AF_INET, SOCK_DGRAM)

        self.socket.settimeout(1)  # Set a timeout for ACKs

        self.base = 0
        self.next_seq_num = 0

        # Using AIMD, window size begins at 1 MSS
        self.window_size = 1

        self.data_buffer = []
        self.loss_prob = loss_prob
        self.corruption_prob = corruption_prob

    def send(self, data):
        # create a buffer on the sending side, containing partitioned data
        # each parition should be at most MSS chars
        data_buffer = [data[i:i + self.MSS] for i in range(0, len(data), self.MSS)]

        print(data_buffer)
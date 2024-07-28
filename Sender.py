from socket import *
import random
import time
from TCPSegment import TCPSegment
from utils import *

# Sender Class
class Sender:
    def __init__(self, receiver_ip, receiver_port=2000, MSS=10, loss_prob=0.1, corruption_prob=0.1):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port

        # MSS defines the max. segment size (in chars)
        self.MSS = MSS
        
        # We use SOCK.DGRAM (UDP) because TCP already implements RDT, pipelining, etc
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', 0)) # Bind to any available port
        self.source_port = self.socket.getsockname()[1] # Get the dynamically assigned source port

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

        # assume connection is established and receiver is listening on port self.receiver_port
        data_length = len(data_buffer)
        while self.base < data_length:
            # Send segments in the window
            while self.next_seq_num < self.base + self.window_size and self.next_seq_num < data_length:
                segment_data = data_buffer[self.next_seq_num]
                segment = TCPSegment(
                    sourcePort=self.source_port,
                    destPort=self.receiver_port,
                    sequenceNum=self.next_seq_num,
                    ACKBit=False,
                    ACKNum=None,
                    SYNBit=False,
                    FINBit=False,
                    rwnd=0,
                    data=segment_data
                )
                
                # Encode segment
                encoded_segment = encode_segment(segment)
                # send it
                self.socket.sendto(encoded_segment, (self.receiver_ip, self.receiver_port))        
                self.next_seq_num += 1

                # Wait for ACKs and adjust window
                try:
                    ack_segment_data, _ = self.socket.recvfrom(1024)
                    ack_segment = decode_segment(ack_segment_data)

                    if ack_segment.ACKBit and ack_segment.ACKNum is not None:
                        # if we receive an ACK, 
                        self.base = max(self.base, ack_segment.ACKNum + 1)

                        # Adjust window size based on AIMD (Additive Increase Multiplicative Decrease)
                        self.window_size += 1  # Additive increase
                except timeout:
                    # Timeout occurred, handle retransmission
                    self.window_size = max(1, self.window_size // 2)  # Multiplicative decrease
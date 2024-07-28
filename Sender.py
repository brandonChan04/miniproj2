from socket import *
import random
import time
from Segment import Segment
from utils import *
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

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

        self.socket.settimeout(1)  # Set a timeout for ACKs-

        self.data_buffer = []
        self.loss_prob = loss_prob
        self.corruption_prob = corruption_prob
        logging.debug(f"Created a Sender to destination ({receiver_ip} {receiver_port})")

    def send(self, data):
        # create a buffer on the sending side, containing partitioned data
        # each partition should be at most MSS chars
        data_buffer = [data[i:i + self.MSS] for i in range(0, len(data), self.MSS)]
        logging.debug(f"Sending string of length {len(data)}, split into {len(data_buffer)} segments")
        base = 0
        window_size = 1

        # next_seq_num is the
        next_seq_num = 0

        # Track which packets have been ACKed
        ack_received = [False]*len(data_buffer)
        # print(ack_received)

        next_expected_ACK = next_seq_num

        # assume connection is established and receiver is listening on port self.receiver_port
        while base < len(data_buffer):
            # use GoBackN protocol
            # Create a window of items to be sent. Construct Segments from these items

            # Send the items all at once. Wait for ACK, or timeout.
            # If given an in-order ACK, pop that element from the data_buffer
            # If given a duplicate ACK, ignore it

            # If timeout, use a multiplicative decrease to cut window size in half.
            # Construct a new winddow of items to be sent, from the timeout packet
            # onwards

            # If all packets are sent successfully, use an additive increase to increase
            # window_size by 1
            # Use GoBackN protocol

            # Create a window of items to be sent. Construct Segments from these items
            window = data_buffer[base:base+window_size]
            logging.debug(f"Created window {window}")

            idx_of_last_packet = min(base + window_size-1, len(data_buffer)-1)

            sending_packets = [
                Segment(
                    sourcePort=self.source_port,
                    destPort=self.receiver_port,
                    sequenceNum=next_seq_num + i,
                    ACKBit=False,
                    ACKNum=None,
                    SYNBit=False,
                    FINBit=False,
                    rwnd=0,
                    data=data
                )
                for i, data in enumerate(window)
            ]

            # Send all these packets
            # logging.debug(f"Sending a batch of {len(sending_packets)} segments")
            for p in sending_packets:
                encoded = encode_segment(p)
                self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port))
                # p.print_segment()
                logging.debug(f"Sent packet with seq # {p.sequenceNum}")

            # Should listen for ACKs

            # Upon receiving an ACK, we verify if the ACKNum is that of the next expected
            # ACK. If so, we can slide the window (base += 1 and next_seq_num += 1).
            # If the ACKNum is not that of the next expeced ACK, we ignore it.

            # If all the packets in sending_packets have been ACKed, then we continue to the
            # next iteration of the loop, and increase window size by 1

            # If a time out occurs, we cut window size in half. We would set base to be
            # the index of the timeout packet, and proceed to the next iteration of the loop
            try:
                all_acked = False
                while not all_acked:
                    # ack_packet, _ = self.socket.recvfrom(1024)
                    # ack_segment = decode_segment(ack_packet)

                    # Temporary: simulate reception of ACKs
                    if next_seq_num == 0:
                        ack_segment = Segment(
                            sourcePort=self.source_port,
                            destPort=self.receiver_port,
                            sequenceNum=next_seq_num,
                            ACKBit=True,
                            ACKNum=next_seq_num,
                            SYNBit=False,
                            FINBit=False,
                            rwnd=0,
                            data=data
                        )
                    
                    else:
                        ack_packet, _ = self.socket.recvfrom(1024)
                        ack_segment = decode_segment(ack_packet)

                    if ack_segment.ACKBit and ack_segment.ACKNum is not None:
                        logging.debug(f"Received ACK for segment number {ack_segment.ACKNum}")
                        ack_num = ack_segment.ACKNum

                        if ack_num == next_expected_ACK:
                            # base += 1
                            # next_expected_ACK += 1
                            # next_seq_num += 1
                            ack_received[ack_num] = True
                            base += 1
                            next_expected_ACK += 1
                            next_seq_num += 1

                        # logging.debug(f"Checkintg received {idx_of_last_packet}")
                        if ack_received[idx_of_last_packet]:
                            all_acked = True
                            window_size += 1

            except timeout:
                window_size = max(1, window_size // 2)
                logging.debug(f"Timeout occurred, setting window size to {window_size}")


    # def send(self, data):
    #     # create a buffer on the sending side, containing partitioned data
    #     # each parition should be at most MSS chars
    #     data_buffer = [data[i:i + self.MSS] for i in range(0, len(data), self.MSS)]
    #     logging.debug(f"Sending string of length {len(data)}, split into {len(data_buffer)} segments")
    #     base = 0
    #     window_size = 1

    #     # next_seq_num is the
    #     next_seq_num = 0

    #     # Track which packets have been ACKed
    #     ack_received = [False]*len(data_buffer)

    #     next_expected_ACK = next_seq_num

    #     # assume connection is established and receiver is listening on port self.receiver_port
    #     while base < len(data_buffer):
    #         # use GoBackN protocol
    #         # Create a window of items to be sent. Construct Segments from these items

    #         # Send the items all at once. Wait for ACK, or timeout.
    #         # If given an in-order ACK, pop that element from the data_buffer
    #         # If given a duplicate ACK, ignore it

    #         # If timeout, use a multiplicative decrease to cut window size in half.
    #         # Construct a new winddow of items to be sent, from the timeout packet
    #         # onwards

    #         # If all packets are sent successfully, use an additive increase to increase
    #         # window_size by 1
    #         window = data_buffer[base:base+window_size]

            
    #         sending_packets = [
    #             Segment(
    #                 sourcePort=self.source_port,
    #                 destPort=self.receiver_port,
    #                 sequenceNum=next_seq_num+i,
    #                 ACKBit=False,
    #                 ACKNum=None,
    #                 SYNBit=False,
    #                 FINBit=False,
    #                 rwnd=0,
    #                 data=data
    #             )
    #             for i, data in enumerate(window)
    #         ]

    #         # Send all these packets at once
    #         for p in sending_packets:
    #             encoded = encode_segment(p)
    #             self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port))
    #             logging.debug(f"Sent packet with seq # {p.sequenceNum}")

    #         # Wait for ACKs, or timeout.
    #         all_received = False
    #         try:
    #             while not all_received:
    #                 ack_packet, _ = self.socket.recvfrom(1024)  # buffer size is 1024 bytes
    #                 ack_segment = decode_segment(ack_packet)
                    
    #                 if ack_segment.ACKBit and ack_segment.ACKNum is not None:
    #                     logging.debug(f"Received ACK for segment number {ack_segment.ACKNum}")
    #                     ack_num = ack_segment.ACKNum
    #                     if ack_num==next_expected_ACK:
    #                         ack_received[ack_num] = True
    #                         next_expected_ACK += 1

    #                         # Slide window forward
    #                         base += 1
    #                         next_seq_num += 1

    #                         if ack_received[base]

                            

    #         except timeout:
    #             # Timeout happened, apply multiplicative decrease, which halves the window size
    #             window_size = max(1, window_size // 2)

    #         # If all packets are ACKed successfully, use an additive increase to increase window_size by 1
    #         if base == next_seq_num + len(sending_packets):
    #             window_size += 1
    #             next_seq_num = base
            
















    #         # # Send segments in the window
    #         # # maintain a list of segments to be resent
    #         # while next_seq_num < base + self.window_size and next_seq_num < data_length:
    #         #     segment_data = data_buffer[next_seq_num]
    #         #     segment = TCPSegment(
    #         #         sourcePort=self.source_port,
    #         #         destPort=self.receiver_port,
    #         #         sequenceNum=next_seq_num,
    #         #         ACKBit=False,
    #         #         ACKNum=None,
    #         #         SYNBit=False,
    #         #         FINBit=False,
    #         #         rwnd=0,
    #         #         data=segment_data
    #         #     )
                
    #         #     # Encode segment
    #         #     encoded_segment = encode_segment(segment)
    #         #     self.socket.sendto(encoded_segment, (self.receiver_ip, self.receiver_port))       
    #         #     print(f"Sent seq number {next_seq_num}") 
    #         #     next_seq_num += 1

    #         #     # Wait for ACKs and adjust window
    #         #     try:
    #         #         ack_segment_data, _ = self.socket.recvfrom(1024)
    #         #         ack_segment = decode_segment(ack_segment_data)

    #         #         if ack_segment.ACKBit and ack_segment.ACKNum is not None:
    #         #             # if we receive an ACK
    #         #             last_ACKed = ack_segment.ACKNum

    #         #             # Adjust window size based on AIMD (Additive Increase Multiplicative Decrease)
    #         #             self.window_size += 1  # Additive increase

    #         #     except timeout:
    #         #         # Timeout occurred, handle retransmission
    #         #         self.window_size = max(1, self.window_size // 2)  # Multiplicative decrease
    #         #         next_seq_num = base

    #         #         print("retransmitting")

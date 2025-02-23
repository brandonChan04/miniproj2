from socket import *
import random
from Segment import Segment
from utils import *
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# UNCOMMENT THIS LINE TO ONLY SEE PACKET SEND INFO
# logging.getLogger().setLevel(logging.INFO)

# Sender Class
class Sender:
    def __init__(self, receiver_ip, receiver_port=2000, MSS=10, loss_prob=0.1, corruption_prob=0.1, buffer_size=5):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port

        # MSS defines the max. segment size (in chars)
        self.MSS = MSS
        
        self.buffer_size=buffer_size

        # We use SOCK.DGRAM (UDP) because TCP already implements RDT, pipelining, etc
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', 0)) # Bind to any available port
        self.source_port = self.socket.getsockname()[1] # Get the dynamically assigned source port

        self.socket.settimeout(1)  # Set a timeout for ACKs-

        self.data_buffer = []
        self.loss_prob = loss_prob
        self.corruption_prob = corruption_prob
        logging.debug(f"Created a Sender to destination ({receiver_ip} {receiver_port})")

        self.sequenceNum = 0

    def establish_connection(self):
        # Establish connection with receiver before sending
        logging.debug("Attempting to establish connection, sending SYN")
        SYN_Segment = Segment(
            sourcePort=self.source_port,
            destPort=self.receiver_port,
            sequenceNum=self.sequenceNum,
            ACKBit=False,
            ACKNum=None,
            SYNBit=True,
            FINBit=False,
            rwnd=self.buffer_size,
            data=None
        )

        encoded = encode_segment(SYN_Segment)
        self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port))
        logging.info(f"Sent a packet:\n{SYN_Segment.to_string()}")

        SYN_ACKed = False
        while not SYN_ACKed:
            try:
                ack_packet, _ = self.socket.recvfrom(1024)
                ack_segment = decode_segment(ack_packet)
                # ascertain it is a SYNACK
                if not (ack_segment.SYNBit and ack_segment.ACKBit):
                    logging.debug("Received garb response to SYN")
                    continue

                if ack_segment.ACKNum == self.sequenceNum+1:
                    logging.debug("Reveiced SYNACK")
                    SYN_ACKed = True
                    self.sequenceNum += 1      
                    receiverSeqNum = ack_segment.sequenceNum

                else:
                    logging.debug("ACKed a garb sequence number")              
            
            except timeout:
                SYN_Segment = Segment(
                    sourcePort=self.source_port,
                    destPort=self.receiver_port,
                    sequenceNum=self.sequenceNum,
                    ACKBit=False,
                    ACKNum=None,
                    SYNBit=True,
                    FINBit=False,
                    rwnd=self.buffer_size,
                    data=None
                )

                encoded = encode_segment(SYN_Segment)
                self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port)) 
                logging.info(f"Sent a packet:\n{SYN_Segment.to_string()}")
                logging.debug("SYN Timed out. sending again.")

        # ACK the establishment 
        logging.debug("Connection established on sender side. sending ACK")
        ACK_Segment = Segment(
            sourcePort=self.source_port,
            destPort=self.receiver_port,
            sequenceNum=self.sequenceNum,
            ACKBit=True,
            ACKNum=receiverSeqNum+1,
            SYNBit=False,
            FINBit=False,
            rwnd=self.buffer_size,
            data=None
        )

        encoded = encode_segment(ACK_Segment)
        self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port))
        logging.info(f"Sent a packet:\n{ACK_Segment.to_string()}")

        self.sequenceNum = 0



    def send(self, data):
        self.establish_connection()
        # create a buffer on the sending side, containing partitioned data
        # each partition should be at most MSS chars
        data_buffer = [data[i:i + self.MSS] for i in range(0, len(data), self.MSS)]
        logging.debug(f"Sending string of length {len(data)}, split into {len(data_buffer)} segments")
        base = 0
        window_size = 1


        # Track which packets have been ACKed
        ack_received = [False]*len(data_buffer)
        # print(ack_received)

        next_expected_ACK = self.sequenceNum + 1

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
                    sequenceNum=self.sequenceNum + i,
                    ACKBit=False,
                    ACKNum=None,
                    SYNBit=False,
                    FINBit=False,
                    rwnd=self.buffer_size,
                    data=data
                )
                for i, data in enumerate(window)
            ]

            # Send all these packets
            # logging.debug(f"Sending a batch of {len(sending_packets)} segments")
            for p in sending_packets:
                encoded = encode_segment(p)

                # lose the packet with random prob.
                if random.random() >= self.loss_prob:
                    self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port))
                    logging.info(f"Sent a packet:\n{p.to_string()}")
                # p.print_segment()
                    logging.debug(f"Sent packet with seq # {p.sequenceNum}")

                else:
                    logging.debug(f"Packet with sequence # {p.sequenceNum} was LOST!")

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
                    ack_packet, _ = self.socket.recvfrom(1024)
                    ack_segment = decode_segment(ack_packet)

                    # Artificially insert corruption
                    if not ack_segment.verify_checksum() or random.random() < self.corruption_prob:
                        logging.debug(f"Detected corruption in incoming packet, discarding")
                        continue

                    # # Temporary: simulate reception of ACKs
                    # if next_seq_num == 0:
                        # ack_segment = Segment(
                        #     sourcePort=self.source_port,
                        #     destPort=self.receiver_port,
                        #     sequenceNum=next_seq_num,
                        #     ACKBit=True,
                        #     ACKNum=next_seq_num,
                        #     SYNBit=False,
                        #     FINBit=False,
                        #     rwnd=self.buffer_size,
                        #     data=data
                        # )
                    
                    # else:
                    #     ack_packet, _ = self.socket.recvfrom(1024)
                    #     ack_segment = decode_segment(ack_packet)

                    if ack_segment.ACKBit and ack_segment.ACKNum is not None:
                        logging.debug(f"Received ACK for segment number {ack_segment.ACKNum-1}")
                        ack_num = ack_segment.ACKNum

                        if ack_num >= next_expected_ACK:
                            # base += 1
                            # next_expected_ACK += 1
                            # next_seq_num += 1
                            

                            # Whenw e receive an ACK, the previous packet was successfully delivered
                            while next_expected_ACK <= ack_num:
                                ack_received[next_expected_ACK-1] = True
                                base += 1
                                next_expected_ACK += 1
                                self.sequenceNum += 1

                        # logging.debug(f"Checkintg received {idx_of_last_packet}")
                        if ack_received[idx_of_last_packet]:
                            all_acked = True
                            logging.debug(f"Increasing window size to the smaller of: {window_size + 1}, receiver_buffer: {ack_segment.rwnd}")
                            window_size = min(window_size+1, ack_segment.rwnd)

            except timeout:
                window_size = max(1, window_size // 2)
                logging.debug(f"Timeout occurred, setting window size to {window_size}")
        
        # Send a FIN bit
        FIN = Segment(
            sourcePort=self.source_port,
            destPort=self.receiver_port,
            sequenceNum=self.sequenceNum,
            ACKBit=False,
            ACKNum=None,
            SYNBit=False,
            FINBit=True,
            rwnd=self.buffer_size,
            data=None
        )
        encoded = encode_segment(FIN)
        self.socket.sendto(encoded, (self.receiver_ip, self.receiver_port))
        logging.info(f"Sent a packet:\n{FIN.to_string()}")
        logging.debug("Transfer finished, sending FIN")
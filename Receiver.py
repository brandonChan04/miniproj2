import logging
from socket import *
from Segment import Segment
from utils import *
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

class Receiver:
    def __init__(self, receiver_port=2000, MSS=10, loss_prob=0.1, corruption_prob=0.1):
        self.receiver_port = receiver_port
        self.MSS = MSS
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', receiver_port))
        self.loss_prob = loss_prob
        self.corruption_prob = corruption_prob

        self.expected_seq_num = 0
        self.received_data = []

        logging.debug(f"Receiver listening on port {receiver_port}")

    def receive(self):
        while True:
            # Loop to capture incoming Segments
            try:
                segment, sender_address = self.socket.recvfrom(1024)
                decoded_segment = decode_segment(segment)
                logging.debug(f"Received segment with seq # {decoded_segment.sequenceNum}")

                # Check for SYN
                if decoded_segment.SYNBit:
                    logging.debug("Received a SYN")
                    # send back a SYNACK and wait for ACK
                    SYNACK = Segment(
                        sourcePort=self.receiver_port,
                        destPort=decoded_segment.sourcePort,
                        sequenceNum=0,
                        ACKBit=True,
                        ACKNum=decoded_segment.sequenceNum+1,
                        SYNBit=True,
                        FINBit=False,
                        rwnd=0,
                        data=''
                    )
                    encoded = encode_segment(SYNACK)
                    self.socket.sendto(encoded, sender_address)
                    logging.debug("Sent SYNACK")

                    receivedACK = False
                    while not receivedACK:
                        segment, sender_address = self.socket.recvfrom(1024)
                        decoded_segment = decode_segment(segment)
                        if decoded_segment.ACKBit and decoded_segment.ACKNum==1:
                            logging.debug("Connection Established!")
                            receivedACK=True
                        
                        else:
                            logging.debug("Received garb while expecting ACK")
                    
                    continue

                # Simulate corruption
                if not decoded_segment.verify_checksum() or random.random() < self.corruption_prob:
                    logging.debug(f"Detected corruption in incoming packet with seq Number {decoded_segment.sequenceNum}")
                    continue

                #Check for checksum
                # The seq number which we intend to ACK
                ACKNum = -1
                if decoded_segment.sequenceNum == self.expected_seq_num:
                    #Check if segment is in the right order
                    self.received_data.append(decoded_segment.data)
                    self.expected_seq_num += 1
                    ACKNum = self.expected_seq_num
                    logging.debug(f"Segment {decoded_segment.sequenceNum} is correctly received and ACKed")
                else:
                    logging.debug(f"Segment {decoded_segment.sequenceNum} is out of order, expected {self.expected_seq_num}")

                    ACKNum = self.expected_seq_num if self.expected_seq_num != 0 else -1

                # Create ACK
                ack_segment = Segment(
                    sourcePort=self.receiver_port,
                    destPort=decoded_segment.sourcePort,
                    sequenceNum=0,
                    ACKBit=True,
                    ACKNum=ACKNum,
                    SYNBit=False,
                    FINBit=False,
                    rwnd=0,
                    data=''
                )
                encoded_ack = encode_segment(ack_segment)
                # Random chance of loss
                if random.random() >= self.loss_prob:
                    self.socket.sendto(encoded_ack, sender_address) # SEND ACK
                    logging.debug(f"Sent ACK for segment {self.expected_seq_num - 1}")

                else:
                    logging.debug(f"ACK for segment {self.expected_seq_num - 1} was randomly LOST")

            except KeyboardInterrupt:
                logging.info("Receiver stopped")
                break

        self.socket.close()

if __name__ == '__main__':
    receiver = Receiver(loss_prob=0.1)
    receiver.receive()
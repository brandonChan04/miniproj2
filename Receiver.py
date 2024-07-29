import logging
from socket import *
from Segment import Segment
from utils import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

class Receiver:
    def __init__(self, receiver_port=2000, MSS=10):
        self.receiver_port = receiver_port
        self.MSS = MSS
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', receiver_port))

        self.expected_seq_num = 0
        self.received_data = []

        logging.debug(f"Receiver listening on port {receiver_port}")

    def receive(self):
        while True:
            try:
                segment, sender_address = self.socket.recvfrom(1024)
                decoded_segment = decode_segment(segment)
                logging.debug(f"Received segment with seq # {decoded_segment.sequenceNum}")

                if decoded_segment.verify_checksum():
                    if decoded_segment.sequenceNum == self.expected_seq_num:
                        self.received_data.append(decoded_segment.data)
                        self.expected_seq_num += 1
                        logging.debug(f"Segment {decoded_segment.sequenceNum} is correctly received and ACKed")
                    else:
                        logging.debug(f"Segment {decoded_segment.sequenceNum} is out of order, expected {self.expected_seq_num}")

                    ack_segment = Segment(
                        sourcePort=self.receiver_port,
                        destPort=decoded_segment.sourcePort,
                        sequenceNum=0,
                        ACKBit=True,
                        ACKNum=self.expected_seq_num,
                        SYNBit=False,
                        FINBit=False,
                        rwnd=0,
                        data=''
                    )
                    encoded_ack = encode_segment(ack_segment)
                    self.socket.sendto(encoded_ack, sender_address)
                    logging.debug(f"Sent ACK for segment {self.expected_seq_num - 1}")

                else:
                    logging.debug(f"Received corrupted segment with seq # {decoded_segment.sequenceNum}")

            except KeyboardInterrupt:
                logging.info("Receiver stopped")
                break

        self.socket.close()
        logging.debug("Received data:")
        for data in self.received_data:
            logging.debug(data)

if __name__ == "__main__":
    receiver = Receiver()
    receiver.receive()

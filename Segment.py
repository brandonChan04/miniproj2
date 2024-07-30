import logging
from socket import *
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Segment Class
# Source port #
# Destination port #
# Sequence Number
# ACKBit: True indicates this TCP segment is an ACK
# ACKNumr: The sequence number of next expected byte, if this segment is an ACKBit
# SYNbit: for connection management
# FINbit: for closing a connection
# rwnd: The amount of space the receiver has available
# Data payload
class Segment:
    def __init__(self, sourcePort, destPort, sequenceNum, ACKBit, ACKNum,
                 SYNBit, FINBit, rwnd, data):
        self.sourcePort = sourcePort
        self.destPort = destPort
        self.sequenceNum = sequenceNum
        self.ACKBit = ACKBit
        self.ACKNum = ACKNum
        self.SYNBit = SYNBit
        self.FINBit = FINBit
        self.rwnd = rwnd
        self.data = data

        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        checksum = 0

        header_fields = [
            self.sourcePort,
            self.destPort,
            self.sequenceNum,
            self.ACKBit,
            self.ACKNum,
            self.SYNBit,
            self.FINBit,
            self.rwnd
        ]

        for item in header_fields:
            if not item is None:
                checksum += int(item)
        

        # convert all chars in the 'data' string to their ASCII encoding
        if not self.data is None:
            for c in self.data:
                checksum += ord(c)
                
        return checksum
    

    def verify_checksum(self):
        computed_sum = self.compute_checksum()
        return computed_sum == self.checksum
    
    def print_segment(self):
        # for debugging purposes, print the contents of the segment
        print("Displaying segment information:")
        print(f'sourcePort: {self.sourcePort}')
        print(f'destPort: {self.destPort}')
        print(f'sequenceNum: {self.sequenceNum}')
        print(f'ACKBit: {self.ACKBit}')
        print(f'ACKNum: {self.ACKNum}')
        print(f'SYNBit: {self.SYNBit}')
        print(f'FINBit: {self.FINBit}')
        print(f'rwnd: {self.rwnd}')
        print(f'data: {self.data}')
        print(f'checksum: {self.checksum}')
    
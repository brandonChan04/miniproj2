import logging
from socket import *

# TCP Segment Class
# Source port #
# Destination port #
# Sequence Number
# ACKBit: True indicates this TCP segment is an ACK
# ACKNumr: The sequence number of next expected byte, if this segment is an ACKBit
# SYNbit: for connection management
# FINbit: for closing a connection
# rwnd: The amount of space the receiver has available
# Data payload
class TCPSegment:
    def __init__(self, sourcePort, destPort, sequenceNum, ACKBit, ACKNum,
                 SYNBit, FINBit, rwnd, data):
        self.sourcePort = sourcePort
        self.destPort = destPort
        self.sequenceNum = sequenceNum
        self.ACKBit = ACKBit
        self.ACKNum = ACKNum
        self.SYNBit = SYNBit
        self.FINbit = FINBit
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
            self.FINbit,
            self.rwnd
        ]

        for item in header_fields:
            if not item is None:
                checksum += int(item)
        

        # convert all chars in the 'data' string to their ASCII encoding
        for c in self.data:
            checksum += ord(c)
        
        return checksum
    

    def verify_checksum(self):
        computed_sum = self.compute_checksum()
        return computed_sum == self.checksum
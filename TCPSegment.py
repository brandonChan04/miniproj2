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
                 SYNbit, FINbit, rwnd, data):
        self.sourcePort = sourcePort
        self.destPort = destPort
        self.sequenceNum = sequenceNum
        self.ACKBit = ACKBit
        self.ACKNum = ACKNum

        self.SYNBit = SYNbit
        self.FINbit = FINbit

        self.rwnd = rwnd

        self.data = data

        
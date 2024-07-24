import logging
from socket import *

class TCPSegment:
    def __init__(self, sourcePort, destPort, sequenceNum, ACKBit, ACKNum):
         self.sourcePort = sourcePort
         self.destPort = destPort
         self.sequenceNum = sequenceNum
         self.ACKBit = ACKBit
         self.ACKNum = ACKNum

        
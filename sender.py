import socket
import struct
import time
import random

class Sender:
    ALPHA = 0.125
    BETA = 0.25
    estimatedRTT = 1
    sample_RTT = "TO BE DETERMINED"

    def calculate_timeout(self, sample_rtt):
        if self.estimated_rtt is None:
            self.estimated_rtt = sample_rtt
        else:
            self.estimated_rtt = (1 - self.ALPHA) * self.estimated_rtt + self.ALPHA * sample_rtt

        if self.dev_rtt is None:
            self.dev_rtt = sample_rtt / 2
        else:
            self.dev_rtt = (1 - self.BETA) * self.dev_rtt + self.BETA * abs(sample_rtt - self.estimated_rtt)

        timeout_interval = self.estimated_rtt + 4 * self.dev_rtt
        self.timeout = timeout_interval


    def __init__(self, address):
        self.address = address
        self.window_size = 0
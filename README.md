# Pipeline Protocol
We will use Selective Repeat for our pipeline protocol.

In selective repeat, the sender may have up to N un-acked packets in the pipeline at once. This N is the window size and can be adjusted dynamically when implementing congestion control. The receiver sends individual acknowledgements for each successfully received packet. The sender maintains a timer for each un-acked packet, and considers the packet lost if it has not received acknowledgement for that packet when the timer expires. Upon a packet being lost, the sender will retransmit the packet.

# Congestion Control Protocol
We will use AIMD as our congestion control protocol.

AIMD varies the congestion window (cwnd) depending on if congestion in the system. In AIMD, the cwnd will start at 1 MSS and increases by 1 MSS every RTT (round trip time). When loss is detected, we will cut cwnd in half to ease congestion and then keep increasing by 1 MSS per RTT from there.

The receiver will also maintain the size of its buffer. It will communicate this to the sender within its ACK packets, and the sender will adjust its sending window size accordingly. This guarantees that the receiver buffer will not overflow.

# Classes
We define the following classes for our project:

## TCPSegment Class:
This class defines a TCP packet.
- Source port #
- Destination port #
- Sequence Number
- ACKBit: `True` indicates this TCP segment is an ACK
- ACKNumber: The sequence number of next expected byte, if this segment is an ACKBit
<!-- - SYNbit: for connection management
- FINbit: for closing a connection -->
- MAX Receive Window Size: The amount of space the receiver has available
- Data payload

### ACK Class
This class inherits from the TCPSegment class. It contains an ACK of a previously received segment

## TCP Agent class
Parent class for sender and receiver. This class has functionality to send and recieve packets. It also implements timers for un-ACKed packets

## Sender Class
The sender class inherits from TCP Agent class as senders need to both send and receive data. The sender will send packets as well as dealing with timeouts and loss. In these events, the sender will resend packets. The sender will also be reponsible for changing window size depending on congestion. 

- We will need a queue for packets that need to be sent
- We will need a another queue for packets in the sending window

We will need to adjust the window size according to packet losses, and the value of MAX Receive Window SIze from receiver.

For each packet currently in the pipeline, we maintain a timer to check for loss.

## Receiver
The receiver will recieve packets and send ACKs 

For congestion control, the receiver should maintain the size of free buffer space. This is communicated to the sender in the ACK packets

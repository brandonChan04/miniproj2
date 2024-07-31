# Pipeline Protocol
We will use Go-Back N for our pipeline protocol

In Go-Back N, the sender may have up to N un-acked packets in the pipeline at once. This N is the window size and can be adjusted dynamically when implementing congestion control. The receiver sends cumulative ACKs instead of individual ACKs. We will not ACK packets when prior packets havn't arrived yet. For example, we won't ACK packet 3 before packet 2 has arrived. The sender maintains a timer for oldest un-acked packet, and considers the packet lost if it has not received acknowledgement for that packet when the timer expires. Upon a packet being lost, the sender will retransmit all un-acked packets.

# Congestion Control Protocol
We will use AIMD as our congestion control protocol.

AIMD varies the congestion window (cwnd) depending on if congestion in the system. In AIMD, the cwnd will start at 1 MSS and increases by 1 MSS every RTT (round trip time). When loss is detected, we will cut cwnd in half to ease congestion and then keep increasing by 1 MSS per RTT from there.

The receiver will also maintain the size of its buffer. It will communicate this to the sender within its ACK packets, and the sender will adjust its sending window size accordingly. This guarantees that the receiver buffer will not overflow.

# Classes
We define the following classes for our project:

## TCPSegment Class:
This class defines a TCP packet. It has the following fields.
- Source port #
- Destination port #
- Sequence Number
- ACKBit: `True` indicates this TCP segment is an ACK
- ACKNumber: The sequence number of next expected byte, if this segment is an ACKBit
- SYNbit: for connection management
- FINbit: for closing a connection
- MAX Receive Window Size: The amount of space the receiver has available
- Data payload
- Checksum: used to check for bitswitches and other erros during the transportation of the packet

Compute Checksum function:
We compute checksum by adding the ACII int values for each of the paramaters in the segment.

## Sender Class

The `Sender` class in the provided code implements a basic reliable data transfer protocol using the Go-Back-N ARQ (Automatic Repeat reQuest) mechanism and AIMD (Additive Increase Multiplicative Decrease) for congestion control over UDP. The sender is initialized with the receiver's IP address and port, a maximum segment size (MSS), and probabilities for packet loss and corruption simulation. A UDP socket is created and bound to any available port, and the sender's initial sequence number is set to 0.

The sender initiates a connection by sending a SYN segment to the receiver and waits for a SYN-ACK segment. Upon receiving the SYN-ACK, the sender sends an ACK segment, completing the three-way handshake. For data transmission, the data to be sent is divided into segments of size MSS and stored in a buffer. The sender maintains a window of unacknowledged segments and transmits them to the receiver. The window size is dynamically adjusted using AIMD: it starts at 1 MSS and increases by 1 MSS for each round-trip time (RTT) if no packet loss occurs. If a packet loss is detected (via timeout), the window size is halved.

The sender listens for ACK segments from the receiver. If a valid ACK is received, the sender slides the window forward, acknowledging the receipt of the corresponding data. If all segments within the current window are acknowledged, the window size is increased. If an ACK is not received within a specified timeout period, the sender reduces the window size by half and retransmits the unacknowledged segments starting from the base of the window.

After all data segments are successfully transmitted and acknowledged, the sender sends a FIN segment to indicate the end of the transmission. This class is designed to demonstrate the principles of reliable data transfer and congestion control in a simplified networking environment, providing a clear example of how these protocols can be implemented over an unreliable transport layer like UDP.

## Receiver

The `Receiver` class implements the receiving end of a reliable data transfer protocol using UDP. It listens for incoming segments, handles connection establishment through a three-way handshake, processes received data segments, and simulates both packet corruption and loss. 

When initialized, the `Receiver` class binds a UDP socket to the specified port and sets up parameters for segment size (MSS), packet loss probability, and packet corruption probability. The receiver listens for incoming segments in a loop and processes them based on the segment's flags (SYN, FIN, ACK).

During connection establishment, the receiver responds to a SYN segment with a SYN-ACK segment and waits for an ACK to confirm the connection. For data transmission, the receiver maintains the expected sequence number and accumulates received data segments in the correct order. If an out-of-order segment is received, it is discarded. The receiver acknowledges correctly received segments by sending back ACK segments.

To simulate network conditions, the receiver introduces random packet loss and corruption. If a segment is detected as corrupt or a random condition triggers loss, the segment is discarded. Otherwise, the receiver processes the segment and sends the appropriate acknowledgment. When a FIN segment is received, indicating the end of transmission, the receiver resets its state and prepares for a new connection.

The receiver class runs until interrupted, at which point it closes the socket and stops listening for incoming segments.

# Testing

We conducted testing through a Jupiter notebook test.ipynb 
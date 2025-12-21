# Computer Networks Protocol Simulations

A collection of implementations for reliable data transfer protocols and TCP congestion control algorithms, demonstrating fundamental concepts in computer networking.

## Project Overview

This repository contains Python implementations of key networking protocols studied in computer networks courses:

- **Reliable Data Transfer Protocols**: RDT 2.2 and RDT 3.0
- **TCP Congestion Control Algorithms**: TCP Tahoe and TCP Reno

## Features

### Reliable Data Transfer (RDT)

#### RDT 2.2 - Protocol with Bit Error Detection
- Stop-and-wait ARQ protocol
- Sequence numbers for packet ordering
- Checksum-based error detection
- ACK/NAK mechanism for reliability
- Simulates packet corruption over unreliable channels

#### RDT 3.0 - Protocol with Bit Errors and Packet Loss
- Extends RDT 2.2 with timeout mechanisms
- Handles packet loss and delays
- Retransmission on timeout
- Simulates realistic network conditions with:
  - Variable packet delays
  - Configurable packet loss rates
  - Bit-level corruption

### TCP Congestion Control

#### TCP Tahoe
- Slow start phase implementation
- Congestion avoidance phase
- Threshold-based algorithm switching
- Congestion window visualization
- Packet loss detection and recovery

#### TCP Reno
- Extends TCP Tahoe functionality
- Fast recovery mechanism
- Distinguishes between timeout and triple duplicate ACKs
- More efficient congestion window management
- Comparative performance analysis with Tahoe

## Visualizations

Both TCP implementations generate graphs showing:
- Congestion window size evolution over time
- RTT (Round Trip Time) progression
- Impact of packet loss events
- Threshold adjustments

## Installation

### Prerequisites
- Python 3.6 or higher
- Required Python packages:
  ```bash
  pip install -r requirements.txt
  ```

## Usage

### Running RDT Protocols

**RDT 2.2:**
```bash
python rdt/rdt2.2.py
```

**RDT 3.0:**
```bash
python rdt/rdt3.0.py
```

### Running TCP Congestion Control Simulations

**TCP Tahoe:**
```bash
python tcp/tahoe.py
```
Follow the prompts to:
- Enter total number of RTT rounds
- Set initial threshold value
- Choose random or manual loss event configuration

**TCP Reno:**
```bash
python tcp/reno.py
```
Similar prompts as Tahoe, with additional options for:
- Timeout loss events
- Triple duplicate ACK events

## Project Structure

```
.
├── README.md
├── requirements.txt
├── LICENSE
├── rdt/
│   ├── rdt2.2.py          # RDT 2.2 implementation
│   ├── rdt3.0.py          # RDT 3.0 implementation
│   └── sample_outputs/
│       ├── rdt_2.2_op.txt
│       └── rdt_3.0_op.txt
└── tcp/
    ├── tahoe.py           # TCP Tahoe implementation
    └── reno.py            # TCP Reno implementation
```

## Technical Details

### RDT Implementation
- **Channel Simulation**: Includes configurable bit error rates and corruption models
- **Packet Structure**: Sequence number, payload data, and checksum
- **State Machine**: Implements sender and receiver finite state machines
- **Error Detection**: Binary checksum calculation and validation

### TCP Implementation
- **Slow Start**: Exponential growth of congestion window
- **Congestion Avoidance**: Linear growth after threshold
- **Loss Detection**: Timeout and triple duplicate ACK mechanisms
- **Window Management**: Dynamic threshold adjustment based on network conditions

## Sample Outputs

The `sample_outputs` directory contains example execution logs demonstrating:
- Packet transmission sequences
- Error detection and recovery
- Retransmission events
- State transitions

## Learning Outcomes

This project demonstrates understanding of:
- Transport layer protocols
- Error detection and correction mechanisms
- Flow control and congestion control
- Network reliability principles
- Protocol state machines
- Performance analysis and visualization

## License

-This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for   details.
- Implemented as part of Computer Networks coursework
- Based on concepts from "Computer Networking: A Top-Down Approach" by Kurose and Ross
- Inspired by real-world TCP/IP protocol implementations

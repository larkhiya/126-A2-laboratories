import socket  # Import socket module for potential network communication
import struct  # Import struct module for packing/unpacking binary data
import pickle  # Import pickle module for serializing/deserializing Python objects
import json  # Import json module for encoding/decoding JSON data
import uuid

def get_mac_address():
    mac = uuid.getnode()
    mac_bytes = mac.to_bytes(6, byteorder='big') 
    return ':'.join(f'{b:02x}' for b in mac_bytes)


# Physical Layer: Responsible for transmitting and receiving raw binary data
class PhysicalLayer:
    def send(self, data):
        binary_data = struct.pack(f"{len(data)}s", data)  # Convert data to binary format
        print(f"Physical Layer: Transmitting raw bits: {binary_data}")
        return binary_data

    def receive(self, data):
        decoded_data = struct.unpack(f"{len(data)}s", data)[0]  # Decode binary data back to original format
        print(f"Physical Layer: Received raw bits: {decoded_data}")
        return decoded_data

# Data Link Layer: Adds MAC address and frames the data before sending
class DataLinkLayer:
    def send(self, data):
        mac_address = get_mac_address()
        # print("KANI" + mac_address)
        framed_data = json.dumps({"MAC": mac_address, "Payload": data.hex()}).encode('utf-8')  # Convert data to JSON format
        print(f"Data Link Layer: Framing data: {framed_data}")
        return PhysicalLayer().send(framed_data)  # Pass framed data to Physical Layer

    def receive(self, data):
        decoded_data = json.loads(PhysicalLayer().receive(data).decode('utf-8'))  # Decode received data from JSON
        print(f"Data Link Layer: Received frame: {decoded_data}")
        return bytes.fromhex(decoded_data["Payload"])  # Extract and convert payload back to bytes

# Network Layer: Adds an IP address and routes the data
class NetworkLayer:
    def send(self, data):
        ip_address = self.get_local_ip() # accessed IP address
        packet = json.dumps({"IP": ip_address, "Payload": data.hex()}).encode('utf-8')  # Create a packet with IP address
        print(f"Network Layer: Routing data: {packet}")
        return DataLinkLayer().send(packet)  # Pass packet to Data Link Layer

    def receive(self, data):
        decoded_data = json.loads(DataLinkLayer().receive(data).decode('utf-8'))  # Decode received packet
        print(f"Network Layer: Received packet: {decoded_data}")
        return bytes.fromhex(decoded_data["Payload"])  # Extract payload and convert to bytes
    
    def get_local_ip(self):
        """Retrieve the local network IP address."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Connect to an external server (Google DNS) but don't actually send data
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        finally:
            s.close()
        return ip_address

# Transport Layer: Ensures data integrity and maintains sequence
class TransportLayer:
    def send(self, data):
        sequence_number = 1  # Simulated sequence number for reliability
        packet = json.dumps({"SEQ": sequence_number, "Payload": data.hex()}).encode('utf-8')  # Create transport layer packet
        print(f"Transport Layer: Ensuring complete and accurate data: {packet}")
        return NetworkLayer().send(packet)  # Pass packet to Network Layer

    def receive(self, data):
        decoded_data = json.loads(NetworkLayer().receive(data).decode('utf-8'))  # Decode received transport packet
        print(f"Transport Layer: Received segment: {decoded_data}")
        return bytes.fromhex(decoded_data["Payload"])  # Extract payload and convert to bytes

# Session Layer: Manages communication sessions
class SessionLayer:
    def send(self, data):
        session_data = json.dumps({"Session": "Active", "Payload": data.hex()}).encode('utf-8')  # Create session data packet
        print(f"Session Layer: Managing session: {session_data}")
        return TransportLayer().send(session_data)  # Pass session data to Transport Layer

    def receive(self, data):
        decoded_data = json.loads(TransportLayer().receive(data).decode('utf-8'))  # Decode received session data
        print(f"Session Layer: Received session data: {decoded_data}")
        return bytes.fromhex(decoded_data["Payload"])  # Extract payload and convert to bytes

# Presentation Layer: Handles encoding and decoding of data
class PresentationLayer:
    def send(self, data):
        encoded_data = pickle.dumps(data)  # Serialize data into binary format
        print(f"Presentation Layer: Encoding data: {encoded_data.hex()}")
        return SessionLayer().send(encoded_data)  # Pass encoded data to Session Layer

    def receive(self, data):
        decoded_data = pickle.loads(SessionLayer().receive(data))  # Deserialize received data
        print(f"Presentation Layer: Decoded data: {decoded_data}")
        return decoded_data

# Application Layer: Simulates an HTTP-like request at the top level
class ApplicationLayer:
    def send(self, data):
        request = json.dumps({"Protocol": "HTTP", "Request": data}).encode('utf-8')  # Create an application request
        print(f"Application Layer: Sending HTTP-like request: {request}")
        return PresentationLayer().send(request)  # Pass request to Presentation Layer

    def receive(self, data):
        decoded_data = json.loads(PresentationLayer().receive(data).decode('utf-8'))  # Decode received application request
        print(f"Application Layer: Received HTTP-like request: {decoded_data}")
        return decoded_data["Request"]  # Extract and return the request data

# Example usage of the layered network simulation
app_layer = ApplicationLayer()
sent_data = app_layer.send("Hello, Network!")  # Send data through the network stack
received_data = app_layer.receive(sent_data)  # Receive and process the data
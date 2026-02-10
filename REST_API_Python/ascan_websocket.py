"""
A1580 A-Scan WebSocket Client
==============================

Standalone WebSocket client for receiving real-time A-scan data from A1580 devices.

This module can be copied directly into your project for easy integration.
No dependencies other than standard library and websocket-client.

Installation:
    pip install websocket-client

Basic Usage:
    from ascan_websocket import AScanWebSocketClient
    
    # Create client (use device's ascan_length!)
    client = AScanWebSocketClient(
        url="ws://192.168.200.18:80",
        ascan_length=2048
    )
    
    # Register callback to process data
    def on_data(packet):
        print(f"Received {len(packet['data'])} samples")
        print(f"Peak value: {max(packet['data'])}")
    
    client.on_data(on_data)
    
    # Connect and receive data
    client.connect()
    time.sleep(10)
    client.disconnect()

Author: A1580 Integration Examples
License: MIT
"""

import struct
import time
import threading
try:
    import websocket
except ImportError:
    print("ERROR: websocket-client library not found")
    print("Please install it with: pip install websocket-client")
    raise


class AScanWebSocketClient:
    """
    WebSocket client for receiving real-time A-scan data from the A1580 device.
    
    The device streams binary data packets over WebSocket. Each packet contains:
    - Header (28 bytes): Metadata including timing, packet info, and telemetry
    - Data: Int16 samples representing the A-scan waveform
    
    Packet Structure (matches firmware implementation):
    ┌─────────────────────────────────────────────────────────────┐
    │ HEADER (28 bytes)                                           │
    ├─────────────────────────────────────────────────────────────┤
    │ Magic bytes 'FtH1' (4 bytes)    - Packet start marker      │
    │ CTP coordinate (12 bytes)        - X,Y,Z coordinates       │
    │ Length fields (3 bytes)          - Packet length info       │
    │ Packet number (1 byte)           - Sequential counter       │
    │ Telemetry (3 bytes)              - Device status            │
    │ Flags (4 bytes)                  - Buffer status, A-scan #  │
    │ Reserved (2 bytes)               - Future use               │
    ├─────────────────────────────────────────────────────────────┤
    │ DATA (variable length)                                      │
    ├─────────────────────────────────────────────────────────────┤
    │ Int16 samples × ascan_length     - A-scan waveform data    │
    └─────────────────────────────────────────────────────────────┘
    
    CRITICAL: The ascan_length parameter MUST match the device configuration!
    Read it from the device first: GET /api/v1/ascan_length
    """
    
    def __init__(self, url, ascan_length=1024):
        """
        Initialize the WebSocket client.
        
        Parameters:
            url (str): WebSocket URL (e.g., "ws://192.168.200.18:80")
            ascan_length (int): Expected number of samples per A-scan
                               MUST match the ascan_length parameter set on device!
        
        Example:
            client = AScanWebSocketClient("ws://192.168.200.18:80", ascan_length=2048)
        """
        self.url = url
        self.ws = None
        self.ascan_length = ascan_length
        self.callbacks = []
        self.running = False
        self.receive_thread = None
        
        # Protocol constants - must match device firmware
        self.MAGIC_BYTES = b'FtH1'  # 0x46, 0x74, 0x48, 0x31
        self.HEADER_LENGTH = 28
        self.stream_buffer = bytearray()
        
        # Statistics for monitoring and diagnostics
        self.packets_received = 0
        self.bytes_received = 0
        self.parse_errors = 0
        
    def connect(self):
        """
        Connect to the WebSocket server.
        
        Establishes connection and starts receiving data in a background thread.
        Data packets are automatically parsed and passed to registered callbacks.
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            ConnectionRefusedError: If server is not responding
            TimeoutError: If connection times out
            
        Example:
            if client.connect():
                print("Connected successfully")
            else:
                print("Connection failed")
        """
        try:
            print(f"Connecting to WebSocket at {self.url}...")
            
            # Create WebSocket connection with subprotocol
            # timeout=5 means wait up to 5 seconds for connection
            self.ws = websocket.create_connection(
                self.url,
                subprotocols=["server-websocket"],
                timeout=5
            )
            
            print("✓ WebSocket connected successfully")
            self.running = True
            self.stream_buffer.clear()
            
            # Start background thread to receive data
            # daemon=True means thread will exit when main program exits
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            return True
            
        except ConnectionRefusedError:
            print("✗ Connection refused - WebSocket server not responding")
            print(f"  Check that device is streaming data on the specified port")
            return False
            
        except TimeoutError:
            print("✗ Connection timeout - device not responding")
            print(f"  Verify device IP and network connectivity")
            return False
            
        except Exception as e:
            print(f"✗ WebSocket connection failed: {str(e)}")
            return False
    
    def _receive_loop(self):
        """
        Background thread that continuously receives and processes data.
        
        This runs in a separate thread so it doesn't block your main program.
        Do not call this directly - it's started automatically by connect().
        """
        while self.running and self.ws:
            try:
                # Receive binary data from WebSocket
                # Each message may contain one or more complete packets
                data = self.ws.recv()
                
                if data:
                    self.bytes_received += len(data)
                    self._process_incoming_data(data)
                    
            except websocket.WebSocketConnectionClosedException:
                print("WebSocket connection closed by server")
                self.running = False
                break
                
            except Exception as e:
                if self.running:
                    print(f"Error receiving data: {str(e)}")
                    self.parse_errors += 1
                break
    
    def _process_incoming_data(self, data_block):
        """
        Process incoming binary data and extract complete packets.
        
        The device may send partial packets, so we buffer data until we have
        a complete packet with magic bytes and correct length.
        
        This implementation matches the JavaScript version in websocketClient.js
        
        Parameters:
            data_block (bytes): Raw binary data received from WebSocket
        """
        # Append new data to buffer
        self.stream_buffer.extend(data_block)
        
        # Calculate expected packet size
        data_size_bytes = 2 * self.ascan_length  # Int16 = 2 bytes per sample
        packet_size = self.HEADER_LENGTH + data_size_bytes
        
        # Process all complete packets in buffer
        while True:
            # Find magic bytes (packet start marker)
            start_index = self.stream_buffer.find(self.MAGIC_BYTES)
            
            if start_index < 0:
                # No magic bytes found
                # If buffer is getting large, keep only last packet worth of data
                if len(self.stream_buffer) > packet_size * 2:
                    self.stream_buffer = self.stream_buffer[-packet_size:]
                break
            
            # Remove any garbage data before magic bytes
            if start_index > 0:
                self.stream_buffer = self.stream_buffer[start_index:]
            
            # Check if we have a complete packet
            if len(self.stream_buffer) < packet_size:
                # Wait for more data
                break
            
            # Extract complete packet
            packet_data = bytes(self.stream_buffer[:packet_size])
            
            # Parse packet and notify callbacks
            try:
                packet = self._parse_packet(packet_data)
                if packet:
                    self.packets_received += 1
                    self._notify_callbacks(packet)
            except Exception as e:
                print(f"Parse error: {str(e)}")
                self.parse_errors += 1
            
            # Remove processed packet from buffer
            self.stream_buffer = self.stream_buffer[packet_size:]
    
    def _parse_packet(self, packet_data):
        """
        Parse a binary packet into a structured dictionary.
        
        Packet structure (28-byte header + data):
        Offset | Size | Type   | Field         | Description
        -------|------|--------|---------------|---------------------------
        0      | 4    | char[] | magic         | Magic bytes 'FtH1'
        4      | 12   | u32[3] | ctp           | CTP timing array
        16     | 2    | u16    | length_lo     | Length low word
        18     | 1    | u8     | length_hi     | Length high byte
        19     | 1    | u8     | packet_number | Sequential packet counter
        20     | 1    | u8     | telemetry_a   | Telemetry byte A
        21     | 1    | u8     | telemetry_b   | Telemetry byte B
        22     | 1    | u8     | telemetry_c   | Telemetry byte C
        23     | 1    | u8     | is_full       | Buffer full flag
        24     | 1    | u8     | buffer_fill   | Buffer fill level (0-255)
        25     | 1    | u8     | ascan_count   | Number of A-scans
        26     | 2    | u8[2]  | reserved      | Reserved for future use
        28     | var  | i16[]  | data          | Int16 sample array
        
        Parameters:
            packet_data (bytes): Raw binary packet data
            
        Returns:
            dict: Parsed packet with 'header' and 'data' fields, or None if invalid
        """
        if len(packet_data) < self.HEADER_LENGTH:
            return None
        
        # Parse header using struct module
        # Format string: '<' = little-endian, 'I' = uint32, 'H' = uint16, 'B' = uint8
        header_format = '<4s3IH2B6B2B'
        header_values = struct.unpack(header_format, packet_data[:self.HEADER_LENGTH])
        
        # Build header dictionary with meaningful names
        header = {
            'magic': header_values[0],           # Should be b'FtH1'
            'ctp': list(header_values[1:4]),     # CTP timing [uint32, uint32, uint32]
            'length_lo': header_values[4],       # Length low word
            'length_hi': header_values[5],       # Length high byte
            'packet_number': header_values[6],   # Sequential packet counter
            'telemetry_a': header_values[7],     # Telemetry byte A
            'telemetry_b': header_values[8],     # Telemetry byte B
            'telemetry_c': header_values[9],     # Telemetry byte C
            'is_full': header_values[10],        # Buffer full flag (0 or 1)
            'buffer_fill': header_values[11],    # Buffer fill level (0-255)
            'ascan_count': header_values[12],    # Number of A-scans accumulated
            'reserved_b': header_values[13],     # Reserved
            'reserved_c': header_values[14]      # Reserved
        }
        
        # Parse data samples as Int16 array
        data_bytes = packet_data[self.HEADER_LENGTH:]
        num_samples = len(data_bytes) // 2
        
        # Format: '<' = little-endian, 'h' = int16 (signed 16-bit integer)
        data_format = f'<{num_samples}h'
        data = list(struct.unpack(data_format, data_bytes))
        
        return {
            'header': header,
            'data': data,
            'vector_length': len(data),
            'packet_size': len(packet_data),
            'timestamp': time.time()
        }
    
    def _notify_callbacks(self, packet):
        """
        Call all registered callback functions with the parsed packet.
        
        Callbacks are called in the order they were registered.
        If a callback raises an exception, it's caught and logged,
        and other callbacks continue to execute.
        
        Parameters:
            packet (dict): Parsed packet data
        """
        for callback in self.callbacks:
            try:
                callback(packet)
            except Exception as e:
                print(f"Callback error: {str(e)}")
    
    def on_data(self, callback):
        """
        Register a callback function to receive parsed packets.
        
        The callback will be called for each packet received with the format:
        callback(packet) where packet is a dictionary with:
            - header (dict): Dictionary of header fields
            - data (list): List of Int16 sample values
            - vector_length (int): Number of samples
            - packet_size (int): Total packet size in bytes
            - timestamp (float): Time when packet was received (Unix time)
        
        Parameters:
            callback (callable): Function that takes one parameter (packet dict)
        
        Example:
            def my_callback(packet):
                samples = packet['data']
                print(f"Received {len(samples)} samples")
                print(f"Max value: {max(samples)}")
                print(f"Packet #{packet['header']['packet_number']}")
            
            client.on_data(my_callback)
        """
        self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        """
        Remove a previously registered callback function.
        
        Parameters:
            callback (callable): The callback function to remove
            
        Example:
            client.remove_callback(my_callback)
        """
        self.callbacks = [cb for cb in self.callbacks if cb != callback]
    
    def set_ascan_length(self, length):
        """
        Update the expected A-scan length.
        
        CRITICAL: This must match the ascan_length parameter on the device!
        If the lengths don't match, packets will not be parsed correctly.
        
        When you change this value:
        - The stream buffer is cleared (discards partial packets)
        - Packet size calculations are updated
        - You should reconnect to ensure clean state
        
        Parameters:
            length (int): Number of samples per A-scan (e.g., 1024, 2048, 4096)
            
        Example:
            # Read from device first
            device_length = get_parameter("ascan_length")  
            client.set_ascan_length(int(device_length))
        """
        if length > 0 and length != self.ascan_length:
            self.ascan_length = length
            print(f"A-scan length updated to {self.ascan_length}")
            # Clear buffer since packet size changed
            self.stream_buffer.clear()
    
    def get_statistics(self):
        """
        Get connection and data statistics.
        
        Useful for monitoring connection health and diagnosing issues.
        
        Returns:
            dict: Statistics dictionary containing:
                - packets_received (int): Total packets successfully parsed
                - bytes_received (int): Total bytes received from WebSocket
                - parse_errors (int): Number of parsing errors encountered
                - buffer_size (int): Current buffer size in bytes
                - is_connected (bool): Connection status
                - packet_rate (float): Packets per second (if tracking enabled)
        
        Example:
            stats = client.get_statistics()
            print(f"Received {stats['packets_received']} packets")
            print(f"Parse errors: {stats['parse_errors']}")
            if stats['parse_errors'] > 0:
                print("WARNING: Parse errors detected - check ascan_length!")
        """
        return {
            'packets_received': self.packets_received,
            'bytes_received': self.bytes_received,
            'parse_errors': self.parse_errors,
            'buffer_size': len(self.stream_buffer),
            'is_connected': self.is_connected()
        }
    
    def clear_buffer(self):
        """
        Clear the stream buffer - removes any incomplete packets.
        
        Use this if you suspect the buffer has become corrupted or
        if you want to ensure you're only receiving fresh data.
        
        Example:
            client.clear_buffer()
        """
        self.stream_buffer.clear()
    
    def is_connected(self):
        """
        Check if WebSocket is currently connected.
        
        Returns:
            bool: True if connected and receiving, False otherwise
            
        Example:
            if client.is_connected():
                print("Client is connected")
            else:
                print("Client is disconnected")
        """
        return self.ws is not None and self.running
    
    def disconnect(self):
        """
        Disconnect from WebSocket and stop receiving data.
        
        This will:
        - Close the WebSocket connection
        - Stop the background receive thread
        - Clean up resources
        
        Always call this when you're done to free system resources.
        
        Example:
            client.disconnect()
        """
        print("Disconnecting WebSocket...")
        self.running = False
        
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
        
        # Wait for receive thread to finish (max 2 seconds)
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2)
        
        print("WebSocket disconnected")

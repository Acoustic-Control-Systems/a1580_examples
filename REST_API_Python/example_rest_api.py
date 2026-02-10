"""
A1580 REST API - Python Examples
==============================================

This example demonstrates how to interact with the A1580 device using:
1. REST API - For device configuration and control over HTTP
2. WebSocket - For real-time A-scan data streaming

REST API allows you to control and configure the device over a network connection
using simple HTTP requests.

WebSocket provides real-time streaming of A-scan data packets for continuous
data acquisition and analysis.

Target Audience: Integrators.

What you need:
1. Python 3.6 or higher installed on your computer
2. Required libraries (install with: pip install -r requirements.txt)
   - requests: For REST API communication
   - websocket-client: For WebSocket data streaming
3. Network access to your A1580 device
4. The device's IP address, REST API port, and WebSocket port

Basic Concepts:
- REST API: A way to communicate with devices over HTTP (like a web browser)
  * GET: Ask the device for information (read a parameter)
  * POST: Send information to the device (write/set a parameter)
  * JSON: A text format for sending structured data (like {key: value})

- WebSocket: Real-time bidirectional communication channel
  * Maintains persistent connection for streaming data
  * Receives binary packets containing A-scan waveforms
  * Each packet has header (metadata) + data (Int16 samples)
  * Must match device ascan_length for correct parsing
"""

import requests  # Library for making HTTP requests (network communication)
import json      # Library for working with JSON data format
import time      # Library for adding delays between operations

# Import WebSocket client for real-time data acquisition
# This is a separate module that can be copied to your project
from ascan_websocket import AScanWebSocketClient


# =============================================================================
# Configuration Section - CHANGE THESE VALUES FOR YOUR DEVICE
# =============================================================================

# The IP address of your A1580 device
# Find this in your device's network settings or use a network scanner
DEVICE_IP = "192.168.200.18"

# The REST API port number (default is 80, but check your device settings)
REST_PORT = 80

# WebSocket port for real-time data streaming (default is 80)
WEBSOCKET_PORT = 80

# Build the base URL - this is the starting point for all API requests
# Format: http://<device-ip>:<port>/api/v1/
BASE_URL = f"http://{DEVICE_IP}:{REST_PORT}/api/v1/"

# Build the WebSocket URL for data streaming
# Format: ws://<device-ip>:<port>
WEBSOCKET_URL = f"ws://{DEVICE_IP}:{WEBSOCKET_PORT}"


# =============================================================================
# Helper Functions - These make it easier to work with the API
# =============================================================================

def get_parameter(parameter_name):
    """
    Read a parameter value from the device.
    
    This function sends a GET request to read a parameter's current value.
    Think of it like asking the device "What is your current setting for X?"
    
    Parameters:
        parameter_name (str): The name of the parameter to read
                             (e.g., "sampling_freq", "serial_number")
    
    Returns:
        The parameter value if successful, None if there was an error
    
    Example:
        serial = get_parameter("serial_number")
        print(f"Device serial number: {serial}")
    """
    
    # Construct the full URL by adding the parameter name to the base URL
    url = BASE_URL + parameter_name
    
    try:
        # Send the GET request to the device
        # timeout=5 means wait up to 5 seconds for a response
        response = requests.get(url, timeout=5)
        
        # Check if the request was successful (status code 200 = OK)
        if response.status_code == 200:
            # Parse the JSON response into a Python dictionary
            data = response.json()
            
            # Check if the device reported success
            if data.get("status") == "success":
                # Extract and return the parameter value
                parameter_value = data["data"][parameter_name]
                print(f"Successfully read {parameter_name}: {parameter_value}")
                return parameter_value
            else:
                # The device returned an error
                print(f"Device error reading {parameter_name}")
                print(f"  Error message: {data.get('message', 'Unknown error')}")
                return None
        else:
            # HTTP request failed (e.g., 404 Not Found, 400 Bad Request)
            print(f"HTTP error reading {parameter_name}")
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        # The request took too long - device might be offline or unreachable
        print(f"Timeout while reading {parameter_name}")
        print(f"  Device did not respond within 5 seconds")
        return None
        
    except requests.exceptions.ConnectionError:
        # Could not connect to the device - check IP, port, and network
        print(f"Connection error while reading {parameter_name}")
        print(f"  Could not connect to {DEVICE_IP}:{REST_PORT}")
        print(f"  Check device IP, port, and network connection")
        return None
        
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error reading {parameter_name}: {str(e)}")
        return None


def set_parameter(parameter_name, value):
    """
    Set a parameter value on the device.
    
    This function sends a POST request to change a parameter's value.
    
    Parameters:
        parameter_name (str): The name of the parameter to set
                             (e.g., "sampling_freq", "tvg_mode")
        value: The new value to set (can be a number or string)
    
    Returns:
        True if successful, False if there was an error
    
    Example:
        success = set_parameter("sampling_freq", 100)
        if success:
            print("Sampling frequency updated!")
    """
    
    # Construct the full URL
    url = BASE_URL + parameter_name
    
    # Create the JSON payload (data to send to the device)
    # The API requires the value to be in a JSON object with a "value" field
    payload = {"value": value}
    
    # Set the HTTP headers - tells the device we're sending JSON data
    headers = {"Content-Type": "application/json"}
    
    try:
        # Send the POST request with the JSON payload
        # This sends the new value to the device
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Check if the device accepted the new value
            if data.get("status") == "success":
                # Get the confirmed value from the response
                confirmed_value = data["data"][parameter_name]
                print(f"Successfully set {parameter_name} to {confirmed_value}")
                return True
            else:
                # The device rejected the value
                print(f"Device error setting {parameter_name} to {value}")
                print(f"  Error message: {data.get('message', 'Unknown error')}")
                
                # Show detailed error information if available
                if "details" in data:
                    details = data["details"]
                    print(f"  Error code: {details.get('code')}")
                    print(f"  Field: {details.get('field')}")
                    print(f"  Expected: {details.get('expected')}")
                    print(f"  Received: {details.get('received')}")
                return False
        else:
            # HTTP request failed
            print(f"HTTP error setting {parameter_name} to {value}")
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"Timeout while setting {parameter_name}")
        print(f"  Device did not respond within 5 seconds")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"Connection error while setting {parameter_name}")
        print(f"  Could not connect to {DEVICE_IP}:{REST_PORT}")
        print(f"  Check device IP, port, and network connection")
        return False
        
    except Exception as e:
        print(f"Unexpected error setting {parameter_name}: {str(e)}")
        return False


def check_device_connection():
    """
    Test if the device is reachable and responding.
    
    This function attempts to read a basic parameter to verify connectivity.
    Use this at the start of your program to make sure you can communicate
    with the device before trying other operations.
    
    Returns:
        True if device is accessible, False otherwise
    """
    print("Testing connection to A1580 device...")
    print(f"Device IP: {DEVICE_IP}")
    print(f"REST Port: {REST_PORT}")
    print(f"Base URL: {BASE_URL}")
    
    # Try to read the device type - a simple read-only parameter
    # This is a good test because it should always work if the device is online
    device_type = get_parameter("device_type")
    
    if device_type is not None:
        print("Device connection successful!")
        return True
    else:
        print("Device connection failed!")
        print("\nTroubleshooting tips:")
        print("1. Verify the device IP address is correct")
        print("2. Check that the REST API port matches your device configuration")
        print("3. Ensure your computer and device are on the same network")
        print("4. Try pinging the device: ping", DEVICE_IP)
        return False


# =============================================================================
# WebSocket Data Acquisition - Using Imported Module
# =============================================================================
# The AScanWebSocketClient class is imported from ascan_websocket.py module.
# 
# This separate module can be easily copied to your own project.
# See ascan_websocket.py for the complete implementation and documentation.
#
# Usage:
#   from ascan_websocket import AScanWebSocketClient
#   client = AScanWebSocketClient(url="ws://192.168.200.18:80", ascan_length=2048)
# =============================================================================


def websocket_example_basic():
    """
    Basic example: Connect to WebSocket and display received packets.
    
    This is the simplest way to receive real-time data from the device.
    """
    print("\nConnecting to WebSocket for basic data reception...")
    
    # Step 1: Get the ascan_length from device (IMPORTANT!)
    # The client must use the same ascan_length as the device
    device_ascan_length = get_parameter("ascan_length")
    if device_ascan_length is None:
        print("Could not read ascan_length from device")
        return
    
    print(f"Device ascan_length: {device_ascan_length}")
    
    # Step 2: Create WebSocket client with correct ascan_length
    client = AScanWebSocketClient(url=WEBSOCKET_URL, ascan_length=int(device_ascan_length))
    
    # Step 3: Define callback function to process each packet
    packet_count = 0
    
    def on_packet_received(packet):
        """
        This function is called automatically for each packet received.
        You can process the data here however you want.
        """
        nonlocal packet_count
        packet_count += 1
        
        # Extract information from packet
        data = packet['data']              # List of Int16 samples
        header = packet['header']          # Header dictionary
        
        # Display packet information
        print(f"\rPacket #{packet_count}: "
              f"{len(data)} samples, "
              f"range [{min(data)}, {max(data)}], "
              f"pkt# {header['packet_number']}", 
              end='', flush=True)
    
    # Step 4: Register the callback
    client.on_data(on_packet_received)
    
    # Step 5: Connect and start receiving
    if client.connect():
        # Start automatic A-scan acquisition to ensure data is streaming
        set_parameter("start_auto_ascan", 1)

        print("Receiving data for 5 seconds...")
        time.sleep(5)
        
        # Stop acquisition when done
        set_parameter("start_auto_ascan", 0)
        
        # Step 6: Disconnect when done
        client.disconnect()
        print(f"\n\nReceived {packet_count} packets total")
    else:
        print("Failed to connect")


def websocket_example_analysis():
    """
    Advanced example: Analyze A-scan data in real-time.
    
    This shows how to extract useful information from the waveforms,
    such as peak detection, time-of-flight, and signal statistics.
    """
    print("\nConnecting to WebSocket for real-time analysis...")
    
    # Get device configuration
    device_ascan_length = get_parameter("ascan_length")
    sampling_freq = get_parameter("sampling_freq")
    
    if device_ascan_length is None or sampling_freq is None:
        print("Could not read device parameters")
        return
    
    print(f"Configuration: {device_ascan_length} samples @ {sampling_freq} MHz")
    
    # Calculate time per sample (microseconds)
    time_per_sample = 1.0 / float(sampling_freq)  # microseconds
    
    # Create client
    client = AScanWebSocketClient(url=WEBSOCKET_URL, ascan_length=int(device_ascan_length))
    
    # Storage for analysis results
    analysis_results = []
    
    def analyze_ascan(packet):
        """
        Analyze each A-scan waveform to extract useful information.
        
        This example shows common signal processing tasks:
        - Find peak amplitude and location
        - Calculate RMS (signal strength)
        - Detect threshold crossings
        - Calculate time-of-flight
        """
        data = packet['data']
        
        # Find peak amplitude and its index
        abs_data = [abs(x) for x in data]
        peak_amplitude = max(abs_data)
        peak_index = abs_data.index(peak_amplitude)
        peak_time = peak_index * time_per_sample  # microseconds
        
        # Calculate RMS (Root Mean Square) - indicates signal energy
        sum_squares = sum(x*x for x in data)
        rms = (sum_squares / len(data)) ** 0.5
        
        # Find first threshold crossing (simple echo detection)
        # Use 20% of peak as threshold
        threshold = peak_amplitude * 0.2
        first_crossing = None
        for i, val in enumerate(abs_data):
            if val > threshold:
                first_crossing = i
                break
        
        tof = first_crossing * time_per_sample if first_crossing else None
        
        # Store results
        result = {
            'packet_number': packet['header']['packet_number'],
            'peak_amplitude': peak_amplitude,
            'peak_index': peak_index,
            'peak_time_us': peak_time,
            'rms': rms,
            'time_of_flight_us': tof
        }
        analysis_results.append(result)
        
        # Display only every 10th packet to avoid flooding console
        if len(analysis_results) % 10 == 0:
            print(f"\rAnalyzed {len(analysis_results)} packets | "
                  f"Peak: {peak_amplitude} @ {peak_time:.2f}µs | "
                  f"RMS: {rms:.1f} | "
                  f"TOF: {tof:.2f}µs" if tof else "No echo",
                  end='', flush=True)
    
    # Register callback and collect data
    client.on_data(analyze_ascan)
    
    if client.connect():
        
        # Start automatic A-scan acquisition to ensure data is streaming
        set_parameter("start_auto_ascan", 1)
        
        print("Analyzing data for 5 seconds...")
        time.sleep(5)
        
        # Stop acquisition when done
        set_parameter("start_auto_ascan", 0)
        
        client.disconnect()
        
        # Display summary statistics
        print(f"\n\nAnalysis Summary ({len(analysis_results)} packets):")
        if analysis_results:
            avg_peak = sum(r['peak_amplitude'] for r in analysis_results) / len(analysis_results)
            avg_rms = sum(r['rms'] for r in analysis_results) / len(analysis_results)
            
            # Filter out None values for TOF
            valid_tofs = [r['time_of_flight_us'] for r in analysis_results if r['time_of_flight_us'] is not None]
            if valid_tofs:
                avg_tof = sum(valid_tofs) / len(valid_tofs)
                print(f"  Average Peak Amplitude: {avg_peak:.1f}")
                print(f"  Average RMS:            {avg_rms:.1f}")
                print(f"  Average Time of Flight: {avg_tof:.2f} µs")
                print(f"  Echo Detection Rate:    {len(valid_tofs)/len(analysis_results)*100:.1f}%")
    else:
        print("Failed to connect")


def websocket_example_save_data():
    """
    Example: Save A-scan data to a file for later analysis.
    
    This shows how to capture data and save it in a simple format
    that can be loaded in Excel, MATLAB, Python, etc.
    """
    print("\nConnecting to WebSocket to save data...")
    
    # Get device configuration
    device_ascan_length = get_parameter("ascan_length")
    if device_ascan_length is None:
        print("Could not read device parameters")
        return
    
    # Create client
    client = AScanWebSocketClient(url=WEBSOCKET_URL, ascan_length=int(device_ascan_length))
    
    # Storage for captured waveforms
    saved_waveforms = []
    max_waveforms = 20  # Capture 20 A-scans
    
    def save_waveform(packet):
        """Save waveform data to memory."""
        if len(saved_waveforms) < max_waveforms:
            saved_waveforms.append({
                'packet_number': packet['header']['packet_number'],
                'timestamp': packet['timestamp'],
                'data': packet['data']
            })
            print(f"\rCaptured {len(saved_waveforms)}/{max_waveforms} waveforms...", 
                  end='', flush=True)
    
    # Register callback
    client.on_data(save_waveform)
    
    if client.connect():
        # Start automatic A-scan acquisition to ensure data is streaming
        set_parameter("start_auto_ascan", 1)
        
        # Wait until we have enough waveforms
        while len(saved_waveforms) < max_waveforms and client.is_connected():
            time.sleep(0.1)
        
        # Stop acquisition when done
        set_parameter("start_auto_ascan", 0)
        
        client.disconnect()
        
        # Save to CSV file
        filename = "ascan_data.csv"
        print(f"\n\nSaving {len(saved_waveforms)} waveforms to {filename}...")
        
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write("# A-scan data from A1580 device\n")
                f.write(f"# Captured: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Ascan length: {device_ascan_length} samples\n")
                f.write("#\n")
                f.write("# Format: Each row is one A-scan waveform\n")
                f.write("# Columns: packet_number, timestamp, sample_0, sample_1, ...\n")
                f.write("#\n")
                
                # Write data - each row is one waveform
                for wf in saved_waveforms:
                    # Start with packet number and timestamp
                    row = [str(wf['packet_number']), f"{wf['timestamp']:.6f}"]
                    # Add all sample values
                    row.extend(str(x) for x in wf['data'])
                    f.write(','.join(row) + '\n')
            
            print(f"Data saved successfully to {filename}")
            print(f"  File contains {len(saved_waveforms)} waveforms")
            print(f"  Each waveform has {len(saved_waveforms[0]['data'])} samples")
            print("\nYou can now:")
            print("  • Open the file in Excel or spreadsheet software")
            print("  • Load it in Python with: pandas.read_csv('ascan_data.csv', comment='#')")
            print("  • Import to MATLAB with: readmatrix('ascan_data.csv')")
            
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    else:
        print("Failed to connect")


# =============================================================================
# Example Usage - Demonstration of common operations
# =============================================================================

def main():
    """
    Main function demonstrating how to use the REST API.
    
    This shows examples of reading and writing various parameters.
    You can use these examples as templates for your own integration.
    """
    
    print("A1580 REST API Python Example")
    
    # Step 1: Test device connectivity
    # Always start by checking if you can communicate with the device
    if not check_device_connection():
        print("\nCannot proceed - device is not accessible")
        return
    
    # Add a small delay between operations to avoid overwhelming the device
    time.sleep(0.5)
    
    
    # =========================================================================
    # Example 1: Reading System Information (Read-Only Parameters)
    # =========================================================================
    print("Example 1: Reading System Information")
    print("These parameters are read-only and provide device identification.")
    
    # Read device serial number
    serial_number = get_parameter("serial_number")
    time.sleep(0.2)  # Short delay between requests
    
    # Read firmware version
    firmware_version = get_parameter("firmware_version")
    time.sleep(0.2)
    
    # Read protocol version
    protocol_version = get_parameter("protocol_version")
    time.sleep(0.2)
    
    # Read device hostname
    hostname = get_parameter("system.hostname")
    
    print(f"\nDevice Information Summary:")
    print(f"  Serial Number:     {serial_number}")
    print(f"  Firmware Version:  {firmware_version}")
    print(f"  Protocol Version:  {protocol_version}")
    print(f"  Hostname:          {hostname}")
    
    time.sleep(1)  # Longer delay before next section
    
    
    # =========================================================================
    # Example 2: Reading Current Acquisition Settings
    # =========================================================================
    print("Example 2: Reading Current Acquisition Settings")
    print("These settings control how the device acquires data.")
    
    # Read sampling frequency (in MHz)
    sampling_freq = get_parameter("sampling_freq")
    time.sleep(0.2)
    
    # Read A-scan length (number of samples)
    ascan_length = get_parameter("ascan_length")
    time.sleep(0.2)
    
    # Read number of accumulations
    accumulations = get_parameter("accumulations")
    time.sleep(0.2)
    
    # Read current operating mode
    current_mode = get_parameter("current_mode")
    
    print(f"\nCurrent Acquisition Settings:")
    print(f"  Sampling Frequency: {sampling_freq} MHz")
    print(f"  A-scan Length:      {ascan_length} samples")
    print(f"  Accumulations:      {accumulations}")
    print(f"  Operating Mode:     {current_mode}")
    
    time.sleep(1)
    
    
    # =========================================================================
    # Example 3: Setting Acquisition Parameters
    # =========================================================================
    print("Example 3: Setting Acquisition Parameters")
    print("Changing device settings by writing parameter values.")
    
    # Set sampling frequency to 100 MHz
    print("\nSetting sampling frequency to 100 MHz...")
    success = set_parameter("sampling_freq", 100)
    if success:
        print("Sampling frequency updated successfully")
    time.sleep(0.5)
    
    # Set A-scan length to 2048 samples
    print("\nSetting A-scan length to 2048 samples...")
    success = set_parameter("ascan_length", 2048)
    if success:
        print("A-scan length updated successfully")
    time.sleep(0.5)
    
    # Set accumulations to 4 (2^4 = 16 accumulations)
    print("\nSetting accumulations to 4 (16 accumulations)...")
    success = set_parameter("accumulations", 4)
    if success:
        print("Accumulations updated successfully")
    time.sleep(0.5)
    
    
    # =========================================================================
    # Example 4: Configuring Time Variable Gain (TVG)
    # =========================================================================
    print("Example 4: Configuring Time Variable Gain (TVG)")
    print("TVG settings control signal amplification over time.")
    
    # Read current TVG mode
    print("\nReading current TVG mode...")
    tvg_mode = get_parameter("tvg_mode")
    time.sleep(0.5)
    
    # Set TVG mode to OFF (use bypass gain instead)
    print("\nSetting TVG mode to OFF...")
    success = set_parameter("tvg_mode", "OFF")
    time.sleep(0.5)
    
    # When TVG is OFF, set the bypass gain (constant gain in dB)
    print("\nSetting TVG bypass gain to 30 dB...")
    success = set_parameter("tvg_bypass", 30)
    if success:
        print("TVG configured: mode=OFF, bypass gain=30 dB")
    time.sleep(0.5)
    
    
    # =========================================================================
    # Example 5: Configuring Triggering
    # =========================================================================
    print("Example 5: Configuring Triggering")
    print("Trigger settings control when the device starts acquiring data.")
    
    # Set internal triggering mode
    print("\nSetting triggering mode to INTERNAL...")
    success = set_parameter("triggering_mode", "INTERNAL")
    time.sleep(0.5)
    
    # Set internal trigger interval to 1000 microseconds (1 kHz repetition rate)
    print("\nSetting trigger interval to 1000 µs (1 kHz)...")
    success = set_parameter("triggering_interval", 1000)
    if success:
        print("Triggering configured: INTERNAL mode at 1 kHz")
    time.sleep(0.5)
    
    
    # =========================================================================
    # Example 6: Configuring Pulser Settings
    # =========================================================================
    print("Example 6: Configuring Pulser Settings")
    print("Pulser settings control the transmitted ultrasonic pulse.")
    
    # Set pulse frequency to 5000 kHz (5 MHz)
    print("\nSetting pulse frequency to 5000 kHz (5 MHz)...")
    success = set_parameter("zonder_frequency", 5000)
    time.sleep(0.5)
    
    # Set number of pulse periods to 2.5
    print("\nSetting pulse periods to 2.5...")
    success = set_parameter("zonder_periods", 2.5)
    time.sleep(0.5)
    
    # Set pulse amplitude to 100 V
    print("\nSetting pulse amplitude to 100 V...")
    success = set_parameter("zonder_amplitude", 100)
    time.sleep(0.5)
    
    # Enable the pulser
    print("\nEnabling pulser...")
    success = set_parameter("zonder_enable", "ON")
    if success:
        print("Pulser configured: 5 MHz, 2.5 periods, 100V, enabled")
    time.sleep(0.5)
    
    
    # =========================================================================
    # Example 7: Error Handling - Intentional Errors for Learning
    # =========================================================================
    print("Example 7: Error Handling Demonstration")
    print("Showing what happens when you send invalid values.")
    
    # Try to set a value outside the valid range
    print("\nAttempting to set TVG bypass to 500 dB (exceeds max of 80)...")
    success = set_parameter("tvg_bypass", 500)
    # You should see a detailed error message with expected range
    time.sleep(0.5)
    
    # Try to set an invalid mode value
    print("\nAttempting to set TVG mode to 'INVALID_MODE'...")
    success = set_parameter("tvg_mode", "INVALID_MODE")
    # You should see an error with the list of valid values
    time.sleep(0.5)
    
    # Try to read a non-existent parameter
    print("\nAttempting to read non-existent parameter...")
    value = get_parameter("nonexistent_parameter")
    # You should see a "parameter not found" error
    
    
    # =========================================================================
    # Example 8: Controlling Data Acquisition
    # =========================================================================
    print("Example 8: Controlling Data Acquisition")
    print("Starting and stopping automatic A-scan acquisition.")
    
    # Start automatic A-scan acquisition
    print("\nStarting automatic A-scan acquisition...")
    success = set_parameter("start_auto_ascan", 1)
    if success:
        print("A-scan acquisition started")
        print("Device is now continuously acquiring data")
    time.sleep(2)  # Let it run for 2 seconds
    
    # Stop automatic A-scan acquisition
    print("\nStopping automatic A-scan acquisition...")
    success = set_parameter("stop_auto_ascan", 1)
    if success:
        print("A-scan acquisition stopped")
    
    
    # =========================================================================
    # Example 9: Real-Time Data Acquisition via WebSocket
    # =========================================================================
    print("Example 9: Real-Time Data Acquisition via WebSocket")
    print("Receiving live A-scan data from the device.")
    
    # Example 9a: Basic data reception
    print("\n--- Example 9a: Basic Data Reception ---")
    websocket_example_basic()
    
    # Example 9b: Data analysis
    print("\n--- Example 9b: Real-Time Data Analysis ---")
    websocket_example_analysis()
    
    # Example 9c: Saving data to file
    print("\n--- Example 9c: Saving Data to File ---")
    websocket_example_save_data()
    
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("Example Complete!")
    print("\nYou've learned how to:")
    print("  • Connect to the device and verify communication")
    print("  • Read system information and current settings")
    print("  • Set acquisition parameters (sampling, A-scan length, etc.)")
    print("  • Configure TVG and triggering settings")
    print("  • Configure pulser parameters")
    print("  • Handle errors and invalid values")
    print("  • Start and stop data acquisition")
    print("  • Receive real-time data via WebSocket")
    print("  • Parse and analyze A-scan waveforms")
    print("  • Diagnose WebSocket connection issues")
    print("\nNext steps:")
    print("  • Modify the examples above for your specific needs")
    print("  • See REST_API.md for complete parameter documentation")
    print("  • Build your own integration using these functions as building blocks")


# =============================================================================
# Additional Utility Functions
# =============================================================================

def get_all_system_info():
    """
    Convenience function to read all system information at once.
    
    Returns a dictionary with all system information parameters.
    Useful for logging or displaying complete device status.
    """
    info = {}
    
    # List of system information parameters
    system_params = [
        "system.hostname",
        "system.version",
        "device_type",
        "serial_number",
        "protocol_version",
        "firmware_version"
    ]
    
    print("\nReading all system information...")
    for param in system_params:
        value = get_parameter(param)
        if value is not None:
            info[param] = value
        time.sleep(0.2)
    
    return info


def configure_basic_acquisition(sampling_freq, ascan_length, accumulations):
    """
    Convenience function to configure basic acquisition settings in one call.
    
    Parameters:
        sampling_freq: Sampling frequency in MHz
        ascan_length: A-scan length in samples
        accumulations: Number of accumulations (0-8, power of 2)
    
    Returns:
        True if all settings were applied successfully
    """
    print(f"\nConfiguring acquisition settings:")
    print(f"  Sampling Frequency: {sampling_freq} MHz")
    print(f"  A-scan Length:      {ascan_length} samples")
    print(f"  Accumulations:      {accumulations}")
    
    success = True
    success &= set_parameter("sampling_freq", sampling_freq)
    time.sleep(0.2)
    success &= set_parameter("ascan_length", ascan_length)
    time.sleep(0.2)
    success &= set_parameter("accumulations", accumulations)
    
    if success:
        print("All acquisition settings applied successfully")
    else:
        print("Some acquisition settings failed to apply")
    
    return success


# =============================================================================
# Program Entry Point
# =============================================================================

if __name__ == "__main__":
    """
    This block runs when you execute the script directly.
    
    To run this example:
    1. Update DEVICE_IP, REST_PORT, and WEBSOCKET_PORT at the top of this file
    2. Install required libraries: pip install -r requirements.txt
    3. Run the script: python example_rest_api.py
    """
    
    try:
        # Run the main demonstration
        main()
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\nProgram interrupted by user (Ctrl+C)")
        print("Exiting...")
        
    except Exception as e:
        # Catch any unexpected errors
        print(f"\n\nUnexpected error occurred: {str(e)}")
        print("Please check your configuration and try again")


# =============================================================================
# Quick Reference Guide
# =============================================================================
"""
QUICK REFERENCE FOR INTEGRATORS:
================================

1. CONNECTING TO DEVICE:
   - Update DEVICE_IP, REST_PORT, and WEBSOCKET_PORT variables
   - Run check_device_connection() to verify REST API connectivity

2. READING A PARAMETER (GET):
   value = get_parameter("parameter_name")
   Example: serial = get_parameter("serial_number")

3. SETTING A PARAMETER (POST):
   success = set_parameter("parameter_name", value)
   Example: set_parameter("sampling_freq", 100)

4. WEBSOCKET DATA ACQUISITION:
   # Get device ascan_length first (CRITICAL!)
   ascan_length = get_parameter("ascan_length")
   
   # Create client with matching ascan_length and URL
   client = AScanWebSocketClient(url=WEBSOCKET_URL, ascan_length=int(ascan_length))
   
   # Define callback to process data
   def my_callback(packet):
       data = packet['data']  # List of Int16 samples
       print(f"Received {len(data)} samples")
   
   # Register callback and connect
   client.on_data(my_callback)
   client.connect()
   
   # Receive data...
   time.sleep(10)
   
   # Disconnect when done
   client.disconnect()

5. PARSING WEBSOCKET PACKETS:
   Each packet is a dictionary with:
     - data: List of Int16 sample values (the A-scan waveform)
     - header: Dictionary with metadata
       * packet_number: Sequential counter
       * ctp: CTP timing array
       * ascan_count: Number of A-scans accumulated
       * buffer_fill: Device buffer status
     - vector_length: Number of samples in data
     - timestamp: Time when packet was received
   
   Example analysis:
     peak_value = max(packet['data'])
     peak_index = packet['data'].index(peak_value)
     rms = (sum(x*x for x in packet['data']) / len(packet['data'])) ** 0.5

6. COMMON PARAMETERS:
   System Info (Read-Only):
     - serial_number
     - firmware_version
     - device_type
     
   Acquisition Settings:
     - sampling_freq (MHz)
     - ascan_length (samples) ← MUST match WebSocket client!
     - accumulations (0-8)
     
   TVG Settings:
     - tvg_mode ("OFF", "LINEAR", "ARBITRARY")
     - tvg_bypass (dB, base gain level for all modes)
     
   Triggering:
     - triggering_mode ("INTERNAL", "CTP", "TTL", "SENSOR")
     - triggering_interval (microseconds)
     
   Pulser:
     - zonder_frequency (kHz)
     - zonder_periods (0.5 to 8)
     - zonder_amplitude (V)
     - zonder_enable ("ON" / "OFF")

7. ERROR HANDLING:
   REST API:
   - Functions return None (for reads) or False (for writes) on error
   - Check return values before proceeding
   - Error messages are printed automatically with details
   
   WebSocket:
   - Check statistics with client.get_statistics()
   - Common issues:
     * No data: Device not streaming (start_auto_ascan not called)
     * Parse errors: ascan_length mismatch between client and device
     * Connection refused: Wrong port or device not running WebSocket server

8. BEST PRACTICES:
   - Always check device connection first
   - Read ascan_length from device before creating WebSocket client
   - Add small delays between REST API operations (0.2-0.5 seconds)
   - Check return values to confirm success
   - Use callbacks for WebSocket data processing
   - Disconnect WebSocket when done to free resources

9. TROUBLESHOOTING:
   REST API:
   - Connection refused: Check IP address and REST_PORT
   - Parameter not found: Verify parameter name spelling
   - Value rejected: Check valid range/values in REST_API.md
   - Timeout: Device may be offline or network is slow
   
   WebSocket:
   - No data received: Device not streaming (call start_auto_ascan)
   - Parse errors: ascan_length mismatch (read from device first)
   - Connection refused: Check WEBSOCKET_PORT, verify device WebSocket enabled
   - Packet loss: Check network quality, reduce packet rate if needed

10. COMPLETE WORKFLOW EXAMPLE:
    # Step 1: Connect and configure device via REST API
    check_device_connection()
    set_parameter("sampling_freq", 100)
    set_parameter("ascan_length", 2048)
    set_parameter("triggering_mode", "INTERNAL")
    set_parameter("triggering_interval", 1000)
    
    # Step 2: Start acquisition
    set_parameter("start_auto_ascan", 1)
    
    # Step 3: Get ascan_length for WebSocket
    ascan_length = int(get_parameter("ascan_length"))
    
    # Step 4: Connect WebSocket and receive data
    client = AScanWebSocketClient(url=WEBSOCKET_URL, ascan_length=ascan_length)
    client.on_data(lambda pkt: print(f"Peak: {max(pkt['data'])}"))
    client.connect()
    time.sleep(10)
    
    # Step 5: Stop and cleanup
    client.disconnect()
    set_parameter("stop_auto_ascan", 1)

For complete parameter documentation, see REST_API.md
"""

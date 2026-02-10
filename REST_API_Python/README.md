# A1580 REST API Python Examples

Python examples for integrating with the A1580 device using REST API and WebSocket.

## Files

### Main Files

- **[example_rest_api.py](example_rest_api.py)** - Complete examples demonstrating REST API and WebSocket usage
  - Configuration and device control via REST API
  - Real-time data acquisition via WebSocket
  - Data analysis and file saving examples

- **[ascan_websocket.py](ascan_websocket.py)** - **Standalone WebSocket client module**
  - Copy this file directly into your project
  - Self-contained with full documentation
  - No dependencies except `websocket-client` library

- **[requirements.txt](requirements.txt)** - Python package dependencies

- **[REST_API.md](../REST_API.md)** - Complete REST API documentation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Device Connection

Edit the configuration section in `example_rest_api.py`:

```python
DEVICE_IP = "192.168.200.18"    # Your device IP
REST_PORT = 80                   # REST API port (default: 80)
WEBSOCKET_PORT = 80            # WebSocket port (default: 80)
```

### 3. Run Examples

```bash
python example_rest_api.py
```

## Using the WebSocket Client in Your Project

The `ascan_websocket.py` module is designed to be copied directly into your project:

### Basic Usage

```python
from ascan_websocket import AScanWebSocketClient

# Create client (match device ascan_length!)
client = AScanWebSocketClient(
    url="ws://192.168.200.18:80",
    ascan_length=2048
)

# Define callback for data processing
def on_data(packet):
    samples = packet['data']  # List of Int16 values
    print(f"Received {len(samples)} samples")
    print(f"Peak: {max(samples)}")

# Connect and receive data
client.on_data(on_data)
client.connect()

# ... process data ...

client.disconnect()
```

## Key Concepts

### REST API
- **GET**: Read parameter values from device
- **POST**: Set parameter values on device
- Used for configuration and control

### WebSocket
- **Real-time streaming**: Continuous A-scan data packets
- **Binary protocol**: Header (28 bytes) + Int16 sample data
- **CRITICAL**: `ascan_length` must match device configuration!

### Raw socket alternative

Instead of WebSocket, you can also connect to the device's raw TCP socket (port 2758) to receive the same binary data stream. This may be useful for low-level integration or if WebSocket support is not available in your environment.
See [common_functions.py](../SCPI_Python/common_functions.py) for example code to connect to the raw socket and parse data packets.

### Typical Workflow

1. Configure device via REST API
   ```python
   set_parameter("sampling_freq", 100)
   set_parameter("ascan_length", 2048)
   ```

2. Start acquisition
   ```python
   set_parameter("start_auto_ascan", 1)
   ```

3. Connect WebSocket and receive data
   ```python
   ascan_length = int(get_parameter("ascan_length"))
   client = AScanWebSocketClient(url=WEBSOCKET_URL, ascan_length=ascan_length)
   client.connect()
   ```

4. Process data in callback
   ```python
   def process_data(packet):
       # Your analysis code here
       pass
   ```

5. Cleanup
   ```python
   client.disconnect()
   set_parameter("stop_auto_ascan", 1)
   ```

## Examples Included

The `example_rest_api.py` file contains complete working examples:

1. **System Information** - Reading device details
2. **Acquisition Settings** - Reading current configuration
3. **Setting Parameters** - Changing device settings
4. **TVG Configuration** - Time Variable Gain setup
5. **Triggering Configuration** - Trigger mode and timing
6. **Pulser Configuration** - Pulse parameters
7. **Error Handling** - Handling invalid values
8. **Data Acquisition Control** - Starting/stopping acquisition
9. **WebSocket Data Streaming** - Three complete examples:
   - Basic data reception
   - Real-time data analysis (peak detection, RMS, TOF)
   - Saving data to CSV file

## Troubleshooting

### REST API Issues
- **Connection refused**: Check `DEVICE_IP` and `REST_PORT`
- **Parameter not found**: Verify parameter name spelling
- **Value rejected**: Check valid range in REST_API.md
- **Timeout**: Device may be offline

### WebSocket Issues
- **No connection**: Check `WEBSOCKET_PORT`, verify device WebSocket is running
- **No data received**: Device not streaming (call `start_auto_ascan`)
- **Parse errors**: `ascan_length` mismatch - read from device first!

## Requirements

- Python 3.6 or higher
- `requests` library for REST API
- `websocket-client` library for WebSocket
- Network access to A1580 device

## Documentation

- [REST_API.md](../REST_API.md) - Complete REST API reference
- [SCPI_COMMANDS.md](../SCPI_COMMANDS.md) - SCPI command reference
- [example_rest_api.py](example_rest_api.py) - Inline documentation and examples

## License

MIT - Free to use and modify for your integration needs.

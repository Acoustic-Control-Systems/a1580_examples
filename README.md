# A1580
Examples for integration of A1580 Sonic Ultrasonic Pulser-Receiver frontend unit 

# Files
* [SCPI commands](SCPI_COMMANDS.md) - List of supported SCPI commands for controlling the A1580 device
* [REST API](REST_API.md) - Documentation for the REST API interface of the A1580 device

* [SCPI protocol example](SCPI_Python/example_scpi_protocol.py) - Read identity, acquisition settings, and plate revisions, control the device via SCPI, and receive A-scan data over the TCP data port
* [Common functions](SCPI_Python/common_functions.py) - Shared utility functions for device control and data processing
* [REST API example](REST_API_Python/example_rest_api.py) - Read serial number, firmware and protocol versions, acquisition settings, and plate revisions with `get_parameter()`, configure the device, and receive A-scan data via WebSocket
* [WebSocket client module](REST_API_Python/ascan_websocket.py) - Standalone WebSocket client for receiving A-scan data in real-time

Install the requirements from the corresponding example directory before running its examples.

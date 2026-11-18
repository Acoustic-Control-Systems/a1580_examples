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

## Data stream access

Use one A-scan data receiver at a time: either WebSocket or raw TCP port 2758.
The browser receives data over WebSocket. Both access methods share one device
stream; a new data connection closes the previous receiver's connection.

| Current receiver | New connection | Result |
| --- | --- | --- |
| Browser over WebSocket | A raw TCP client connects to port 2758 | The browser stream disconnects; the raw client takes over. |
| Raw TCP client | Browser or a WebSocket script connects | The raw client disconnects; the WebSocket client takes over. |
| Any data receiver | A second browser tab, WebSocket client, or raw client connects | The previous receiver disconnects; the new client takes over. |

A browser can automatically reconnect and take the stream back. Before raw TCP
capture, close all A1580 browser tabs and other stream clients. Before switching
to WebSocket, disconnect the raw client and any other WebSocket receiver.
SCPI commands on port 5025 can be used alongside the selected data stream.

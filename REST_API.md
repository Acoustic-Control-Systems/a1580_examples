# A1580 REST API Documentation

## Overview

The A1580 firmware provides a JSON-based REST API for device configuration and control. The API runs on a configurable TCP port (default: 80) and provides access to device parameters through simple HTTP requests.

**Base URL:** `http://<device-ip>:<rest_port>/api/v1/`

## Request/Response Format

### Successful GET Response
```json
{
  "status": "success",
  "data": {
    "<parameter>": "<value>"
  }
}
```

### Successful POST/PUT Request
**Request body:**
```json
{
  "value": "<string|number>"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "<parameter>": "<value>"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "<human-readable error message>",
  "details": {
    "code": <error_code>,
    "field": "<parameter_name>",
    "expected": "<expected_value_or_range>",
    "received": "<actual_value_received>"
  }
}
```

## Error Codes

The API provides granular error reporting with the following error codes:

| Code | Name | Description | Example |
|------|------|-------------|---------|
| `0` | `REST_ERR_SUCCESS` | Operation successful | N/A (no error) |
| `-1` | `REST_ERR_INVALID_VALUE` | Value not in allowed list | Setting tvg_mode to "INVALID" when only "OFF", "LINEAR", "ARBITRARY" are valid |
| `-2` | `REST_ERR_OUT_OF_RANGE` | Numeric value outside valid range | Setting sampling_freq to 500000000 when max is 100000000 |
| `-3` | `REST_ERR_MISSING_FIELD` | Required field missing from request | POST request without "value" field in JSON body |
| `-4` | `REST_ERR_NOT_FOUND` | Parameter does not exist | Accessing non-existent parameter |
| `-5` | `REST_ERR_READ_ONLY` | Attempt to modify read-only parameter | Trying to set firmware_version |
| `-6` | `REST_ERR_PROTOCOL_FAILED` | Internal protocol error | Communication failure with device subsystem |

## HTTP Methods

| Method | Purpose | Body Required |
|--------|---------|---------------|
| `GET` | Read parameter value | No |
| `POST` | Set parameter value | Yes (JSON with "value" field) |
| `PUT` | Set parameter value (alias for POST) | Yes (JSON with "value" field) |
| `OPTIONS` | CORS preflight | No |

## Available Parameters

The API provides access to the following parameter categories:

### System Information (Read-Only)
- `system.hostname` — Device hostname
- `system.version` — System version
- `device_type` — Device type identifier
- `serial_number` — Device serial number
- `protocol_version` — Protocol version
- `firmware_version` — Firmware version

### Acquisition Settings
- `sampling_freq` — Sampling frequency in MHz (see list of available freqs in SCPI)
- `ascan_length` — A-scan length in samples
- `accumulations` — Number of accumulations, 0-8 (power of 2)
- `current_mode` — Current operating mode (Master/Slave)
- `ping_pong` — Ping-pong mode setting (set to 0 to disable)

### Time Variable Gain (TVG) Control
- `tvg_mode` — TVG mode: "OFF", "LINEAR", "ARBITRARY"
- `tvg_bypass` — Bypass gain in dB (when TVG is OFF)
- `tvg_linear` — Linear TVG parameters
- `tvg_arbitrary` — Arbitrary TVG curve data

### Triggering
- `triggering_mode` — Trigger source mode, INTERNAL/CTP/TTL/SENSOR
- `triggering_interval` — Internal trigger interval, us
- `trigger_delay` — Trigger delay in samples before acquisition
- `constant_delay` — Constant delay value for averaging
- `random_delay` — Random delay range for averaging

### Pulser/Receiver (Zonder) Control
- `zonder_frequency` — Pulse frequency, kHz
- `zonder_periods` — Number of pulse periods, from 0.5 to 8
- `zonder_amplitude` — Pulse amplitude, V
- `zonder_enable` — Enable/disable pulser, ON/OFF
- `zonder_reverse_polarity` — Reverse polarity setting, ON/OFF
- `zonder_mode` — Pulser operating mode, COMBINED/SPLIT
- `zonder_damp_enable` — Enable damping, ON/OFF
- `high_pass_filter` — High-pass filter setting
- `split_preamp` — Split preamplifier gain (+20 dB), ON/OFF
- `combined_preamp` — Combined preamplifier gain (+20 dB), ON/OFF
- `impedance` — Input impedance setting, HIGH/200/1000

- `clean_memory` — Clear device memory (write-only)
- `start_auto_ascan` — Start automatic A-scan acquisition (write-only)
- `stop_auto_ascan` — Stop automatic A-scan acquisition (write-only)

## Examples with curl

### Successful GET Request
```bash
# Get device hostname
curl -X GET "http://192.168.200.18:8080/api/v1/system.hostname"
```

```powershell
Invoke-RestMethod -Method Get -Uri "http://192.168.200.18:8080/api/v1/system.hostname"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "system.hostname": "A1580-device"
  }
}
```

### Successful POST Request
```bash
# Set sampling frequency to 12 MHz
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"value": "100"}' \
  "http://192.168.200.18:8080/api/v1/sampling_freq"
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://192.168.200.18:8080/api/v1/sampling_freq" -ContentType "application/json" -Body '{"value":100}'
```
or
```powershell
Invoke-RestMethod -Method Post -Uri 'http://192.168.200.18:8080/api/v1/sampling_freq' -ContentType 'application/json' -Body (@{ value = 100 } | ConvertTo-Json)
```


**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "sampling_freq": "100"
  }
}
```



### Error: Out of Range
```bash
# Try to set sampling frequency to invalid value (too high)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"value": "500"}' \
  "http://192.168.200.18:8080/api/v1/tvg_bypass"
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://192.168.200.18:8080/api/v1/tvg_bypass" -ContentType "application/json" -Body '{"value":500}'
```
or
```powershell
Invoke-RestMethod -Method Post -Uri 'http://192.168.200.18:8080/api/v1/tvg_bypass' -ContentType 'application/json' -Body (@{ value = 500 } | ConvertTo-Json)
```

**Response (400 Bad Request):**
```json
{
    "status":"error",
    "message":"Value out of valid range for parameter",
    "details":{
        "code":-2,
        "field":"tvg_bypass",
        "expected":"0 to 80",
        "received":"500"
        }
    }
```

### Error: Invalid Value (Not in List)
```bash
# Try to set TVG mode to invalid value
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"value": "INVALID"}' \
  "http://192.168.200.18:8080/api/v1/tvg_mode"
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://192.168.200.18:8080/api/v1/tvg_mode" -ContentType "application/json" -Body '{"value":"INVALID"}'
```
or
```powershell
Invoke-RestMethod -Method Post -Uri 'http://192.168.200.18:8080/api/v1/tvg_mode' -ContentType 'application/json' -Body (@{ value = 'INVALID' } | ConvertTo-Json)
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Invalid value for parameter",
  "details": {
    "code": -1,
    "field": "tvg_mode",
    "expected": "ON, BYPASS",
    "received": "INVALID"
  }
}
```

### Error: Missing Field
```bash
# POST request without required "value" field
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"wrong_field": "12000000"}' \
  "http://192.168.200.18:8080/api/v1/sampling_freq"
```

```powershell
Invoke-RestMethod -Method Post -Uri "http://192.168.200.18:8080/api/v1/sampling_freq" -ContentType "application/json" -Body '{"wrong_field":"12000000"}'
```
or
```powershell
Invoke-RestMethod -Method Post -Uri 'http://192.168.200.18:8080/api/v1/sampling_freq' -ContentType 'application/json' -Body (@{ wrong_field = '12000000' } | ConvertTo-Json)
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Missing or invalid 'value' field in request body",
  "details": {
    "code": -3,
    "field": "value",
    "expected": "JSON object with 'value' field",
    "received": "{\"wrong_field\": \"12000000\"}"
  }
}
```

### Error: Parameter Not Found
Try to access non-existent parameter
```bash
curl -X GET "http://192.168.200.18:8080/api/v1/nonexistent_param"
```
```powershell
Invoke-RestMethod -Method Get -Uri 'http://192.168.200.18:8080/api/v1/nonexistent_param'
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "parameter not found"
}
```

### Error: Missing Content-Length
```bash
# POST without Content-Length header (malformed request)
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Transfer-Encoding: chunked" \
  -d '{"value": "12000000"}' \
  "http://192.168.200.18:8080/api/v1/sampling_freq"
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "missing Content-Length header"
}
```

## CORS Support

The API includes CORS headers to allow cross-origin requests from web applications:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

## Implementation Details

- **Per-connection contexts:** Each REST client gets isolated SCPI state and buffers
- **TCP buffering:** Handles HTTP requests split across multiple TCP packets
- **cJSON library:** Uses cJSON for JSON serialization/parsing
- **Parameter validation:** Validates against protocol-defined ranges and allowed values
- **No authentication:** This implementation intentionally does not include authentication or authorization

## Troubleshooting

### 404 Not Found
- Verify REST API port is correct and matches device configuration
- Check that firmware was rebuilt and deployed after adding `rest_port` configuration
- Ensure path starts with `/api/v1/`

### Connection Refused
- Verify device is running and accessible at the specified IP
- Check that REST port matches configuration (default: 8080)
- Confirm firewall settings allow incoming connections

### Request Body Not Parsed
- Ensure `Content-Type: application/json` header is present
- Include `Content-Length` header (curl adds this automatically)
- Verify JSON body contains `"value"` field

### Value Rejected
- Check error response `details.expected` field for valid range or list
- Verify value matches expected data type (string vs number)
- Some parameters may be read-only (check `haveSetter` in protocol definition)

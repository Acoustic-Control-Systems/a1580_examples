# SCPI Command Reference

# Identification query *IDN?

**Description:**
Identifies the version of firmware that is loaded on the instrument

**Syntax:**
```
*IDN?
```

**Parameters:**
None

**Query Response:**
Manufacturer, Model, Serial number, Firmware version

**Example:**
```
> *IDN?
< ACS-Solutions GmbH,A1580-HF,100500,1.6.b41
```

# IEEE 488.2 Common Commands

The following common commands are registered by the SCPI implementation:

| Command | Description | Query response |
|---|---|---|
| `*CLS` | Clear the status data structures and error queue. | None |
| `*ESE <numeric>` | Set the Standard Event Status Enable register. | None |
| `*ESE?` | Query the Standard Event Status Enable register. | `<numeric>` |
| `*ESR?` | Query and clear the Standard Event Status register. | `<numeric>` |
| `*OPC` | Set the Operation Complete event when SCPI library operations finish; this does not confirm asynchronous acquisition or DMA completion. | None |
| `*OPC?` | Wait for SCPI library operations to finish; it does not confirm asynchronous acquisition or DMA completion. | `1` |
| `*RST` | Log a reset request; device settings are not reset. | None |
| `*SRE <numeric>` | Set the Service Request Enable register. | None |
| `*SRE?` | Query the Service Request Enable register. | `<numeric>` |
| `*STB?` | Query the Status Byte register. | `<numeric>` |
| `*TST?` | Registered stub; no self-test is run. | `0` |
| `*WAI` | Wait for SCPI library operations before processing subsequent commands; it does not confirm asynchronous acquisition or DMA completion. | None |

# SYSTem Subsystem

## Error message queue number

**Description:**
This method reads out error message queue.

**Syntax:**
```
SYSTem:ERRor[:NEXT]?
```

**Query Response:**
<numeric>,<string>

**Example:**
```
> SYSTem:ERRor?
< 0, "No error"
> SYSTem:ERRrr?
> SYSTem:ERRor?
-113,"Undefined header;Command: SYST:ERRrr"
```

## Error message queue count

**Description:**
Returns the number of queued SCPI errors without removing them.

**Syntax:**
```
SYSTem:ERRor:COUNt?
```

**Query Response:**
<numeric> - number of queued errors

**Example:**
```
> SYST:ERR:COUN?
< 0
```

## SCPI standard version

**Description:**
Returns the supported SCPI standard version. This is not the device firmware version; use *IDN? for firmware identity.

**Syntax:**
```
SYSTem:VERSion?
```

**Query Response:**
SCPI standard version

**Example:**
```
> SYST:VERS?
< 1999.0
```

# SOURce Subsystem

## Sampling rate
**Description:**
This property gets or sets frequency in Hz for AD conversion of the input signal.

**Syntax:**
```
[SOURce:]FREQuency <numeric|char>
[SOURce:]FREQuency?
```

**Parameters:**
<numeric> {1 | 2 | 5 | 10 | 25 | 50 | 100} in MHz
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 1 MHz
- MAXimum - 100 MHz
- DEFault - 100 MHz
- UP - advances to the next value in the supported list
- DOWN - returns to the previous value in the supported list

**Query Response:**
<numeric> in Hz

**Example:**
```
> FREQ 100 MHZ
> FREQ?
< 100000000
```

## Acquired data length

**Description:**
This property gets or sets number of samples in an acquired data vector.

**Syntax:**
```
[SOURce:]DATA:LENGth <numeric|char>
[SOURce:]DATA:LENGth?
```

**Parameters:**
<numeric> = {1024 to 36864}
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 1024
- MAXimum - 36864
- DEFault - 1024
- UP - increases the current value by 1
- DOWN - decreases the current value by 1

**Query Response:**
<numeric>

**Example:**
```
> DATA:LENG 1024
> DATA:LENG?
< 1024
```

## Data port number

**Description:**
This property gets the TCP port number for data transfer. The command is used to establish a connection for data transfer between the instrument and a controlling device.
After starting acquisition, the instrument will send acquired data to the controlling device via TCP connection to the specified port. The controlling device should establish a connection to the instrument using this port number before starting acquisition. The command is used in combination with Start acquisition and Stop acquisition commands.

**Syntax:**
```
DATA:PORT?
```

**Example:**
```
> DATA:PORT?
< 2758
```

**Query Response:**
<numeric> in range from 0 to 65535

## Operating mode

**Description:**
Selects whether the instrument operates as the master or as a slave device.

**Syntax:**
```
[:SOURce]:MODE <char>
[:SOURce]:MODE?
```

**Parameters:**
`<char> = {MASTer | SLAVe}`

**Query Response:**
`{MASTer | SLAVe}`

**Example:**
```
> MODE MASTER
> MODE?
< MASTER
```

## Transmitter enable

**Description:**
This property defines if the transmitter generates pulse

**Syntax:**
```
[SOURce:]TRANsmitter:ENABle <char>
[SOURce:]TRANsmitter:ENABle?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}
- DEFault - OFF

- OFF or 0 – no pulse will be generated.
- ON or 1 – pulse will be generated according to other transmitter settings (amplitude, polarity, duration, frequency).

**Query Response:**
{0 | 1}

**Example:**
```
> TRAN:ENAB ON
> TRAN:ENABLE?
< 1
```

## Transmitter type

**Description:**
This property defines the type of transducer used with the instrument.

**Syntax:**
```
[SOURce:]TRANsmitter:TYPE <char>
[SOURce:]TRANsmitter:TYPE?
```

**Parameters:**
<char> = {DUAL | SINGle}
- DEFault - DUAL
- DUAL - Dual-crystal transducer or trough transmission. Pulse burst will be generated at the “OUT” socket of A1580.
- SINGle - Single-crystal transducer. Pulse burst will be generated at the “IN” socket of A1580.

**Query Response:**
{DUAL | SINGle}

The getter can also return DIAGnostic if diagnostic routing was selected through another protocol. The SCPI setter accepts only DUAL and SINGle.

**Example:**
```
> TRAN:TYPE DUAL
> TRAN:TYPE?
< DUAL
```

## Transmitter polarity mode

**Description:**
This property defines the initial polarity of the pulse burst generated at the transducer output

**Syntax:**
```
[SOURce:]TRANsmitter:REVerse <char>
[SOURce:]TRANsmitter:REVerse?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}
- DEFault - OFF
- OFF or 0 – the burst starts with the positive pulse.
- ON or 1 – the burst starts with the negative pulse.

**Query Response:**
{0 | 1}

**Example:**
```
> TRAN:REV ON
> TRAN:REV?
< 1
```

## Transmitter pulse amplitude 

**Description:**
This property sets or gets an amplitude in volts for a pulse burst sent to a transmitting transducer.

**Syntax:**
```
[SOURce:]TRANsmitter:PULSe[:LEVel] <numeric|char>
[SOURce:]TRANsmitter:PULSe[:LEVel]?
```

**Parameters:**
<numeric> = {5 ... 200}
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 5 V
- MAXimum - 200 V
- DEFault - 20 V
- UP - increases the current value by 5 V
- DOWN - decreases the current value by 5 V

**Query Response:**
<numeric> in volts

**Example:**
```
> TRANsmitter:PULS 20 V
> TRANsmitter:PULSe?
< 20
```

## Transmitter burst frequency

**Description:**
This property sets or gets the frequency in hertz for a pulse burst sent to a transmitting transducer.

**Syntax:**
```
[SOURce:]TRANsmitter:FREQuency <frequency|char>
[SOURce:]TRANsmitter:FREQuency?
```

**Parameters:**
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
<frequency> = {10 to 20000 KHZ}
- MINimum - 10 KHZ
- MAXimum - 20 MHZ
- DEFault - 5 MHZ
- UP - increases the actual value by 1 KHZ
- DOWN - decreases the actual value by 1 KHZ

**Query Response:**
<frequency> in hertz

**Example:**
```
> TRAN:FREQ 100 KHZ
> TRAN:FREQ?
< 100000
```

## Transmitter burst duration

**Description:**
This property sets or gets number of periods in transmitter burst.

**Syntax:**
```
[SOURce:]TRANsmitter:DURation {numeric|char}
[SOURce:]TRANsmitter:DURation?
```

**Parameters:**
<numeric> = {0.5 to 16}
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 0.5
- MAXimum - 16
- DEFault - 1
- UP - increases the current value by 0.5
- DOWN - decreases the current value by 0.5

**Query Response:**
<numeric>

**Example:**
```
> TRAN:DUR 5
> TRAN:DUR?
< 5
```

## Acquisition triggering mode

**Description:**
This property is used to choose which event initiates an acquisition.

**Syntax:**
```
[SOURce:]TRIGgering:MODE <char>
[SOURce:]TRIGgering:MODE?
```

**Parameters:**
<char> = {INTernal | CTP | ENCoder | TTL}
- INTernal – Periodic mode with internal triggering: One acquisition will be performed every Triggering Interval seconds.
- CTP - CTP trigger input.
- ENCoder - Encoder trigger input (SENSOR in the REST/internal protocol).
- TTL - External TTL trigger input.

**Query Response:**
{INTernal | CTP | ENCoder | TTL}

**Example:**
```
> TRIG:MODE INT
> TRIG:MODE?
< INTernal
```

## Trigger delay

**Description:**
Sets or gets the delay between a trigger and the start of acquisition. Hardware uses 10 ns ticks. Unlike averaging delay queries, this query returns an integer in nanoseconds.

**Syntax:**
```
[SOURce:]TRIGgering:DELay <time|char>
[SOURce:]TRIGgering:DELay?
```

**Parameters:**
<time> = {0 to 2147483647} NS
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 0 NS
- MAXimum - 2147483647 NS
- DEFault - 15000 NS
- UP/DOWN - changes the value by 1 NS

**Query Response:**
<numeric> in nanoseconds

**Example:**
```
> TRIG:DEL 15 US
> TRIG:DEL?
< 15000
```

## Periodic acquisition interval

**Description:**
This property sets or gets time in seconds between two consecutive acquisition in periodic (INTERNAL) mode.

**Syntax:**
```
[SOURce:]TRIGgering:INTerval <time|char>
[SOURce:]TRIGgering:INTerval?
```

**Parameters:**
<time> = {10 to 2147483647} US
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}

- MINimum - 10 US
- MAXimum - 2147483647 US
- DEFault - 1000 US
- UP - increases the current value by 1 US
- DOWN - decreases the current value by 1 US

**Query Response:**
<time> in seconds

**Example:**
```
> TRIG:INT 100000 US
> TRIG:INT?
< 100.0E-3
```

## Start acquisition

**Description:**
Method will start a single acquisition or a sequence of acquisitions

**Syntax:**
```
[SOURce:]STARt <char>
```

**Parameters:**
<char> = {AUTO}

**Example:**
```
>SOUR:STAR AUTO
>STAR AUTO
```

## Stop acquisition

**Description:**
The method is used to stop a sequence of measurements. Stop is not needed in the single ascan mode.

**Syntax:**
```
[SOURce:]STOP
```

**Example:**
```
>SOUR:STOP
>STOP
```

## Constant gain at input

**Description:**
This property sets or gets analog amplification in decibels

**Syntax:**
```
[SOURce:]GAIN[:LEVel] <numeric | char>
[SOURce:]GAIN?
```

**Parameters:**
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
<numeric> {0 to +80 dB}
- MINimum - 0 dB
- MAXimum - +80 dB
- DEFault - 0 dB
- UP - increases the current value by 1 dB
- DOWN - decreases the current value 1 dB

**Query Response:**
<numeric> in decibel

**Example:**
```
> GAIN:LEV 10 DB
> GAIN?
< 10
```

## Combined preamplifier

**Description:**
Enables or disables the +20 dB preamplifier for the combined (single-crystal) signal path. GAIN? reports programmable gain without the additional preamplifier gain. Changing transmitter type can switch the active preamplifier path.

**Syntax:**
```
[SOURce:]GAIN:PREamp:COMBined <char>
[SOURce:]GAIN:PREamp:COMBined?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}
- DEFault - OFF

**Query Response:**
{0 | 1}

**Example:**
```
> GAIN:PRE:COMB ON
> GAIN:PRE:COMB?
< 1
```

## Split preamplifier

**Description:**
Enables or disables the +20 dB preamplifier for the split (dual-crystal) signal path. GAIN? reports programmable gain without the additional preamplifier gain. Changing transmitter type can switch the active preamplifier path.

**Syntax:**
```
[SOURce:]GAIN:PREamp:SPLIT <char>
[SOURce:]GAIN:PREamp:SPLIT?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}
- DEFault - OFF
- SPLIT requires the full five-letter command header.

**Query Response:**
{0 | 1}

**Example:**
```
> GAIN:PRE:SPLIT ON
> GAIN:PRE:SPLIT?
< 1
```

## Transmitter damping

**Description:**
This property enables or disables the pulse damping

**Syntax:**
```
[SOURce:]TRANsmitter:DAMP[:ENABle] <char>
[SOURce:]TRANsmitter:DAMP[:ENABle]?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}
- DEFault - OFF
- OFF or 0 – the damping is disabled
- ON or 1 – the damping is enabled

**Query Response:**
{ 0 | 1}

**Example:**
```
> TRAN:DAMP ON
> TRAN:DAMP?
< 1
```

## Transmitter pulse gap

**Description:**
Sets or gets the pulser gap. Hardware uses 5 ns resolution; the query returns an integer in nanoseconds.

**Syntax:**
```
[SOURce:]TRANsmitter:GAP <time|char>
[SOURce:]TRANsmitter:GAP?
```

**Parameters:**
<time> = {0 to 500} NS
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 0 NS
- MAXimum - 500 NS
- DEFault - 5 NS
- UP/DOWN - changes the value by 5 NS

**Query Response:**
<numeric> in nanoseconds

**Example:**
```
> TRAN:GAP 5 NS
> TRAN:GAP?
< 5
```

## Transmitter damping gap

**Description:**
Sets or gets the damping gap, independently of damping enable. Hardware uses 5 ns resolution. Setting the gap requires super-pulser hardware support; enable damping separately with TRAN:DAMP ON.

**Syntax:**
```
[SOURce:]TRANsmitter:DAMP:GAP <time|char>
[SOURce:]TRANsmitter:DAMP:GAP?
```

**Parameters:**
<time> = {10 to 500} NS
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 10 NS
- MAXimum - 500 NS
- DEFault - 10 NS
- UP/DOWN - changes the value by 5 NS

**Query Response:**
<numeric> in nanoseconds

**Example:**
```
> TRAN:DAMP:GAP 100 NS
> TRAN:DAMP:GAP?
< 100
```

## Input impedance

**Description:**
This property sets/gets the input impedance in Ohms

**Syntax:**
```
[SOURce:]TRANsmitter:IMPedance <char>
[SOURce:]TRANsmitter:IMPedance?
```

**Parameters:**
<char> = {HIGH | 200 | 1000}
- DEFault - HIGH
- HIGH - the input impedance is set to HIGH_Z
- 200 - the input impedance is set to 200 Ohm
- 1000 - the input impedance is set to 1000 Ohm

**Query Response:**
{HIGH | 200 | 1000}

**Example:**
```
> TRAN:IMP HIGH
> TRAN:IMP?
< HIGH
```

## TGC Mode

**Description:**
This property sets/gets if and how TGC (Time Gain Compensation) will be applied to the ascan

**Syntax:**
```
[SOURce:]GAIN:TGC:MODE <char>
[SOURce:]GAIN:TGC:MODE?
```

**Parameters:**
<char> = {OFF | LINear | ARBitrary}
- DEFault - OFF
- OFF - the TGC is off, constant gain is applied
- LINear - TGC  is defined by linear function meaning the gain increases proportionally with time (or depth)(see Linear TGC command)
- ARBitrary - TCG is configured using multiple gain levels at specified time points (see Arbitrary TGC command)

**Query Response:**
{OFF | LINear | ARBitrary}

**Example:**
```
> GAIN:TGC:MODE OFF
> GAIN:TGC:MODE?
< OFF
```

### Linear TGC

**Description:**
This property sets/gets parameters of TGC defined by linear function  (see TGC Mode)

**Syntax:**
```
[SOURce:]GAIN:TGC:LINear <float array>
[SOURce:]GAIN:TGC:LINear?
```

**Parameters:**
<float array> - list of 2 values separated by comma:
- offset (in µs),
- slope (dB/µs)

Offset must be nonnegative. The firmware stores it as an integer in microseconds, truncating fractional offsets. Writing coefficients does not select LINear mode; set TGC Mode separately.

Time Gain Compensation (TGC) consists of two segments:
- Constant Gain Segment: From 0 to offset microseconds (µs), the gain remains constant at a level defined via Constant gain at input .
- Linear Gain Segment: After the offset point, the gain changes linearly with time. The rate of this increase is defined by the parameter slope. The slope can be positive, negative or zero. If the slope is zero, the constant gain will be set for the whole range.
- Constant Gain Segment: If the gain slope reached system maximum or minimum value, the rest of the TGC range will be filled with the corresponding value (see Constant gain at input for the limits).
This configuration allows for precise control of signal amplification compensating for tissue attenuation.

**Query Response:**
The same as input for this command

**Example:**
```
> GAIN:TGC:LINear 20, 0.1
> GAIN:TGC:LINear?
< 20.0, 0.1
```

### Arbitrary TGC

**Description:**
This property sets/gets parameters of TGC configured by multiple gain levels at specified time points (see TGC Mode)

**Syntax:**
```
[SOURce:]GAIN:TGC:ARBitrary <float array>
[SOURce:]GAIN:TGC:ARBitrary?
```

**Parameters:**
<float array> – A comma-separated list of 2×N float values, where each pair of consecutive values represents a point on a TGC (Time Gain Compensation) curve. Each pair consists of:
- Time (in microseconds)
- Gain (in dB)
The format is: time1, gain1, time2, gain2, ..., timeN, gainN
The firmware accepts at most 128 points, sorts them by time and removes duplicate times. Writing points does not select ARBitrary mode; set TGC Mode separately.
The gain values will be added to a constant gain defined via Constant gain at input.
E.g. user has set constant gain to 40dB and sets a TGC array
10,5,20,10
The effective gain will be applied as:
- from 0µs to 10µs the device will use constant gain 40dB
- from 10µs to 20µs the device will hold gain at 45dB (40+5dB); this firmware uses steps, not linear interpolation
- from 20µs to the rest of the TGC range the device will use a gain 50dB

**Query Response:**
The same as input for this command

**Example:**
```
> GAIN:TGC:ARBitrary 0,5,2,20,5,20,10,40,30,10
> GAIN:TGC:ARBitrary?
< 0,5,2,20,5,20,10,40,30,10
```

# MEMory Subsystem

## Clean internal data buffers

**Description:**
Clean internal buffers

**Syntax:**
```
MEMory:CLEar
```

**Example:**
```
> MEM:CLE
```

# SENSe Subsystem

## Acquisitions per averaged vector

**Description:**
A1580 can perform several pulses/acquisitions in a row and internally calculate an averaged vector from the results. This setting is an exponent N: each vector averages 2^N acquisitions. Zero disables averaging (one acquisition); eight averages 256 acquisitions.

**Syntax:**
```
[SENSe:]AVERage[:COUNt] <numeric|char>
[SENSe:]AVERage[:COUNt]?
```

**Parameters:**
<numeric> = {0 ... 8}
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- DEFault - 0
- UP/DOWN - changes the exponent by 1

**Query Response:**
<numeric>

**Example:**
```
> SENS:AVER:COUNT 5
> SENS:AVER:COUNT?
< 5
```

## Automatic constant averaging delay

**Description:**
Enables automatic calculation of the constant averaging delay for internal triggering. The firmware calculates the delay in nanoseconds as trigger_interval_us * 1000 / 2^N - random_delay_ns - 100000 + 31250, limited to 0..2147483647, where N is the averaging exponent. Changes to trigger interval, averaging exponent or random delay recalculate it.
Enabling AUTO for a non-internal trigger source is rejected by the internal protocol. Changing the source away from internal disables AUTO. Setting AUTO OFF resets the manual delay to 10000 NS; it does not retain the calculated value.

Automatic selection chooses the constant averaging delay for the user using an experience-based timing calculation that covers many common inspection cases. Its purpose is to reduce ghost signals caused by repeated ultrasonic reflections from previous shots appearing in subsequent acquisitions.

**Syntax:**
```
[SENSe:]AVERage:DELay:CONStant:AUTO <char>
[SENSe:]AVERage:DELay:CONStant:AUTO?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}

**Query Response:**
{0 | 1}

**Example:**
```
> SENS:AVER:DEL:CONS:AUTO ON
> SENS:AVER:DEL:CONS:AUTO?
< 1
```

## Constant averaging interval

**Description:**
This property is defined in seconds and gets or sets a constant part of an interval between acquisitions in averaging mode.
In A1580 averaging mode, this is the constant delay within the acquisition sequence. Hardware uses 10 ns ticks. Manual writes are rejected while automatic constant delay is enabled with SCPI error -221, "Settings conflict"; disable Automatic constant averaging delay before setting a manual value.

This delay helps eliminate ghost signals: an ultrasonic wave can reflect repeatedly within the specimen, allowing echoes from a previous shot to appear in the next acquisition. Select averaging delays according to specimen thickness, pulse repetition rate (PRR), and acquired vector length.

**Syntax:**
```
[SENSe:]AVERage:DELay:CONStant[:VALue] <time|char>
[SENSe:]AVERage:DELay:CONStant[:VALue]?
```

**Parameters:**
<time> = {0 to 2147483647} NS
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}

- MINimum - 0 NS
- MAXimum - 2147483647 NS
- DEFault - 10 US
- UP - increases the current value by 1 NS
- DOWN - decreases the current value by 1 NS

**Query Response:**
<time> in seconds

**Example:**
```
> SENS:AVER:DEL:CONS:AUTO OFF
> SENSe:AVERage:DELay:CONStant 50 US
> SENSe:AVERage:DELay:CONStant?
< 50.0E-6
```

## Random averaging interval

**Description:**
This property is defined in seconds and gets or sets a random part of an interval between acquisitions in averaging mode.
In A1580 averaging mode, this sets the random-delay range within the acquisition sequence. Hardware uses 10 ns ticks. Changing this value recalculates the constant delay when automatic constant delay is enabled.

Varying the delay between shots helps reduce ghost signals from repeated reflections of previous shots when averaging acquisitions. Select this range together with the constant delay according to specimen thickness, pulse repetition rate (PRR), and acquired vector length.

**Syntax:**
```
[SENSe:]AVERage:DELay:RANDom <time|char>
[SENSe:]AVERage:DELay:RANDom?
```

**Parameters:**
<time> = {0 to 32767} NS
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}

- MINimum - 0 NS
- MAXimum - 32767 NS
- DEFault - 2 US
- UP - increases the current value by 1 NS
- DOWN - decreases the current value by 1 NS

**Query Response:**
<time> in seconds

**Example:**
```
> SENSe:AVER:DEL:RAND 2 US
> SENSe:AVER:DEL:RAND?
< 2.0E-6
```

## Analog high-pass filter index

**Description:**
This property selects an analog filter at the input of A1580. The command takes an index as a parameter. The table below shows the firmware's default mapping between index and filter frequency.

**Syntax:**
```
[SENSe:]FILTer:HPASs:INDex <char>
[SENSe:]FILTer:HPASs:INDex?
```

**Parameters:**
<char> = {0 | 1 | 2 | 3}

| Index | Cut-off frequency (kHz) |
|---|---|
| 0 | 1 |
| 1 | 100 |
| 2 | 500 |
| 3 | 1000 |

**Query Response:**
<char>

**Example:**
```
> SENS:FILT:HPASs:INDex 1
> SENS:FILT:HPASs:INDex?
< 1
```

# IEEE common commands

## Status registers and clear status

**Description:**
Controls and reads the SCPI library's status registers and error queue.

**Syntax:**
```
*CLS
*ESE <numeric>
*ESE?
*ESR?
*SRE <numeric>
*SRE?
*STB?
```

**Parameters:**
<numeric> = {0 to 255} - status-register bit mask for *ESE and *SRE

**Query Response:**
- *ESE? - standard event status enable mask.
- *ESR? - standard event status register; reading clears it.
- *SRE? - service request enable mask.
- *STB? - status byte.
- *CLS clears status and the error queue; it has no query response.

**Example:**
```
> *CLS
> *ESE 1
> *ESE?
< 1
```

## Operation complete and wait

**Description:**
Provides the SCPI library's operation-complete and wait commands. They do not verify that asynchronous A1580 acquisition or DMA has finished.

**Syntax:**
```
*OPC
*OPC?
*WAI
```

**Query Response:**
*OPC? returns 1. *OPC sets the operation-complete event; *WAI has no query response.

**Example:**
```
> *OPC?
< 1
```

## Reset and self-test

**Description:**
These commands are registered in the firmware, but *RST only logs a reset request and does not restore device settings. *TST? is a stub that returns zero.

**Syntax:**
```
*RST
*TST?
```

**Query Response:**
*TST? returns 0. *RST has no query response.

**Example:**
```
> *TST?
< 0
```


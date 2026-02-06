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

# SYSTem Subsystem

## Error message queue number

**Description:**
This method reads out error message queue.

**Syntax:**
```
SYSTem:ERRor?
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
- DEFault - 1 MHz
- UP - increases the current value
- DOWN - decreases the current value

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
< 5025
```

**Query Response:**
<numeric> in range from 0 to 65535

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
{OFF | ON }

**Example:**
```
> TRAN:ENAB ON
> TRAN:ENABLE?
< ON
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
- DEFault -  SINGle
- DUAL - Dual-crystal transducer or trough transmission. Pulse burst will be generated at the “OUT” socket of A1580.
- SINGle - Single-crystal transducer. Pulse burst will be generated at the “IN” socket of A1580.

**Query Response:**
{DUAL | SINGle}

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
[SOURce:]TRANsmitter:REVerse ?
```

**Parameters:**
<char> = {OFF | ON | 0 | 1}
- DEFault - OFF
- OFF or 0 – the burst starts with the positive pulse.
- ON or 1 – the burst starts with the negative pulse.

**Query Response:**
{OFF | ON | 0 | 1}

**Example:**
```
> TRAN:REV ON
> TRAN:REV?
< ON
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
<numeric> = {5 ... 100}
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 5 V
- MAXimum - 100 V
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

## Transmitter burst period

**Description:**
This property sets or gets the period in seconds for a pulse burst sent to a transmitting transducer.

**Syntax:**
```
[SOURce:]TRANsmitter:PERiod <time|char>
[SOURce:]TRANsmitter:PERiod?
```

**Parameters:**
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
<time> = {10 to 250 NS}
- MINimum - 10 NS
- MAXimum - 250 NS
- DEFault - 140 NS
- UP - increases the current value by 10 NS
- DOWN - decreases the current value by 10 NS

**Query Response:**
<time> in seconds

**Example:**
```
> TRAN:PER 200 NS
> TRAN:PER?
< 200E-9
```

## Acquisition triggering mode

**Description:**
This property is used to choose which event initiates an acquisition.

**Syntax:**
```
[SOURce:]TRIGgering:MODe <char>
[SOURce:]TRIGgering:MODe?
```

**Parameters:**
<char> = {INTernal}
- INTernal – Periodic mode with internal triggering: One acquisition will be performed every Triggering Interval seconds.

**Query Response:**
{INTernal}

**Example:**
```
> TRIG:MODE INT
> TRIG:MODE?
< INT
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
<time> = {100 US to 10 s}
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}

- MINimum - 100 US
- MAXimum - 10 S
- DEFault - 10 MS
- UP - increases the current value by 100 US
- DOWN - decreases the current value by 100 US

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
[SOURce]:STARt <char>
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

## ADC sampling rate

**Description:**
This property gets or sets frequency in Hz for AD conversion of the input signal.

**Syntax:**
```
[SOURce:]FREQuency <numeric|char>
[SOURce:]FREQuency?
```

**Parameters:**
<numeric> { 1 | 2 | 5 | 10 | 25 | 50 | 100} in MHz
<char> = {MINimum | MAXimum | DEFault | UP | DOWN}
- MINimum - 1 MHz
- MAXimum - 100 MHz
- DEFault - 100 MHz
- UP - increases the current value (next in the list)
- DOWN - decreases the current value (previous in the list)

**Query Response:**
<numeric> in Hz

**Example:**
```
> FREQ 100 MHZ
> FREQ?
< 100000000
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

## Transmitter damping

**Description:**
This property enables or disables the pulse damping

**Syntax:**
```
[SOURce]:TRANsmitter:DAMP[:ENABle] <char>
[SOURce]:TRANsmitter:DAMP[:ENABle]?
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
< 0
```

## Input impedance

**Description:**
This property sets/gets the input impedance in Ohms

**Syntax:**
```
[SOURce]:TRANsmitter:IMPedance <char>
[SOURce]:TRANsmitter:IMPedance?
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
[:SOURce]:GAIN:TGC:MODE <char>
[:SOURce]:GAIN:TGC:MODE?
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
[:SOURce]:GAIN:TGC:LINear <float array>
[:SOURce]:GAIN:TGC:LINear?
```

**Parameters:**
<float array> - list of 2 values separated by comma:
- offset (in µs),
- slope (dB/µs)

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
[:SOURce]:GAIN:TGC:ARBitrary <float array>
[:SOURce]:GAIN:TGC:ARBitrary?
```

**Parameters:**
<float array> – A comma-separated list of 2×N float values, where each pair of consecutive values represents a point on a TGC (Time Gain Compensation) curve. Each pair consists of:
- Time (in microseconds)
- Gain (in dB)
The format is: time1, gain1, time2, gain2, ..., gainN, timeN
The gain values will be added to a constant gain defined via Constant gain at input.
E.g. user has set constant gain to 40dB and sets a TGC array
10,5,20,10
The effective gain will be applied as:
- from 0µs to 10µs the device will use constant gain 40dB
- from 10µs to 20µs the device will linearly increase gain from 45dB to 50dB (40+5dB to 40+10dB)
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
<%INSTR%> can perform several pulses/acquisitions in a row and internally calculate an averaged vector from the results, when Acquisitions per averaged vector > 0.

**Syntax:**
```
SENSe:AVERage:COUNt <numeric>
SENSe:AVERage:COUNt?
```

**Parameters:**
<numeric> = {0 ... 8}

**Query Response:**
<numeric>

**Example:**
```
> SENS:AVER:COUNT 5
> SENS:AVER:COUNT?
< 5
```

## Constant averaging interval

**Description:**
This property is defined in seconds and gets or sets a constant part of an interval between acquisitions in averaging mode.
When A1570 performs several pulses/acquisitions in a row for the following averaging, a pause will take place after an acquisition is finished. It is calculated as FixedDelay + Constant averaging interval + RandomInterval, where FixedDelay is a hardware delay of 22μs and  RandomInterval is a random number in a range from 0 to Random averaging interval.

**Syntax:**
```
[SENSe:]AVERage:PERiod<time|char>
[SENSe:]AVERage:PERiod?
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
> SENSe:AVERage:PERiod 50 US
> SENSe:AVERage:PERiod?
< 50.0E-6
```

## Random averaging interval

**Description:**
This property is defined in seconds and gets or sets a random part of an interval between acquisitions in averaging mode.
When A1570 performs several pulses/acquisitions in a row for the following averaging a pause will take place after an acquisition is finished. It is calculated as FixedDelay + Constant averaging interval + RandomInterval, where FixedDelay is a hardware delay of 22μs and  RandomInterval is a random number in a range from 0 to Random averaging interval.

**Syntax:**
```
[SENSe:]AVERage:PERiod:RANDom <time|char>
[SENSe:]AVERage:PERiod:RANDom?
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
> SENSe:AVER:PER:RAND 2 US
> SENSe:AVER:PER:RAND?
< 2.0E-6
```

## Analog high-pass filter index

**Description:**
This property selects an analog filter at the input of %INSTR%.The command takes an index as a parameter. The table below sets correspondance between the index value and the filter frequency

**Syntax:**
```
[:SENSe]:FILTer:HPASs:INDex <char>
[:SENSe]:FILTer:HPASs:INDex
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
> SENS:FILT:HPASs:INDex
< 1
```


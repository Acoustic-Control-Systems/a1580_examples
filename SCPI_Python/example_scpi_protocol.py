import sys
import time
import matplotlib.pyplot as plt
import pyvisa as visa
from pyvisa.resources import Resource
import logging
import socket
import threading

from common_functions import *
from struct import unpack

def set_parameters(inst:Resource, data_length):
    # set sampling freq
    inst.write('FREQ 100 MHZ')
    samp_freq:str = inst.query('FREQ?')
    logger.info(f"Sampling frequency: {int(samp_freq)/1e6} MHz")

    # set ascan length (samples)
    inst.write(f'DATA:LENG {data_length}')
    length: str = inst.query('DATA:LENG?')
    logger.info(f"Data length: {length} samples")

    #set transmitter frequency
    inst.write('TRAN:FREQ 2500 KHz')
    trans_freq: str = inst.query('TRAN:FREQ?')
    trans_freq_int = int(trans_freq)
    logger.info(f"Transmitter frequency: {trans_freq_int/1000} kHz")

    #set tramsmitter pulse amplitude
    inst.write('TRAN:PULS 100 V')
    trans_pulse: str = inst.query('TRAN:PULS?')
    logger.info(f"Transmitter pulse amplitude: {trans_pulse} V")

    #enable transmitter
    inst.write('TRAN:ENAB ON')
    trans_enabled: str = inst.query('TRAN:ENAB?')
    logger.info(f"Transmitter enabled: {trans_enabled}")

    #set transmitter halfperiods? number 
    inst.write('TRAN:DUR 1')
    trans_periods: str = inst.query('TRAN:DUR?')
    logger.info(f"Transmitter duration: {trans_periods}")

    #reverse polarity off
    inst.write('TRAN:REVerse OFF')
    trans_reverse_polarity: str = inst.query('TRAN:REVerse?')
    logger.info(f"Transmitter reverse polarity: {trans_reverse_polarity}")

    #enable transmitter damp
    inst.write('TRAN:DAMP:ENAB ON')
    trans_damp_enabled: str = inst.query('TRAN:DAMP:ENAB?')
    logger.info(f"Transmitter damping enabled: {trans_damp_enabled}")

    # set transmitter type to single
    inst.write('TRAN:TYPE SINGle') 
    tran_type:str = inst.query('TRAN:TYPE?')
    logger.info(f"Transmitter type: {tran_type}")

    #set constant gain value
    inst.write('GAIN 10')
    gain_level: str = inst.query('GAIN?')
    logger.info(f"Gain level: {gain_level} dB")

    #set gain mode to constant gain
    inst.write('GAIN:TGC:MODE OFF')
    tgc_mode: str = inst.query('GAIN:TGC:MODE?')
    logger.info(f"TGC mode: {tgc_mode}")

    #accumulations 
    inst.write('AVER:COUN 0')
    aver_count: str = inst.query('AVER:COUN?')
    logger.info(f"Averaging count: {aver_count}")

    #trigger mode
    inst.write('TRIG:MODE INTERNAL')
    trig_mode: str = inst.query('TRIG:MODE?')
    logger.info(f"Trigger mode: {trig_mode}")

    # set trigger interval to 1/10 s
    inst.write('TRIG:INT 100000 US')
    trig_int: str = inst.query('TRIG:INT?')
    logger.info(f"Trigger interval: {trig_int} s")
    
    #impedance
    inst.write('TRAN:IMP 200')
    impedance: str = inst.query('TRAN:IMP?')
    logger.info(f"Impedance: {impedance}")

    #master mode
    inst.write('MODE MASTer')
    mode: str = inst.query('MODE?')
    logger.info(f"Device mode: {mode}")

    #set trigger delay to 0 ns
    inst.write('TRIG:DEL 0 NS')
    trigger_delay: str = inst.query('TRIG:DEL?')
    logger.info(f"Trigger delay: {trigger_delay} s")

    #constant delay mode
    inst.write('AVERage:DELay:CONStant:AUTO ON')
    constant_delay_auto: str = inst.query('AVERage:DELay:CONStant:AUTO?')
    logger.info(f"Constant delay auto: {constant_delay_auto}")

    constant_delay: str = inst.query('AVERage:DELay:CONStant?')
    logger.info(f"Constant delay: {constant_delay} s")

    #random delay
    inst.write('AVERage:DELay:RANDom 2000 NS')
    random_delay: str = inst.query('AVERage:DELay:RANDom?')
    logger.info(f"Random delay: {random_delay} s")

    #debug parameters
    #zonder gap
    inst.write('TRAN:GAP 5 NS')
    trans_gap: str = inst.query('TRAN:GAP?')
    logger.info(f"Transmitter gap: {trans_gap} ns")

    #zonder damp gap
    inst.write('TRAN:DAMP:GAP 30 NS')
    trans_damp_gap: str = inst.query('TRAN:DAMP:GAP?')
    logger.info(f"Transmitter damp gap: {trans_damp_gap} ns")

def set_tgc_linear_mode(inst: Resource, offset: float, slope: float):

    # configure linear tgc: slope in dB/us, offset in us
    inst.write(f'SOURce:GAIN:TGC:LINear {offset}, {slope}')
    answ = inst.query(f'SOURce:GAIN:TGC:LINear?')

    parts = answ.split(",")
    assert len(parts) == 2, 'Wrong getting linear tgc answer'
    triple = tuple(map(float, parts))

    assert (offset, slope) == triple, f'An error in tgc setter/getter Sent {(offset, slope)}. Revceived: {triple}'
    
    # set tgc mode to linear
    inst.write(f'SOURce:GAIN:TGC:MODE LINear')
    mode = inst.query('SOURce:GAIN:TGC:MODE?')
    assert mode == 'LINear', f'Error setting tgc mode to linear. Received: {mode}'
    logger.info(f'TGC mode: {mode}')

def set_tgc_arbitrary_mode(inst: Resource, time_points: list, gain_points: list):
    # from lists to string time,gain,time,gain,...
    params = ",".join(f"{x},{y}" for x, y in zip(time_points, gain_points))

    # configure arbitrary tgc curve
    inst.write(f'SOURce:GAIN:TGC:ARBitrary {params}')

    answ = inst.query(f'SOURce:GAIN:TGC:ARBitrary?')
    logger.info(f'TGC arbitrary curve from device {answ}')
    
    # set tgc mode to arbitrary
    inst.write(f'SOURce:GAIN:TGC:MODE ARBitrary')
    mode = inst.query(f'SOURce:GAIN:TGC:MODE?')
    assert mode == 'ARBitrary', f'Error setting tgc mode to arbitrary. Received: {mode}'
    logger.info(f'TGC mode: {mode}')

    
def unpack_and_plot_data(data):
    if not data:
        logger.info("No data to unpack and plot.")
        return
    ascans={}
    for i in range(len(data)):
        shorts = unpack('<'+'h'*(len(data[i])//2),data[i]) #convert to 2byte values
        ascans[i] = shorts[14:] #cut the header
        plt.plot(ascans[i])



logger = logging.getLogger()
logger.level = logging.INFO

stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)
logger.info('Start SCPI communication on A1580...')

ip: str = '192.168.200.18'
cmd_port: int = 5025    #scpi command port
data_port: int = 2758   #data port

rm = visa.ResourceManager()
inst = rm.open_resource(f'tcpip::{ip}::{str(cmd_port)}::SOCKET')
inst.encoding = 'iso-8859-1'
inst.timeout = 5000 # miliseconds
inst.read_termination = '\r\n'
inst.write_termination = '\r\n'

#readout error queue before start
while True:
    err_num, err_msg = read_error_queue(inst)
    if (err_num == 0):
        break

#get id string from the device
idn: str = inst.query('*IDN?')
logger.info(idn)


#stop any previously started measurements
inst.write('STOP')

#clear device memory
inst.write('MEM:CLEar')

#vector length in samples to be measured
data_length = 8*1024

#program device
set_parameters(inst, data_length)

do_use_linear_tgc = False # True to use linear tgc
# set tgc mode to linear with 10us offset and 0.22 dB/us slope
if do_use_linear_tgc:
    set_tgc_linear_mode(inst, 10, 0.22)
    
do_use_arbitrary_tgc = False # True to use arbitrary tgc
# set tgc mode to arbitrary with given points
if do_use_arbitrary_tgc:
    time_points = [0, 2, 5, 10, 30]
    dbs = [5, 20, 20, 40, 10]
    set_tgc_arbitrary_mode(inst, time_points, dbs)

#check data length
length: str = inst.query('DATA:LENG?')
logger.info(length)

#get data port number
data_port_str: str = inst.query('DATA:PORT?')
data_port = int(data_port_str)

ascan_header_size = 28  #ascan header size in bytes
length_bytes = data_length*2 +ascan_header_size #vector length in bytes

#measure single ascans in cycle
stop_event = threading.Event()
data = {}

duration_in_seconds = 5
#measure and read data in auto mode
data = {}
stop_event.clear()

data_thread = threading.Thread(target=read_binary_data, args=(ip, data_port, stop_event, data, length_bytes))
data_thread.start()

inst.write(f'STAR AUTO')
start_time = time.time()
while time.time() - start_time < duration_in_seconds:
    time.sleep(0.1)

stop_event.set()
data_thread.join()   #wait for thread to finish
inst.write(f'STOP')

unpack_and_plot_data(data)

plt.show()  # Show all plots

#close session
inst.close()
rm.close()


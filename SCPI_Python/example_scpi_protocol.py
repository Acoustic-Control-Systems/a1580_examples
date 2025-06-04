import sys
import time
import matplotlib.pyplot as plt
import pyvisa as visa
import logging
import socket
import threading

from common_functions import *
from struct import unpack

def set_parameters(inst, data_length):
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
    inst.write('TRAN:MODE OFF')
    trans_reverse_polarity: str = inst.query('TRAN:MODE?')
    logger.info(f"Transmitter reverse polarity: {trans_reverse_polarity}")

    #enable transmitter damp
    inst.write('TRAN:DAMP:ENAB ON')
    trans_damp_enabled: str = inst.query('TRAN:DAMP:ENAB?')
    logger.info(f"Transmitter damping enabled: {trans_damp_enabled}")

    # set transmitter type to single
    inst.write('TRAN:TYPE SINGle') 
    tran_type:str = inst.query('TRAN:TYPE?')
    logger.info(f"Transmitter type: {tran_type}")

    #set linear gain value
    inst.write('GAIN 10')
    gain_level: str = inst.query('GAIN?')
    logger.info(f"Gain level: {gain_level} dB")

    #set gain mode to linear
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

    constant_delay: str = inst.query('AVERage:PERiod?')
    logger.info(f"Constant delay: {constant_delay} s")

    #random delay
    inst.write('AVERage:PERiod:RANDom 2000 NS')
    random_delay: str = inst.query('AVERage:PERiod:RANDom?')
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

ip: str = '192.168.0.11'
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

#check data length
length: str = inst.query('DATA:LENG?')
logger.info(length)

ascan_header_size = 28  #ascan header size in bytes
length_bytes = data_length*2 +ascan_header_size #vector length in bytes

#read single ascan

data: dict = {}
# Create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip, data_port))
    logger.info("Connected to data port")

    #request single ascan measurement
    inst.write(f'STAR SING')

    # Read data 
    s.settimeout(1.0)  # Set a timeout for the socket to prevent hanging, seconds
    try:      
        data[0] = s.recv(length_bytes) # receive data from the socket
        if not data[0]:
            logger.info("No data received")
        else:
            logger.info(f"Received data of length {len(data[0])}")
    except socket.timeout:
        logger.error("Socket timeout, no data received")
    except Exception as e:
        logger.error(f"Error while receiving data: {e}")    
    
unpack_and_plot_data(data)


#measure single ascans in cycle
stop_event = threading.Event()
data = {}

#create a separate thread to read data via the data port
data_thread = threading.Thread(target=read_binary_data, args=(ip, data_port, stop_event, data, length_bytes))
data_thread.start()

duration_in_seconds = 5

start_time = time.time()

while time.time() - start_time < duration_in_seconds:
    # start measurement (single ascan)
    inst.write(f'STAR SING')
    time.sleep(0.5)

stop_event.set()    #stop data reading thread
data_thread.join()   #wait for thread to finish

unpack_and_plot_data(data)
plt.show()  # Show all plots

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


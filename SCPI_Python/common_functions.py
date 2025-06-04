import socket
import logging

def check_error_queue_and_assert(inst):
    msg_num, msg_str = read_error_queue(inst)
    assert msg_num == 0, f'Found error in queue: {msg_str}'

def check_error_queue_and_assert_if_no_error(inst):
    msg_num, msg_str = read_error_queue(inst)
    assert msg_num != 0, f'No error in queue found: {msg_str}'

def read_error_queue(inst):
    error = inst.query(f'SYSTem:ERRor?')
    msg_num, msg_str = parse_error(error)
    return msg_num, msg_str

def parse_error(error_msg: str):
    msg_spl = error_msg.split(',', 1)
    num = int(msg_spl[0])
    msg = msg_spl[1] if len(msg_spl) == 2 else ''
    return num, msg

def read_binary_data(host, port, stop_event, raw_data, length_bytes):
    logger = logging.getLogger(__name__)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        logger.info(f"[DATA_READ] Connected to data port {port}")

        s.settimeout(1.0)

        counter = 0
        while not stop_event.is_set():
            try:
                data = s.recv(length_bytes) 
                if not data:
                    logger.info("Receiving data stopped")    
                    break
                else:
                    logger.debug(f"[DATA_READ] Received data of length {len(data)}")
            
                raw_data[counter] = data
                counter = counter + 1
            except socket.timeout:
                logger.debug("[DATA_READ] Socket timeout, no data received")
                continue
            except Exception as e:
                logger.error(f"[DATA_READ] Error while receiving data: {e}")
                continue
    logger.info("[DATA_READ] Stopping data thread...")

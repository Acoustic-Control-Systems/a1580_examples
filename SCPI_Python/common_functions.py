import socket
import json
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

def get_hardware_info(inst):
    """Read one IEEE block and decode its complete JSON document."""
    payload = inst.query_binary_values(
        'SYST:HARD:INFO?', datatype='B', container=bytes)
    document = json.loads(payload.decode('utf-8'))
    if document.get('status') != 'success':
        raise RuntimeError(document.get('message', 'Hardware information unavailable'))
    return document['data']['plates']


def read_binary_data(host, port, stop_event, raw_data, length_bytes, ready_event=None):
    """Reassemble complete A-scan frames across arbitrary TCP receive boundaries."""
    logger = logging.getLogger(__name__)
    if length_bytes < 28 or (length_bytes - 28) % 2:
        raise ValueError('Expected a 28-byte header and int16 samples')
    pending = bytearray()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
            stream.settimeout(1.0)
            stream.connect((host, port))
            logger.info('[DATA_READ] Connected to data port %s', port)
            if ready_event is not None:
                ready_event.set()
            while not stop_event.is_set():
                try:
                    chunk = stream.recv(length_bytes)
                except socket.timeout:
                    continue
                if not chunk:
                    break
                pending.extend(chunk)
                while True:
                    offset = pending.find(b'FtH1')
                    if offset < 0:
                        # Preserve a possible magic prefix split across receives.
                        pending[:] = pending[-3:]
                        break
                    if offset:
                        del pending[:offset]
                    if len(pending) < length_bytes:
                        break
                    raw_data[len(raw_data)] = bytes(pending[:length_bytes])
                    del pending[:length_bytes]
    except OSError as error:
        logger.error('[DATA_READ] Connection failed: %s', error)
    if pending:
        logger.debug('[DATA_READ] Discarding %s incomplete trailing bytes', len(pending))
    logger.info('[DATA_READ] Stopping data thread')

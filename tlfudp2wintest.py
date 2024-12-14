
import sys
import argparse
import logging
import socketserver
import time
import socket

from dataclasses import dataclass

@dataclass
class Qso:
    call: str = ''
    freq: float = 0
    mode: str = ''
    rst_s: str = ''
    rst_r: str = ''
    exhange: str = ''
    seq: int = 0
    time: int = int(time.time())    # epoch seconds


#A1 40CW  14-Dec-24 08:10 0004  TE4ST          599  599  123                              |
#A1 40CW  14-Dec-24 08:14 0005  TE5ST          599  599  987                        7030.0|
def parse_tlf_qso(line):
    result = Qso()
    result.mode = line[5:8].strip()
    result.call = line[31:45].strip()
    result.rst_s = line[46:50].strip()
    result.rst_r = line[51:56].strip()
    result.exchange = line[56:66].strip()
    result.freq = float(line[83:]) * 1000
    result.seq = int(line[25:29])

    # fixme: parse time
    #result.time = ...

    return result


def get_wt_band(freq):
    mhz = int(freq / 1_000_000)
    match mhz:
        case 1: return 1
        case 3: return 2
        case 7: return 3
        case 10: return 4
        case 14: return 5
        case 18: return 6
        case 21: return 7
        case 24: return 8
        case 28 | 29: return 9

    return 0


def build_wt_qso(qso):
    f = int(qso.freq / 100)
    mode = 0 if qso.mode == 'CW' else 1
    band = get_wt_band(qso.freq)
    return (
        f'ADDQSO: "STN1" "" "STN1" {qso.time} {f} {mode}'
        f' {band} 0 0 0 {qso.seq} {qso.seq} "{qso.call}"'
        f' "{qso.rst_s}" "{qso.rst_r}{qso.exchange}"'
        f' "" "" "" 0 "" "" "" 5'
        )


def send_wt_qso(qso):
    global args
    line = build_wt_qso(qso)
    # add checksum
    data = line.encode('utf-8')
    checksum = (sum(data) | 0x80) & 0xff
    data += bytes([checksum, 0])
    logging.debug(data)
    # and send it
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(data, (args.wt_host, args.wt_port))


class TlfUdpHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        ip = self.client_address[0]
        raw = self.rfile.readline().strip()
        logging.info(f'*** {len(raw)} bytes from {ip}')
        logging.debug(raw)

        data = raw.decode("utf-8")
        if len(data) == 89 and data[1] == '1':
            qso = parse_tlf_qso(data)
            logging.debug(qso)
            send_wt_qso(qso)


def process_args():
    # default values
    tlf_host = '127.0.0.1'
    tlf_port = 9873
    wt_host = '127.0.0.1'
    wt_port = 9872

    parser = argparse.ArgumentParser(description='TLF UDP to WinTest converter')
    parser.add_argument('-d', '--debug', action='store_true',
                    help='debug log level')
    parser.add_argument('--tlf-host', metavar='HOST', type=str, default=tlf_host,
                    help=f'TLF node host/IP (default: {tlf_host})')
    parser.add_argument('--tlf-port', metavar='PORT', type=int, default=tlf_port,
                    help=f'TLF node port (default: {tlf_port})')
    parser.add_argument('--wt-host', metavar='HOST', type=str, default=wt_host,
                    help=f'WinTest destination host (default: {wt_host})')
    parser.add_argument('--wt-port', metavar='PORT', type=int, default=wt_port,
                    help=f'WinTest destination port (default: {wt_port})')

    parsed_args, unparsed_args = parser.parse_known_args()
    if unparsed_args:
        parser.print_help()
        sys.exit(1)

    return parsed_args

#########################

args = process_args()

log_level = logging.INFO
if args.debug:
    log_level = logging.DEBUG

logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
logging.info(f'Listening on {args.tlf_host}:{args.tlf_port}')
logging.info(f'  Sending to {args.wt_host}:{args.wt_port}')

with socketserver.UDPServer((args.tlf_host, args.tlf_port), TlfUdpHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


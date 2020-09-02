import scapy.all as scapy
from argparse import ArgumentParser as AP
from subprocess import call
from termcolor import colored
from os import getuid


def check_sudo():
    if getuid() != 0:
        print(
            f"{colored('[-]', 'red')} You must be super user to run this script")
        exit(1)


check_sudo()

parser = AP()

parser.add_argument('-i', '--interface', dest='interface', required=True,
                    help='select the interface that will sniff the packet')

args = parser.parse_args()


def get_mac(ip, interface):
    local_ip = scapy.get_if_addr(interface)
    if local_ip == ip:
        return scapy.Ether().src

    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    response = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    for packet in response:
        return packet[1].hwsrc


def process_packet(packet):
    if packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
        real_mac = get_mac(packet[scapy.ARP].psrc, args.interface)
        response_mac = packet[scapy.ARP].hwsrc

        if real_mac != response_mac:
            print(f"{colored('[!]','red')} ARP spoof was detected")
            print(
                f"{colored(packet[scapy.ARP].psrc, 'green')} has a differente mac {colored(response_mac,'red')}")
            if real_mac != None:
                print(f"The mac should be {colored(real_mac,'cyan')}")


def sniff_packet(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packet)


print(
    f"{colored('[!]', 'green')} Starting to sniff packets on {colored(args.interface, 'blue')}")
sniff_packet(args.interface)

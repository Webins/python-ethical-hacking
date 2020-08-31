import scapy.all as scapy
from termcolor import colored
from os import getuid
from argparse import ArgumentParser as AP

def scan(ip):
    # create an arp packet
    arp_request = scapy.ARP(pdst=ip)
    # create an ether packet
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    # create a final packet
    arp_request_broadcast = broadcast/arp_request
    # send packet with a custom ether part and receive the response
    response = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    print("Ip Address\t\tMac Address\n-------------------------------------------")
    for packets in response:
        print(f"{packets[1].psrc}\t\t{packets[1].hwsrc}")
    
    # debugging
    # arp_request_broadcast.show()
    # print(arp_request.summary())
    # scapy.ls(scapy.ARP()) List of all the field of the ARP object


def check_sudo():
    if getuid() != 0:
        print(colored('[-]', color='red'), end=' ')
        print('You must be super user to run this script')
        exit(1)


check_sudo()

parser = AP()
parser.add_argument('-t', '--target', dest='target', help='target ip \ ip range', default=None)

args = parser.parse_args()

if args.target is None:
    print(colored('[-]', color='red'), end=' ')
    print('You must select a target')
    exit(1)

scan(args.target)

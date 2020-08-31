from argparse import ArgumentParser as AP
from re import search, match, findall, compile, MULTILINE
from random import randint
from subprocess import check_output, call, STDOUT, CalledProcessError
from termcolor import colored
from os import getuid


def rand_mac():
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        randint(0, 255),
        randint(0, 255),
        randint(0, 255),
        randint(0, 255),
        randint(0, 255),
        randint(0, 255)
    )


def check_sudo():
    if getuid() != 0:
        print(colored('[-]', color='red'), end=' ')
        print('You must be super user to run this script')
        exit(1)


def change_mac(mac, interface):
    old_mac = search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w',
                     check_output(['ifconfig', interface]).decode())
    if old_mac == mac:
        print(colored('[*]', color='yellow'), end=' ')
        print("Can not change the mac because the provided and the previous mac are equal")
        exit(0)

    print(colored('[*]', color='yellow'), end=' ')
    print(f"Changing mac address for {interface}")
    call(['ifconfig', interface, 'down'])
    call(['ifconfig', interface, 'hw', 'ether', mac])
    call(['ifconfig', interface, 'up'])
    print(colored('[+]', color='green'), end=' ')
    print(
        f"Mac address changed from {colored(old_mac[0], color='red')} to {colored(mac, color='cyan')} in the interface {colored(interface, color='yellow')}")


def validate_mac(mac):
    if match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
        return
    else:
        print(colored('[-]', color='red'), end=' ')
        print("The mac address provided is not correct")
        exit(1)


def check_interface(interface=None):
    if interface is None:
        print(colored('[-]', color='red'), end=' ')
        print('No interface were provided')
        print_interfaces()
        exit(1)
    try:
        result = search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w',
                        check_output(['ifconfig', interface]).decode())
        if result is None:
            print(colored('[-]', color='red'), end=' ')
            print("The interface provided can not be changed")
            print_interfaces()
            exit(1)
    except CalledProcessError:
        print_interfaces()
        exit(1)


def print_interfaces():
    print('These are the interfaces available for you:')
    pattern = compile(r"^.*\:\s", MULTILINE)
    matches = pattern.findall(check_output('ifconfig',
                                           stderr=STDOUT).decode())
    for match in matches:
        print(colored('[*]', color='yellow'), end=' ')
        print(match.split(sep=':')[0])


def reset_original_mac(interface=None):
    if interface is None:
        print('No interface were provided')
        print_interfaces()
        exit(1)

    check_interface(interface)
    origin_mac = check_output(
        ['ethtool', '-P', interface]).decode().split()[-1]
    change_mac(origin_mac, interface)


check_sudo()

parser = AP()

parser.add_argument('-i', '--interface', dest='interface', default=None,
                    help='select an interface to change the mac address')
parser.add_argument('-m', '--mac', dest='mac', default=rand_mac(),
                    help='specify a new mac to change. If not mac address were supply a random mac address will be generated')
parser.add_argument('-r', '--reset', dest='reset', action='store_true',
                    help='Reset the mac addres to the original mac if it was changed')

args = parser.parse_args()

if args.reset:
    reset_original_mac(args.interface)
else:
    check_interface(args.interface)
    validate_mac(args.mac)
    change_mac(args.mac, args.interface)

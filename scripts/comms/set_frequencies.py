#!/bin/python3
# Given a space seperated list of 802.ll frequencies. Will change a ubiquiti
# station to use those frequencies.

# Guy wires: 10 ft height. 10 feet away. 15ft cordage
import subprocess
import argparse
import ipaddress
channels_to_freqs = {
    1 : 2412,
    2 : 2417,
    3 : 2422,
    4 : 2427,
    5 : 2432,
    6 : 2437,
    7 : 2442,
    8 : 2447,
    9 : 2452,
    10 : 2457,
    11: 2462
}

def main(args):

    try:
        a = ipaddress.ip_address(args.IP)
    except ValueError:
        print(f'Invalid IP Address {args.IP}')
        return

    print("Changing frequencies for: " + args.IP)

    if(len(args.channels) > 11 or len(args.channels) < 1):
        print("ERR: Invalid number of channels")
        return 1

    # Combine channel nums  into a string 
    channel_string = ''
    for each in args.channels:
        if (each > 11 or each < 1):
            return 1
        channel_string = str(channels_to_freqs[each]) + "," +  channel_string
        #print(each)
    print("Inserting " + channel_string)

    #sed -i.bak 's/wireless.1.scan_list.channels=.*/wireless.1.scan_list.channels=2437/' system.cfg
    output = subprocess.check_output('sshpass -p wvuurc ssh -o \
HostKeyAlgorithms=+ssh-rsa wvuurc@{IP}\
            \'sed -i \'s/wireless.1.scan_list.channels=.*/wireless.1.scan_list.channels={chans}/\' /tmp/system.cfg\''.format(chans=channel_string,IP=args.IP), shell=True)
    
    output = subprocess.check_output(
        'sshpass -p wvuurc ssh -o HostKeyAlgorithms=+ssh-rsa wvuurc@{IP} \'cfgmtd -w -p /etc/\''.format(IP=args.IP), shell=True)
    
    output = subprocess.check_output(
        'sshpass -p wvuurc ssh -o HostKeyAlgorithms=+ssh-rsa wvuurc@{IP} \'reboot\''.format(IP=args.IP), shell=True)
    
    return

if __name__ == "__main__":
    print('This script is not currently functional, do not use')
    # parser = argparse.ArgumentParser(description='Change the operating\
    #                                  frequencies of a ubiquiti AP')
    # parser.add_argument('IP', help="IP of the AP you want to change\
    #                     frequencies of", type=str)
    # parser.add_argument('channels', help='space seperated list of channels\
    #                     [1-11]', type=int, nargs='+')
    # args = parser.parse_args()

    # main(args)
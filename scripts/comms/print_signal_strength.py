#!/bin/python3
import os
import subprocess
import json
import time


# NateP Spring 2022. This is very jank but it works.


def main():

    output = False
    #text_in = os.system('sshpass -p wvuurc ssh -o HostKeyAlgorithms=+ssh-rsa wvuurc@192.168.1.30 \'wstalist\' ')
    try:
        output = subprocess.check_output(
                'sshpass -p wvuurc ssh -o "StrictHostKeyChecking no" -o HostKeyAlgorithms=+ssh-rsa wvuurc@192.168.1.30 \'wstalist\'', shell=True)
    except Exception as E:
        print("Could not get signal strength")
        print(E)
    # sshpass -p wvuurc ssh -o HostKeyAlgorithms=+ssh-rsa -o "StrictHostKeyChecking no" wvuurc@192.168.1.30

    if not output:
        return

    output = output.decode('ASCII')
    data = json.loads(output)
    try:
        print("Base RX: " + str(data[0]["signal"]) + "dBm")
    except:
        print("Couldn't read base strength")
    try:
        print("Rover RX:" + str(data[0]["remote"]["signal"]) + "dBm")
    except:
        print("couldn't read remote strength")

    return

if __name__=="__main__":
    while(1):
        main()
        time.sleep(1)

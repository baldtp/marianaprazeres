#!/usr/bin/python3

# Projeto de Redes de Computadores 2018/19
#   83429   Andre Gaspar
#   83554   Rafael Pereira
#   8xxxx   Joao Afonso

import os
import argparse
import signal
import socket
import sys


# main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', default=59000)  # BSport
    parser.add_argument('-n', default="localhost")  # CSname
    parser.add_argument('-p', default=58069)  # CSport
    args = parser.parse_args()
    global bsport
    global csname
    global csport
    bsport = args.b
    csname = args.n
    csport = args.p
    register()


# cria processo filho para ligacao UDP e faz registo no CS
def register():
    try:
        pid = os.fork()
        if pid == 0:
            try
                udp_send("REG " + csname + " " + bsport)
                msg = udp_receive()
                if msg == 'RGR NOK\n':
                    print('Error: could not unregister the server, its registry was not found.\n')
                    sys.exit(2)
                if msg == 'RGR ERR\n':
                    print('Error: could not unregister the server.\n')
                    sys.exit(2)
            except socket.timeout:
                print('Error: connection to the CS timed out.\n')
                sys.exit(2)
            print(msg)
            sys.exit(0)
    except OSError:
        exit("Could not create a child process")


def udp_send(msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(str.encode(msg), csname, csport)
    s.close()


def udp_receive():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("localhost", bsport))
    data, addr = s.recvfrom(30)
    s.close()
    msg = data.decode()
    return msg


signal.signal(signal.SIGINT, ctrlc_handler)


def ctrlc_handler():
    try
        udp_send("UNR " + csname + " " + bsport)
        msg = udp_receive()
        if msg == 'UAR NOK\n':
            print('Error: could not unregister the server, its registry was not found.\n')
            sys.exit(2)
        if msg == 'UAR ERR\n':
            print('Error: could not unregister the server.\n')
            sys.exit(2)
    except socket.timeout:
        print('Error: connection to the CS timed out.\n')
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()

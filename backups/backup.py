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
import select
import shutil
import datetime


# terminar pograma
def ctrlc_handler(signum, frame):
    try:
        s_udp.sendto(str.encode("UNR " + ip_addr + " " + str(bsport) + "\n"), (csname, int(csport)))
        s_udp.settimeout(5)
        msg = s_udp.recvfrom(300)[0].decode()
        s_udp.settimeout(None)

        if msg == 'UAR OK\n':
            print(msg)
            exit_normally()

        elif msg == 'UAR NOK\n':
            print(msg)
            exit_abnormally()

        elif msg == 'UAR ERR\n':
            print(msg)
            exit_abnormally()

        else:
            print("Resposta nao esperada.\n")
            s_udp.sendto(str.encode("ERR\n"), (csname, int(csport)))
            exit_abnormally()

    except socket.timeout:
        print('Error: connection to the CS timed out.\n')
        exit_abnormally()


signal.signal(signal.SIGINT, ctrlc_handler)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)


# main
def main():
    get_ip()
    get_args()
    register()

    global s_udp
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp.bind((ip_addr, int(bsport)))

    global s_tcp
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.bind((ip_addr, int(bsport)))
    s_tcp.listen(5)

    while True:
        inputready, outputready, exceptready = select.select([s_udp, s_tcp], [], [])
        for s in inputready:

            if s == s_udp:
                read_udp()

            elif s == s_tcp:
                read_tcp()

            else:
                print("Unknow socket.\n")


# obter ip
def get_ip():
    s_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_ip.connect(("8.8.8.8", 80))
    global ip_addr
    ip_addr = s_ip.getsockname()[0]
    s_ip.close()


# obter args
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', default=59000)  # bsport
    parser.add_argument('-n', default=ip_addr)  # csname
    parser.add_argument('-p', default=58066)  # csport
    args = parser.parse_args()
    global bsport
    global csname
    global csport
    bsport = args.b
    csname = args.n
    csport = args.p


# registar no cs
def register():
    try:
        s_reg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_reg.sendto(str.encode("REG " + ip_addr + " " + str(bsport) + "\n"), (csname, int(csport)))
        s_reg.settimeout(5)
        msg = s_reg.recvfrom(300)[0].decode()
        s_reg.settimeout(None)
        s_reg.close()

        if msg == 'RGR OK\n':
            print(msg)

        elif msg == 'RGR NOK\n':
            print(msg)
            sys.exit(2)

        elif msg == 'RGR ERR\n':
            print(msg)
            sys.exit(2)

        else:
            print("Resposta nao esperada.\n")
            s_udp.sendto(str.encode("ERR\n"), (csname, int(csport)))
            sys.exit(2)

    except socket.timeout:
        print('Error: connection to the CS timed out.\n')
        sys.exit(2)


# esperar pedidos udp
def read_udp():
    try:
        pid = os.fork()
        if pid == 0:
            msg = s_udp.recvfrom(300)[0].decode().split()

            if msg[0] == 'LSF':
                s_udp.sendto(str.encode("LFD " + list_files(msg[1], msg[2]) + "\n"), (csname, int(csport)))

            elif msg[0] == 'LSU':
                s_udp.sendto(str.encode("LUR " + reg_user(msg[1], msg[2]) + "\n"), (csname, int(csport)))

            elif msg[0] == 'DLB':
                s_udp.sendto(str.encode("DBR " + del_dir(msg[1], msg[2]) + "\n"), (csname, int(csport)))

            else:
                s_udp.sendto(str.encode("ERR\n"), (csname, int(csport)))
                exit_abnormally()

            exit_normally()

    except OSError:
        print('Error: a connection could not be made.\n')


# listar ficheiros duma pasta
def list_files(user, folder):
    path = 'user_' + user + "/" + folder
    files = os.listdir(path)
    res = str(len(files))

    for file in files:
        info = os.stat(path + '/' + file)
        date_time = datetime.datetime.fromtimestamp(info.st_mtime).strftime("%d.%m.%Y %H:%M:%S")
        file_info = file + ' ' + date_time + ' ' + str(info.st_size)
        res = res + ' ' + file_info

    return res


# registar user
def reg_user(user, pw):
    filename = 'user_' + user + '.txt'
    try:
        with open(filename, "w+") as file:
            file.write(pw)

            if pw == file.read():
                res = 'OK'

            else:
                res = 'NOK'

    except OSError:
        res = 'ERR'

    return res


# apagar pasta
def del_dir(user, folder):
    path = 'user_' + user + "/" + folder
    shutil.rmtree(path, ignore_errors=True)

    if os.path.isdir(path):
        res = 'NOK'

    else:
        res = 'OK'

    return res


# esperar pedidos tcp
def read_tcp():
    try:
        conn, addr = s_tcp.accept()
        pid = os.fork()
        if pid == 0:
            msg = conn.recv(1024).decode().split(None, 3)

            if msg[0] == 'AUT':
                user = msg[1]
                conn.sendall(str.encode("AUR " + aut(user, msg[2]) + "\n"))
                msg = conn.recv(1024).decode().split(None, 3)

                if msg[0] == 'UPL':
                    conn.sendall(str.encode("UPR " + up_files(user, msg[1], msg[2], conn) + "\n"))

                elif msg[0] == 'RSB':
                    if len(msg) > 2:
                        conn.sendall(str.encode("RBR ERR\n"))
                    else:
                        conn.sendall(str.encode("RBR " + down_files(user, msg[1]) + "\n"))

            else:
                conn.sendall(str.encode('ERR\n'))
                conn.close()
                exit_abnormally()

            conn.close()
            exit_normally()

        else:
            conn.close()

    except OSError:
        print('Error: a connection could not be made.\n')


def aut(user, pw):
    filename = 'user_' + user + '.txt'
    with open(filename, "r") as file:

        if pw == file.read():
            res = 'OK'

        else:
            res = 'NOK'

    return res


def up_files(user, folder, n, conn):
    return ''
    # todo


def down_files(user, folder):
    path = 'user_' + user + "/" + folder

    if os.path.isdir(path):
        files = os.listdir(path)
        res = str(len(files))

        for file in files:
            with open(path + '/' + file, "rb") as down_file:
                file_data = down_file.read()
            info = os.stat(path + '/' + file)
            date_time = datetime.datetime.fromtimestamp(info.st_mtime).strftime("%d.%m.%Y %H:%M:%S")
            file_info = file + ' ' + date_time + ' ' + str(info.st_size) + ' ' + file_data.decode()
            res = res + ' ' + file_info

    else:
        res = 'EOF'

    return res


def exit_abnormally():
    s_udp.close()
    s_tcp.close()
    sys.exit(2)


def exit_normally():
    s_udp.close()
    s_tcp.close()
    sys.exit()


if __name__ == "__main__":
    main()

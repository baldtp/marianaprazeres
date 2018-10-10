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


def get_ip():
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp.connect(("8.8.8.8", 80))
    global ip_addr
    ip_addr = s_udp.getsockname()[0]
    s_udp.close()


def udp_send(msg):
    s_udp.sendto(str.encode(msg), (csname, int(csport)))


def udp_receive():
    data = s_udp.recvfrom(30)
    msg = data[0].decode()
    return msg


def tcp_send(s, msg):
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


# terminar pograma
def ctrlc_handler(signum, frame):
    try:
        udp_send("UNR " + ip_addr + " " + str(bsport) + "\n")
        s_udp.settimeout(5)
        msg = udp_receive()
        s_udp.settimeout(None)
        if msg == 'UAR OK\n':
            print(msg)
            exit_normally()
        if msg == 'UAR NOK\n':
            print('Error: could not unregister the server.\n')
            exit_abnormally()
        elif msg == 'UAR ERR\n':
            print('Error: protocol syntax error.\n')
            exit_abnormally()
        else:
            udp_send("ERR\n")
            exit_abnormally()
    except socket.timeout:
        print('Error: connection to the CS timed out.\n')
        exit_abnormally()


signal.signal(signal.SIGINT, ctrlc_handler)


# main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', default=59000)  # BSport
    parser.add_argument('-n', default=socket.gethostname())  # CSname
    parser.add_argument('-p', default=58066)  # CSport
    args = parser.parse_args()
    global bsport
    global csname
    global csport
    bsport = args.b
    csname = args.n
    csport = args.p

    get_ip()

    global s_udp
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    register()
    s_udp.close()

    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp.bind((ip_addr, int(bsport)))

    global s_tcp
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.bind((ip_addr, int(bsport)))
    s_tcp.listen(1)

    input_aux = [s_udp, s_tcp]
    while True:
        inputready, outputready, exceptready = select.select(input_aux, [], [])
        for s in inputready:
            if s == s_udp:
                read_udp()
            elif s == s_tcp:
                read_tcp()
            else:
                print("unknow socket")


# registo no cs
def register():
    try:
        udp_send("REG " + ip_addr + " " + str(bsport) + "\n")
        s_udp.settimeout(5)
        msg = udp_receive()
        s_udp.settimeout(None)
        if msg == 'RGR OK\n':
            print(msg)
        elif msg == 'RGR NOK\n':
            print('Error: could not register the server.\n')
            exit_abnormally()
        elif msg == 'RGR ERR\n':
            print('Error: protocol syntax error.\n')
            exit_abnormally()
        else:
            udp_send("ERR\n")
            exit_abnormally()
    except socket.timeout:
        print('Error: connection to the CS timed out.\n')
        exit_abnormally()


# servidor fica a espera de pedidos udp
def read_udp():
    try:
        pid = os.fork()
        if pid == 0:
            msg = udp_receive()
            split_msg = msg.split()

            if split_msg[0] == 'LSF':
                udp_send("LFD " + list_files(split_msg[1], split_msg[2]) + "\n")

            elif split_msg[0] == 'LSU':
                udp_send("LUR " + up_user(split_msg[1], split_msg[2]) + "\n")

            elif split_msg[0] == 'DLB':
                udp_send("DBR " + del_dir(split_msg[1], split_msg[2]) + "\n")

            else:
                udp_send("ERR\n")
                exit_abnormally()
            exit_normally()
    except OSError:
        print('Error: a connection could not be made.\n')


def list_files(user, dire):

    counter = 0
    info_total = ''
    if get_directory(dire) != False:
        files = os.listdir(dire)
        for file in files:          
                counter = counter + 1
                size = os.path.getsize(dire + '/' + file)
                stat = os.stat(dire + '/' + file)           
                seconds = os.path.getmtime(dire + '/' + file)
                date_time = str(datetime.datetime.fromtimestamp(seconds).strftime("%d.%m.%Y %H:%M:%S"))
                info = name + ' ' + date_time + ' ' + size
                info_total = info_total + info
    msg_ret = str(counter) + ' ' + info_total
    return msg_ret
    # nao deve estar bem tem de ser testado e merdas

def up_user(user, pw):
    fich = 'user_' + user +'.txt'
    file_us = open( fich, "r+")
    if pw in file_us:
        msg_ret = 'status = OK'
    else: 
        msg_ret = 'status = NOK'
        return msg_ret
    # como é o caso de erro, falta testar


def del_dir(user, dir):
    directory = 'user_' + user_ #remover todos as pastas que tenham o diretorio directory

    msg_ret = ''

    # msg_ret = 'OK'
    # msg_ret = 'NOK'
    return msg_ret
    #NOT FINISED

# servidor fica a espera de pedidos tcp
def read_tcp():
    try:
        conn, addr = s_tcp.accept()
        pid = os.fork()
        if pid == 0:
            msg = conn.recv(30).decode()
            split_msg = msg.split()

            if split_msg[0] == 'AUT':
                tcp_send(conn, str.encode("AUR " + aut(split_msg[1], split_msg[2]) + "\n"))

            elif split_msg[0] == 'UPL':
                tcp_send(conn, str.encode("UPR " + up_files(split_msg[1], split_msg[2]) + "\n"))

            elif split_msg[0] == 'RSB':
                tcp_send(conn, str.encode("RBR " + down_files(split_msg[1]) + "\n"))
            else:
                tcp_send(conn, str.encode('ERR\n'))
            conn.close()
            exit_normally()
        else:
            conn.close()
    except OSError:
        print('Error: a connection could not be made.\n')


def aut(user, pw):
    return ''
    #todo


def up_files(dir, nr):
    return 'OK'
    # todo


def down_files(dir):
    return ''
    #todo


# def get_directory(directory):
#     cwd = os.getcwd()
#     files = os.listdir(cwd)
#
#     if directory in files:
#         dire = cwd + '/' + directory
#         return dire
#     return False


# def backup_request(dire, log):
#     if get_directory(dire) != False:
#         files = os.listdir(dire)
#         msg = ' ' + str(len(files))
#
#         for file in files:
#             size = os.path.getsize(dire + '/' + file)
#             stat = os.stat(dire + '/' + file)
#             seconds = os.path.getmtime(dire + '/' + file)
#             date_time = str(datetime.datetime.fromtimestamp(seconds).strftime("%d.%m.%Y %H:%M:%S"))
#             msg += ' ' + file + ' ' + date_time + ' ' + str(size)
#
#         req = " BCK " + dire + msg
#         reply = 'BKR 192.168.128.2 58001 2 r1.c 19.09.2018 08:45:01 50 r2.c 19.09.2018 09:03:13 70'.split(
#             ' ')  # request_tcp(req,log).split(' ') #descomentar e apagar a mensagem para comunicacao
#         pop = ''
#         if reply[0] == 'BKR':
#             pop = 'backup to: ' + reply[1] + ' ' + reply[2] + ' completed - ' + dire + ':'
#             for x in range(int(reply[3])):
#                 pop += (' ' + reply[4 * (x + 1)])
#
#             print(pop)
#     else:
#         print("Directory doesn't exist: Please try again")


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

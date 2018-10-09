#!/usr/bin/env python3

import socket
import time
import os
import argparse
# import sys

#iniciar programa - flags
parser = argparse.ArgumentParser()
parser.add_argument('-p', default = 58068) #CSport
args = parser.parse_args()
PORT = args.p
HOST = "localhost"

def get_user_backup(name):
    backup = ''

    file = open("userlist.txt", "r")
    for line in file.readlines():
        if name in line:
            line = line.split(',')
            backup = line[2]
    file.close()

    return backup

def get_backup_address(backup):
    h=0
    p=0
    file = open("backuplist.txt", "r")
    for line in file.readlines():
        if backup == line[0]:
            h = line[2]
            p = line[3]
    file.close()
    return h,p

def udp_receive():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    msg = s.recv(30).decode().split(" ")
    s.close()
    return msg

def udp_send(name, port, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(str.encode(msg), name, port)
    s.close()


def login(log):
    user = log[1]
    pw = log[2]
    if os.path.isfile("userlist.txt") is False:
        file = open("userlist.txt", "w+")
        file.close()
    file = open("userlist.txt", "r+")
    if os.stat("userlist.txt").st_size != 0:
        for line in file.readlines():
            line = line.split(',')
            if line[0] == user:
                if line[1] == pw:
                    file.close()
                    return "AUR OK"
                else:
                    file.close()
                    return "AUR NOK"

        if os.path.isfile("backuplist.txt") is False:
        	print('No available backup')
        	return "AUR NOK"
        	f = open('backuplist.txt', 'r')
        	f = f.readlines()
        	for bs in f:
        		bs = bs.split(',')
        		msg = 'LSU ' + user + ' ' + pw
        		udp_send(bs[2], bs[3], msg)
        		if udp_receive() == 'LUR OK':
        			file.write(user + "," + pw + "," + bs[0])
        			file.close()
        			return "AUR NEW"
        print('Error from backup')
        return "AUR NOK"
    else:
    	if os.path.isfile("backuplist.txt") is False:
    		print('No available backup')
    		return "AUR NOK"
    	else:
	    	f = open('backuplist.txt', 'r')
	    	f = f.readlines()
	    	for bs in f:
		    	bs = bs.split(',')
		    	msg = 'LSU ' + user + ' ' + pw
		    	udp_send(bs[2], bs[3], msg)
		    	if udp_receive() == 'LUR OK':
		    		file.write(user + "," + pw + "," + bs[0])
		    		file.close()
		    		return "AUR NEW"
	    		else:
	    			continue

	    	print('Error from backup')
	    	return "AUR NOK"

def bs_register():
    try:
        pid = os.fork()
        if pid == 0:
            backup_counter = 0
            while 1:
                msg = udp_receive()
                if msg[0] == 'REG':
                    try:
                        backup_counter += 1
                        if os.path.isfile("backuplist.txt") == False:
                            file = open("backuplist.txt", "w+")
                            file.close()
                        file = open("backuplist.txt", "r+")
                        file.write(str(backup_counter) + ',0,' + msg[1] + ',' + msg[2])
                        file.close()
                        udp_send(msg[1], int(msg[2]), 'RGR OK')
                    except ValueError:
                        udp_send(msg[1], int(msg[2]), 'RGR ERR')
                elif msg[0] == 'UNR':
                    try:
                        backup_counter -= 1
                        if os.path.isfile("backuplist.txt") == False:
                            file = open("backuplist.txt", "w+")
                            file.close()
                        f = open("backuplist.txt", "r+")
                        new_f = f.readlines()
                        f.seek(0)
                        for line in new_f:
                            if msg[2] not in line:
                                f.write(line)
                        f.truncate()
                        udp_send(msg[1], int(msg[2]), 'UAR OK')
                    except ValueError:
                        udp_send(msg[1], int(msg[2]), 'UAR ERR')
    except OSError:
        exit("Could not create a child process")

def handle_requests(msg):
    global USER

    if len(msg) == 3:
        USER = msg[1]

    if msg[0] == "AUT" and len(msg) == 3:
        return login(msg)
    elif msg[0] == 'DLU':
        msg = ''
        file = open("userlist.txt", "r+")
        new_f = file.readlines()
        file.seek(0)
        for line in new_f:
            if USER in line: # falta login
                print(line)
                l = line.split(',')
                if len(l) != 3:
                    print('escreveu')
                    file.write(line)
                    msg = 'DLR NOK'
                else:
                    msg = 'DLR OK'
            else:
                print('escreveu')
                file.write(line)
        file.truncate()
        file.close()
        print(msg)
        return msg
   
    elif msg[0] == 'BCK':
        msg_ret = ''
        print(msg)
        fich = msg[2:]
        fich1 = ' '.join(fich)
        print(fich1)
        dire = msg[1]
        file_us = open("userlist.txt", "r+")
        f_us = file_us.readlines()
        file_us.seek(0)
        file_bs = open("backuplist.txt", "r+")
        f_bs = file_bs.readlines()
        file_bs.seek(0)
        for line1 in f_us:
            line1 = line1.split(',')
            if dire in line1[3]:
                bs = line1[2]
                for line2 in f_bs:
                    line2 = line2.strip('\n')
                    line2 = line2.split(',')
                    if bs == line2[0]:
                        ip = line2[2]
                        porto = line2[3]
                        msg_ret = 'BKR ' + ip + ' ' + porto + ' ' + fich1
                        #se o user nao esta registado no bs o cs troca LSU-LUR com bs e retorna lista de todos os ficheiros
                        # se estiver registado o cs troca LSF-LFD com bs e para receber a lista de ficheiros modificados
                        print(msg_ret)
        if msg_ret == '':
            	msg_ret = 'BKR EOF'
        file_bs.close()
        file_us.close()
        # como ver se esta bem formulado
        return msg_ret



    elif msg[0] == 'RST':
        msg_ret = ''
        dire = msg[1]
        file_us = open("userlist.txt", "r+")
        f_us = file_us.readlines()
        file_us.seek(0)
        file_bs = open("backuplist.txt", "r+")
        f_bs = file_bs.readlines()
        file_bs.seek(0)
        for line1 in f_us:
            line1 = line1.split(',')
            if dire in line1[3]:
                bs = line1[2]
                for line2 in f_bs:
                    line2 = line2.strip('\n')
                    line2 = line2.split(',')
                    if bs == line2[0]:
                        ip = line2[2]
                        porto = line2[3]
                        msg_ret = 'RSR ' + ip + ' ' + port
                        print(msg_ret)
        if msg_ret == '' :
        	msg_ret = 'RSR EOF'
        file_bs.close()
        file_us.close()
        # como ver se esta bem formulado
        return msg_ret

    # diretorias guardadas pelo user
    elif msg[0] == 'LSD' :
    	counter = 0
    	msg_ret = ''

    	f = open('userlist.txt', 'r')
    	f = f.readlines
    	backup = ''
    	for line in f:
    		l = line.split('')
    		if l[0] == USER:
    			counter = counter +1
    			backup = backup + ' ' + l[2]
    	f.close()
    	msg_ret = 'LDR ' + counter + backup
    	return msg_ret

    elif msg[0] == 'LSF':

    	#abrir ficheiro e procurar backup do user
    	f = open('userlist.txt', 'r')
    	f = f.readlines
    	backup = ''
    	for line in f:
    		l = line.split('')
    		if l[0] == USER:
    			backup = l[2]
    	f.close()

    	#abrir ficheiro e procurar ip e port do bs
    	f = open('backuplist.txt', 'r')
    	f = f.readlines()
    	h = ''
    	p = ''
    	for line in f:
    		l = line.split('')
    		if l[0] == backup:
    			h = l[2]
    			p = l[3]

    	#enviar mensagem ao bs
    	msg = 'LSF ' + USER + ' ' + msg[1]
    	udp_send(h, p, msg)
    	reply = udp_receive()

    	#devolver ao user
    	if reply.split(' ')[0] == 'LFD':
    		return 'LFD ' + h + ' ' + p + ' ' + reply[4:]


    elif msg[0] == 'DEL':
    	#abrir ficheiro e procurar backup do user
    	f = open('userlist.txt', 'r')
    	f = f.readlines
    	backup = ''
    	for line in f:
    		l = line.split('')
    		if l[0] == USER:
    			backup = l[2]
    	f.close()

    	#abrir ficheiro e procurar ip e port do bs
    	f = open('backuplist.txt', 'r')
    	f = f.readlines()
    	h = ''
    	p = ''
    	for line in f:
    		l = line.split('')
    		if l[0] == backup:
    			h = l[2]
    			p = l[3]
    	dire = msg[1]
    	msg_bs = 'DLB '+ USER + ' ' + dire
    	udp_send( h, p,msg_bs)
    	reply = udp_receive()

    # 	#se for bem apagado
    # 	return 'DDR OK'
    # 	#se nao for bem apagado
    # 	return 'DDR NOK'
    return "hello"



def tcp_requests():
    try:
        pid = os.fork()
        if pid == 0:
            while 1:
                print("TCP server on")
                so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                so.bind((HOST, PORT))
                so.listen(1)
                conn, addr = so.accept()
                print('Connected by', addr)
                prev = ""
                msg = ''
                while True:
                    data = conn.recv(1024)
                    msg += data.decode()
                    if len(msg.split()) > 3:
                        if msg == prev:
                            conn.sendall(str.encode('debug'))
                        else:
                            print("")
                            print(msg)
                            print("")
                            prev = msg
                            conn.sendall(str.encode(handle_requests(msg.split()[0:3])))
                            conn.sendall(str.encode(handle_requests(msg.split()[3:])))

                    else:
                        if msg == prev:
                            conn.sendall(str.encode('debug')) #partir mensagem ao meio e responder duas vezes
                        else:
                            prev = msg
                            conn.sendall(str.encode(handle_requests(msg.split()))) #partir mensagem ao meio e responder duas vezes

                    if not data:
                        print("TCP server off")
                        so.shutdown(1)
                        so.close()
                        break
    except OSError:
        exit("Could not create a child process")

bs_register()
tcp_requests()

while 1:
    time.sleep(5)
    print("running")

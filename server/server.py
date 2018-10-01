#!/usr/bin/env python3

import socket
import time
import os
import argparse
import sys

#iniciar programa - flags
parser = argparse.ArgumentParser()
parser.add_argument('-p', default = 58066) #CSport
args = parser.parse_args()
PORT = args.p
HOST = "localhost"

# Recebe um tuplo de dois elementos com um username e uma password e se o login existir, devolve o username e o numero do seu backup
def avai_bs():
    return "1"

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
    if os.path.isfile("userlist.txt") == False:
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
            
        file.write('\n' + user + "," + pw + "," + avai_bs())
        file.close()
        return "AUR NEW"
    else:
        print('ola')
        file.write(user + "," + pw + "," + avai_bs())
        file.close()
        return "AUR NEW"
def bs_register():
    try:
        pid = os.fork()
    except OSError:
        exit("Could not create a child process")
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

def handle_requests(msg):
	msg = msg.split(" ")
	if msg[0] == "AUT":
		return login(msg)
	elif msg[0] == 'DLU':
		msg = ''
		file = open("userlist.txt", "r+")
		new_f = file.readlines()
		for line in new_f:
			if name in line: # falta login
				line = line.split(',')
				if len(line) != 3:
					file.write(line)
					msg = 'DLR NOK'
				msg = 'DLR OK'
			else:
				file.write(line)				
		file.close()
		print(msg)
		return msg


def tcp_requests():
	try:
		pid = os.fork()
	except OSError:
		exit("Could not create a child process")
	if pid == 0:
		while 1:
			print("aqui")
			msg = ''
			so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			so.bind((HOST, PORT))
			so.listen()
			conn, addr = so.accept()
			print('Connected by', addr)
			while True:
				data = conn.recv(1024)
				msg += data.decode()
				conn.sendall(str.encode(handle_requests(msg)))
				if not data:
					break				
			so.close()




#bs_register()
tcp_requests()

while 1:
	time.sleep(5)
	print("running")

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
	file = open("backuplist.txt", "r")
	for line in file.readlines():
		if backup == line[0]:
			h = line[2]
			p = line[3]
	file.close()

	return (h,p)

def bs_requests(name, req, item):
	

	


	# elif req == 'LSD':
	# 	msg = 'LSF ' + name + ' ' + item
	# 	udp_send(h, p, msg)
	# elif req == '
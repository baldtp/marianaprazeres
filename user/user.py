#!/usr/bin/env python3

import socket
import argparse
import sys
import os
import datetime

#iniciar programa - flags
parser = argparse.ArgumentParser()
parser.add_argument('-n', default = "localhost") #CSname
parser.add_argument('-p', default = 58068) #CSport
args = parser.parse_args()
HOST = args.n
PORT = args.p

def send(s, msg):
	totalsent = 0
	while totalsent < len(msg):
		sent = s.send(msg[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent

def request_tcp(req, login):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	log = ''
	if login != 0:
		send(s, str.encode(login))
		log = s.recv(1024).decode()

	send(s, str.encode(req))
	inc = s.recv(1024).decode()
	while inc == log:
		inc = s.recv(1024).decode()
	s.close()
	return inc

def authenticate(log):
	data = request_tcp(log, 0)
	if data == "AUR OK":
		print("\n\nAuthentication successful: You are now logged in!\n")
		return True
	elif data == "AUR NOK":
		print("\n\nWrong password: Please try again")
		return False
	elif data == "AUR NEW":
		print('\n\nUser "' + log.split(' ')[1] + '" created: You are now logged in!\n')
		return True
		
	print('Unexpected return: ' + data)
	quit()
	return 0	    

def login():

	global USER	
	global PASS

	log = input('Please enter your login: (example "login 88888 banana12")\n\nCommand: ')
	l = log.split(" ")

	if l[0] == 'exit':
		print('Bye Bye <3')
		quit()

	
	USER = l[1]
	PASS = l[2]	

	if len(l) == 3 and l[0] == 'login' and l[1].isdigit() and len(l[1]) == 5 and l[2].isalnum() and len(l[2]) == 8:
		if authenticate("AUT " + l[1] + " " + l[2]) == False:
			login()
	else:
		print('\n')
		print('Error: wrong arguments.\nUsername: IST ID (5 numbers)\tPassword: 8 characters restricted to numbers and letters\nType "exit" to exit')
		print('\n')
		login()
	return True

def get_directory(directory):

	cwd = os.getcwd()
	files = os.listdir(cwd)	
	
	if directory in files:
		dire = cwd + '/' + directory
		return dire
	return False

def backup_request(dire, log):

	if get_directory(dire) != False:
		files = os.listdir(dire)
		msg = ' ' + str(len(files))

		for file in files:			
			size = os.path.getsize(dire + '/' + file)
			stat = os.stat(dire + '/' + file)			
			seconds = os.path.getmtime(dire + '/' + file)
			date_time = str(datetime.datetime.fromtimestamp(seconds).strftime("%d.%m.%Y %H:%M:%S"))
			msg += ' ' + file + ' ' + date_time + ' ' + str(size)


		req = " BCK " + dire + msg
		reply = 'BKR 192.168.128.2 58001 2 r1.c 19.09.2018 08:45:01 50 r2.c 19.09.2018 09:03:13 70'.split(' ')#request_tcp(req,log).split(' ') #descomentar e apagar a mensagem para comunicacao
		pop = ''
		if reply[0] == 'BKR':
			pop = 'backup to: ' + reply[1] + ' ' + reply[2] + ' completed - ' + dire + ':'
			for x in range(int(reply[3])):
				pop += (' ' + reply[4 * (x+1)])
	
			print(pop)
	else:
		print("Directory doesn't exist: Please try again")

def list_request(log):
	req = " LST"
	reply = 'LDR 1 RC'.split(" ") #request_tcp(req,log).split(' ')  #descomentar e apagar a mensagem para comunicacao
	if reply[0] == 'LDR' and int(reply[1]) > 0:
		msg = ''
		for x in range(int(reply[1])):
			msg += reply[x + 2]

		print(msg)
	elif reply[1] == '0':
		print('\nThe backup is empty')
	else:
		print('Error')

def menu():
	global first
	global USER	
	global PASS

	if first:
		cmd = input("Please choose one option and type the command:\n\t1 - Request backup of a chosen directory (backup [dir])\n\t\
2 - List the previously stored directories (dirlist)\n\t3 - List files of a directory (filelist [dir])\n\t4 - Retrieve a\
previously backed up directory (restore [dir])\n\t6 - Delete the backup of a directory (delete [dir])\n\t6 - Delete user (deluser)\n\t7 - Logout (logout)\n\nCommand: ")
		print('')
		first = False
	else:
		cmd = input("\nCommand: ")
		print('')
	
	cmd = cmd.split(' ')
	log = "AUT " + USER + " " + PASS
	if cmd[0] == 'deluser':		
		print(request_tcp(" DLU", log))
	elif cmd[0] == 'backup':
		backup_request(cmd[1], log)
	elif cmd[0] == 'restore':
		req = " RST " + cmd[1]
		if get_directory(cmd[1]) != False:
			request_tcp(req,log)
		else:
			print("Directory doesn't exist: Please try again")

	elif cmd[0] == 'dirlist':		
		list_request(log)

	elif cmd[0] == 'filelist':
		req = ' LSF ' + cmd[1]
		if get_directory(cmd[1]) != False:
			request_tcp(req,log)
		else:
			print("Directory doesn't exist: Please try again")
	elif cmd[0] == 'delete':
		req = ' DEL ' + cmd[1]
		if get_directory(cmd[1]) != False:
			request_tcp(req,log)
		else:
			print("Directory doesn't exist: Please try again")
	elif cmd[0] == 'logout':
		USER = ''
		PASS = ''
		first = True
		print('\nLogout successful! (Apu voice) Come again <3\n')
		return False
	elif cmd[0] == 'exit':
		print("Bye bye <3")
		quit()
	return True

def main(argv):
	global first
	first = True

	while 1:
		print("\t WELCOME TO RC'S CLOUD BACKUP SYSTEM\n\n")

		if login():
			while menu():
				continue

if __name__ == "__main__":
    main(sys.argv[1:])
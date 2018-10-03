#!/usr/bin/env python3

import socket
import argparse
import sys
import os
import time

#iniciar programa - flags
parser = argparse.ArgumentParser()
parser.add_argument('-n', default = "localhost") #CSname
parser.add_argument('-p', default = 58068) #CSport
args = parser.parse_args()
HOST = args.n
PORT = args.p

USER = ''
PASS = ''

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
		print("request")
		send(s, str.encode(login))
		log = s.recv(1024).decode()
		print(log)

	print("1 message sent")
	send(s, str.encode(req))
	inc = s.recv(1024).decode()
	while inc == log:
		inc = s.recv(1024).decode()
	s.close()
	return inc

def authenticate(log):
	data = request_tcp(log, 0)
	print(data)
	if data == "AUR OK":
		print("\n\nAuthentication successful: You are now logged in!\n")
		return True
	elif data == "AUR NOK":
		print("\n\nWrong password: Please try again")
		return False
	elif data == "AUR NEW":
		print("\n\nYour account was created successfully: You are now logged in!\n")
		return True
		
	print('Unexpected return: ' + data)
	quit()
	return 0	    

def login():

	log = input('Please enter your login: (example "login 88888 banana12")\n\nCommand: ')
	l = log.split(" ")

	global USER 
	USER = l[1]
	global PASS
	PASS = l[2]

	if l[0] == 'exit':
		print('Bye Bye <3')
		quit()

	if len(l) == 3 and l[0] == 'login' and l[1].isdigit() and len(l[1]) == 5 and l[2].isalnum() and len(l[2]) == 8:
		if authenticate("AUT " + l[1] + " " + l[2]) == False:
			login()
	else:
		print('\n')
		print('Error: wrong arguments.\nUsername: IST ID (5 numbers)\tPassword: 8 characters restricted to numbers and letters\nType "exit" to exit')
		print('\n')
		login()
	return True

def backup_request(directory):	
	#Check if directory exists	
	cwd = os.getcwd()
	files = os.listdir(cwd)
	if directory in files:
		dire = cwd + '/' + directory
		files = os.listdir(dire)
		msg = str(len(files))
		print(dire)
		for file in files:			
			size = os.path.getsize(dire + '/' + file)
			stat = os.stat(dire)
			date = stat.st_mtime
			print(date)
			#msg += ' ' + file + ' ' + date + ' ' + size
	else:
		return "nodir"



def menu():
	cmd = input("Please choose one option and type the command:\n\t1 - Request backup of a chosen directory (backup [dir])\n\t\
2 - List the previously stored directories (dirlist)\n\t3 - List files of a directory (filelist [dir])\n\t4 - Retrieve a\
previously backed up directory (restore [dir])\n\t6 - Delete the backup of a directory (delete [dir])\n\t6 - Delete user (deluser)\n\t7 - Logout (logout)\n\nCommand: ")
	
	cmd = cmd.split(' ')
	msg = "AUT " + USER + " " + PASS
	if cmd[0] == 'deluser':		
		print(request_tcp(" DLU", msg))
	elif cmd[0] == 'backup':
		backup_request(cmd[1])





def main(argv):

	print("\t WELCOME TO RC'S CLOUD BACKUP SYSTEM\n\n")

	if login():
		print(USER)
		print(PASS)
		menu()

if __name__ == "__main__":
    main(sys.argv[1:])
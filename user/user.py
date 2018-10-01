#!/usr/bin/env python3

import socket
import argparse

#iniciar programa - flags
parser = argparse.ArgumentParser()
parser.add_argument('-n', default = "localhost") #CSname
parser.add_argument('-p', default = 58066) #CSport
args = parser.parse_args()
HOST = args.n
PORT = args.p



def request_tcp(out):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	print(str.encode(out))
	s.send(str.encode(out))
	inc = s.recv(1024).decode()
	return inc



def authenticate(log):
	data = request_tcp(log)
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

	log = input('Please enter your login: (example "login 84730 banana12")\n\nCommand: ')
	l = log.split(" ")

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

def menu():
	cmd = input("Please choose one option and type the command:\n\t1 - Request backup of a chosen directory (backup [dir])\n\t\
2 - List the previously stored directories (dirlist)\n\t3 - List files of a directory (filelist [dir])\n\t4 - Retrieve a\
previously backed up directory (restore [dir])\n\t6 - Delete the backup of a directory (delete [dir])\n\t6 - Delete user (deluser)\n\t7 - Logout (logout)\n\nCommand: ")
	if cmd == 'deluser':
		request_tcp("DLU")





print("\t WELCOME TO RC'S CLOUD BACKUP SYSTEM\n\n")

if login():
	menu()

# if log == True:
# 	print("\n")




# print('Received', repr(data))
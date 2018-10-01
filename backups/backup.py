#!/usr/bin/env python3

import os
import sys
import socket
import argparse

#iniciar programa - flags
parser = argparse.ArgumentParser()
parser.add_argument('-b', default = "59001") #BSport
parser.add_argument('-n', default = "localhost") #CSname
parser.add_argument('-p', default = 58069) #CSport
args = parser.parse_args()
cs_snd = (args.n, args.p)
cs_rcv = (args.n, args.b)


#cria processo a parte para ligacao UDP e faz registo no CS
def register():
	try:
		pid = os.fork()
	except OSError:
		exit("Could not create a child process")
	if pid == 0:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.sendto(str("REG " + str(args.n) + " " + str(args.b)).encode(), cs_snd)
		s.close()
		
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('localhost', 59001))
		msg = s.recv(30).decode()
		print(msg)
		s.close()
		sys.exit(0)

register()
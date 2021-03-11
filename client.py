import socket
import sys
import time
import datetime
import random
import os

import logging
import argparse

ENCODE = 'utf-8'

IP_SERVER = ''
PORT_SERVER = 12345

DEFAULT_LOG_LEVEL = logging.INFO
TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'

def main():

	parser = argparse.ArgumentParser(description='sistema de vendas')

	parser.add_argument("--purchase", "-p", help='amount of purchases', type=int)
	parser.add_argument("--ip", "-i", help="ip server", type=str)
	parser.add_argument("--servers", "-ns", help="number servers", type=str)
	parser.add_argument("--timetoken", "-tt", help="time token", type=str)


	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)
	
	args = parser.parse_args()

	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)
	else:
		logging.basicConfig(format='%(asctime)s.%(msecs)03d %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()

	global IP_SERVER 

	IP_SERVER = args.ip

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	s.connect((IP_SERVER, PORT_SERVER))

	dirs = 'times_servers_'+args.servers
	
	if not os.path.exists(dirs):
		os.makedirs(dirs)

	sFile = 'client'+IP_SERVER[7:]+'_'+args.timetoken+'.txt'
	file = open(dirs+'/'+sFile, 'w')

	times = []
	for i in range(args.purchase):

		time_begin = datetime.datetime.now()

		s.send(bytes('purchase', ENCODE))

		msg = s.recv(1024).decode(ENCODE)

		_, _, qnt = msg.split(' ')

		logging.info(msg)

		s.send(bytes(str(random.randint(1,9)), ENCODE))

		response = s.recv(1024).decode(ENCODE)

		logging.info(response)

		time_end = datetime.datetime.now()
		time_diff = (time_end - time_begin)
		time_diff_seconds = time_diff.seconds + (time_diff.microseconds/1000000.0)
		times.append(time_diff_seconds)
		time.sleep(0.01)

	s.send(bytes('disconnect', ENCODE))

	for t in times:
		file.write(str(args.servers)+' '+str(args.timetoken)+' '+str(t)+'\n')

	file.close()	
	s.close()

if __name__ == '__main__':
	main()
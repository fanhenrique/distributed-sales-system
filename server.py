import time
import socket
import threading
import sys

import logging
import argparse

ENCODE = 'utf-8'

IP = ''
IP_SERVER = ''

PORT_SERVER = 5555
PORT_CLIENTS = 12345

TOKEN = False
TIME_TOKEN = 0.5
STOCK = 0

DEFAULT_LOG_LEVEL = logging.INFO
TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'

lock = threading.Lock()

def purchase(conn, addr):

	global STOCK

	conn.send(bytes('quantidade disponivel: '+str(STOCK), ENCODE))

	quantity = int(conn.recv(1024).decode(ENCODE))

	while True:
		if TOKEN:
			if quantity <= STOCK:
				with lock:
					STOCK -= quantity
				conn.send(bytes('compra efetuada: ' + str(quantity), ENCODE))
				logging.info('{} comprou {}'.format(addr, quantity))
				break
			else:
				conn.send(bytes('quantidade indisponivel', ENCODE))
				logging.info('{} tentou comprar {}'.format(addr, quantity))
				break
		time.sleep(1)

def requestClient(conn, addr):

	while True:
		msg = conn.recv(1024).decode(ENCODE)

		if msg == 'disconnect':
			logging.info('disconnected {}'.format(addr))
			break

		if msg == 'purchase':
			purchase(conn, addr)


	conn.close()
	return False

def requestServer(srs):

	global TOKEN

	conn, addr = srs.accept()

	while True:
		
		msg = conn.recv(1024).decode(ENCODE)
		
		if msg == 'token':
			with lock:
				TOKEN = True

		logging.info('{} {} {}'.format(msg, addr, TOKEN))
	
	conn.close()			
	return False

def transmitToken(stt):
	
	global TOKEN
	global TIME_TOKEN

	while True:

		if TOKEN:

			time.sleep(TIME_TOKEN)
			with lock:
				TOKEN = False
			stt.send(bytes('token', ENCODE))

	return False

def main():

	parser = argparse.ArgumentParser(description='sistema de vendas')

	parser.add_argument("--token", "-t", help="token int", type=str)
	parser.add_argument("--timetoken", "-tt", help="time token", type=float)
	parser.add_argument("--ip", "-i", help="ip server", type=str)
	parser.add_argument("--ring", "-r", help="ring server", type=str)
	parser.add_argument('--stock', '-s', help='quantity in stock', type=int)

	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)

	args = parser.parse_args()

	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)
	else:
		logging.basicConfig(format='%(asctime)s.%(msecs)03d %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()

	global TOKEN
	global IP
	global IP_SERVER
	global STOCK
	global TIME_TOKEN

	TOKEN = True if int(args.token) == 1 else False
	IP = args.ip
	IP_SERVER = args.ring
	STOCK = args.stock
	TIME_TOKEN = args.timetoken

	logging.info('server:{}'.format(IP))
	logging.info('token: {}'.format(TOKEN))
	logging.info('connect: {}'.format(IP_SERVER))
	logging.info('---------------------')

	# sockt escuta servidor
	srs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	srs.bind((IP, PORT_SERVER))
	srs.listen(1)

	# thread que escuta servidor
	threading.Thread(target=requestServer, args=(srs, )).start()
	time.sleep(2) # espera a thread que escuta o servidor ser criada
	
	# socket transmite para o servidor
	stt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	stt.connect((IP_SERVER, PORT_SERVER))

	#thread transmite i token para o próximo servidor
	threading.Thread(target= transmitToken, args=(stt, )).start()

	# sockt escuta clientes
	src = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	src.bind((IP, PORT_CLIENTS))
	src.listen(1)

	while True:
		conn, addr = src.accept()
		threading.Thread(target=requestClient, args=(conn, addr, )).start()

	src.close()
	stt.close()
	srs.close()


if __name__ == '__main__':
	main()
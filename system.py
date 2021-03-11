from multiprocessing import Process
import shlex
import subprocess

import logging
import argparse
import time
import numpy

DEFAULT_LOG_LEVEL = logging.INFO
TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'

DEFAULT_BW_MBPS = 1
DEFAULT_DELAY_MS = 0
DEFAULT_SERVERS = [3]
DEFAULT_PURCHASE = 30
DEFAULT_STOCK = 100
DEFAULT_TIME_TOKEN = 0.5
DEFAULT_TIME_TOKEN_FINAL = 1.0

def main():

	parser = argparse.ArgumentParser(description='sistema de vendas')

	parser.add_argument("--mbps", "-b", help="Bandwidth (mbps)", default=DEFAULT_BW_MBPS, type=int)
	parser.add_argument("--delays", "-d", help="deleys", default=DEFAULT_DELAY_MS, type=int)
	parser.add_argument("--servers", "-ls", nargs='+', help='list of servers', default=DEFAULT_SERVERS, type=int)
	parser.add_argument("--timetoken", "-tt", help="time token", default=DEFAULT_TIME_TOKEN, type=float)
	parser.add_argument("--timetokenfinal", "-ttf", help="time token final", default=DEFAULT_TIME_TOKEN_FINAL, type=float)
	parser.add_argument("--purchase", "-p", help='amount of purchases', default=DEFAULT_PURCHASE, type=int)
	parser.add_argument('--stock', '-s', help='quantity in stock', default=DEFAULT_STOCK, type=int)
	

	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)
	
	args = parser.parse_args()

	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)
	else:
		logging.basicConfig(format='%(asctime)s %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()

	for s in args.servers:
		for tt in numpy.arange(args.timetoken, args.timetokenfinal, args.timetoken):
			cmd = 'sudo python3 topology.py --mbps %d --delays %d -ns %d -tt %f -p %d -s %d' % (args.mbps, args.delays, s, tt, args.purchase, args.stock)
			param = shlex.split(cmd)
			logging.info("Param: {}".format(" ".join(param)))
			subprocess.call(param)



if __name__ == '__main__':
	main()
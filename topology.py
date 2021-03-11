from mininet.topo import Topo
from mininet.node import Host
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

import logging
import argparse
import time

DEFAULT_LOG_LEVEL = logging.INFO
TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'


class TopoBasica(Topo):

	def __init__(self, bw_mbps, delay_ms, servers):
		Topo.__init__(self)

		hs = []
		for i in range(1, servers+1):
			hs.append(self.addHost('s'+str(i), cls=Host, ip='10.0.0.'+str(i), defaultRoute=None))
		
		hc = []
		for i in range(1, servers+1):	
			hc.append(self.addHost('c'+str(i), cls=Host, ip='10.0.0.'+str(i+servers), defaultRoute=None))
			
		link_parametros = {'delay': '%dms' % delay_ms, 'bw': bw_mbps, 'loss': 0}

		s0 = self.addSwitch('s0')

		for i in range(servers):
			self.addLink(hs[i], s0, cls=TCLink, **link_parametros)

		for i in range(servers):
			self.addLink(hc[i], s0, cls=TCLink, **link_parametros)
		

def main():

	parser = argparse.ArgumentParser(description='sistema de vendas')

	parser.add_argument("--mbps", "-b", help="Bandwidth (mbps)", type=int)
	parser.add_argument("--delays", "-d", help="delays", type=int)
	parser.add_argument("--servers", "-ns", help='number of servers', type=int)
	parser.add_argument("--timetoken", "-tt", help="time token", type=float)
	parser.add_argument("--purchase", "-p", help='amount of purchases', type=int)
	parser.add_argument('--stock', '-s', help='quantity in stock', type=int)


	help_msg = "Logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--log", "-l", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)
	

	args = parser.parse_args()

	if args.log == logging.DEBUG:
		logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt=TIME_FORMAT, level=args.log)
	else:
		logging.basicConfig(format='%(asctime)s %(message)s', datefmt=TIME_FORMAT, level=args.log)

	args = parser.parse_args()


	topo = TopoBasica(bw_mbps=args.mbps, delay_ms=args.delays, servers=args.servers)

	net = Mininet(topo=topo, host=Host, link=TCLink)

	net.start()

	hs = []
	for i in range(1, args.servers+1):
		hs.append(net.getNodeByName('s'+str(i)))
		
	hc = []
	for i in range(1, args.servers+1):
		hc.append(net.getNodeByName('c'+str(i)))

	for i in range(1, args.servers+1):
		
		if(i == args.servers):
			cmd = 'sudo python3 server.py --token 1 --timetoken '+str(args.timetoken)+' --ip 10.0.0.'+str(i)+' --ring 10.0.0.1 --stock '+str(args.stock)+' &> out_server'+str(i)+'.txt &'
			logging.info('comando s'+str(i)+': %s' % cmd)
			hs[i-1].cmd(cmd)
		else:
			cmd = 'sudo python3 server.py --token 0 --timetoken '+str(args.timetoken)+' --ip 10.0.0.'+str(i)+' --ring 10.0.0.'+str(i+1)+' --stock '+str(args.stock)+' &> out_server'+str(i)+'.txt &' 
			logging.info('comando s'+str(i)+': %s' % cmd)
			hs[i-1].cmd(cmd)

	time.sleep(5)

	for i in range(1, args.servers+1):
		cmdc = 'sudo python3 client.py --ip 10.0.0.'+str(i)+' --purchase '+str(args.purchase)+' --servers '+str(args.servers)+' --timetoken '+str(args.timetoken)+' &> out_client'+str(i)+'.txt'
		logging.info('comando c'+str(i)+': %s' % cmdc)
		hc[i-1].cmd(cmdc)

	net.stop()

if __name__ == '__main__':
	main()
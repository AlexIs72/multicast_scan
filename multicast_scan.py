#!/usr/bin/python
"""
Based on:
	Multicast group scanner.
	Author: Lasse Karstensen <lasse.karstensen@gmail.com>, November 2014
	https://gist.github.com/lkarsten/8194f308b0cf1a3fc0ee
"""



import gevent
from gevent import monkey
monkey.patch_all()

from gevent.queue import JoinableQueue
from time import sleep
from random import random
from netaddr import IPNetwork, IPAddress
from struct import pack
from hexdump import dump

import socket
import logging

INTERFACE_IP = "XXX.XXX.XXX.XXX"
PER_GROUP_LISTEN_TIME = 5  # seconds
CONCURRENT_GROUPS = 10


subnets = [
    [ IPNetwork("225.54.223.0/24"), 5000 ]
];


def join(group, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(5)
    sock.bind((group, port))
    sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
                    socket.inet_aton(INTERFACE_IP))
    mreq = pack('4sl', socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock


def scan_network(q, r, port):
	sleep(random()*5)  # Spread them out.

	while True:
		try:
			group = q.get(timeout=10)
#			print "======> " + str(group)
		except gevent.queue.Empty:
			break
		logging.info("Joining %s" % group)
		sock = join(str(group), port)
		try:
			data = sock.recv(16)
			logging.info("[%s]. Data: %s", group, dump(data, 2))
			r.put(group);
		except socket.timeout:
			logging.info("[%s] Timeout", group)
		sleep(PER_GROUP_LISTEN_TIME)
		sock.close()
		q.task_done()


def prepare_list(q, net):
	for addr in list(net):
		if(addr.words[3] == 0 or addr.words[3] == 255):
			continue
		q.put(addr)            

def process_24_network(net, port):
	q = JoinableQueue()
	r = JoinableQueue()
	gevent.spawn(prepare_list, q, net)

	tasks = []
	for x in range(0, CONCURRENT_GROUPS):
    	#print "spawning %i" % x
		tasks += [gevent.spawn(scan_network, q, r, port)]

	q.join()
	gevent.joinall(tasks)

	if not r.empty():
		with open(str(net.ip) + '_' + str(port) + ".m3u", "w+") as f:
			f.write("#EXTM3U\n")
			while not r.empty():
				try:
					group = r.get(timeout=10)
					f.write('#EXTINF:-1 tvg-logo="" tvg-name="" group-title="",ChannelName' + "\n")
					f.write('udp://@' + str(group) + ':' + str(port) + "\n")
					logging.info("Ok ====> %s" % group)
				except gevent.queue.Empty:
					break;


def process_16_network(net, port):
    for subnet in list(net.subnet(24)):
        process_24_network(subnet, port)


def process_8_network(net, port):
    for subnet in list(net.subnet(16)):
        process_16_network(subnet, port)



def main(): 
    logging.basicConfig(level=logging.DEBUG)

    for subnet in subnets:
        print subnet[0]
        if(subnet[0].netmask == IPAddress("255.0.0.0")):
            process_8_network(subnet[0],subnet[1])
        elif(subnet[0].netmask == IPAddress("255.255.0.0")):
            process_16_network(subnet[0],subnet[1])
        elif(subnet[0].netmask == IPAddress("255.255.255.0")):
            process_24_network(subnet[0],subnet[1])


if __name__ == "__main__":
    main()



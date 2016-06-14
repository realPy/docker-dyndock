#!/usr/bin/env python

import docker
import json
import urllib2
import hashlib
import subprocess
import base64
import os
DOCKER_SOCK = 'unix:///docker.sock'



def get(d, *keys):
    empty = {}
    return reduce(lambda d, k: d.get(k, empty), keys, d) or None

class DockerMonitor(object):
	def __init__(self, client):
		self.client=client
		b64str=base64.encodestring('%s:%s' % (os.environ['API_USER'], os.environ['API_PWD'])).replace('\n', '')
		self.basicAuth='Basic %s' % b64str

	def run(self):
		events = self.client.events()
		for container in self.client.containers():
			rec = self.client.inspect_container(get(container,"Id"))
			if rec["State"]["Status"] == "running" :
				self.add_host(get(container,"Id"))
		for raw in events:
			evt = json.loads(raw)
 			if evt.get('Type', 'container') == 'container':
 				cid = evt.get('id')
 				if cid is None:
					continue
 				status = evt.get('status')
 				if status in set(('start', 'die', 'rename')):
					if status == 'start':
						self.add_host(cid)
					if status == 'die':
						self.delete_host(cid)
		
					#print "new event "+str(self.inspect(cid))
#
	def add_host(self,cid):
		info= self.inspect(cid)
		m = hashlib.md5()
		m.update(cid)
		hash = m.hexdigest()
		url="http://localhost/?hostname=%s.docker&myip=%s&uuid=%s.docker" % (info[0][1:],info[1],hash)
		req = urllib2.Request(url)
		req.add_header('Authorization', self.basicAuth)
		urllib2.urlopen(req).read()

	def delete_host(self,cid):
		
		m = hashlib.md5()
		m.update(cid)
		hash = m.hexdigest()
		domainname=subprocess.check_output("dig +time=0 +tries=0 +short %s.docker TXT | cut -d \"\\\"\" -f2" % (hash),shell=True)
		
		url="http://localhost/delete?hostname=%s" % (domainname)
		req = urllib2.Request(url)
		req.add_header('Authorization', self.basicAuth)
		urllib2.urlopen(req).read()
		url="http://localhost/delete?hostname=%s" % (hash+".docker")
		req = urllib2.Request(url)
		req.add_header('Authorization', self.basicAuth)
		urllib2.urlopen(req).read()





	def inspect(self, cid):
		rec = self.client.inspect_container(cid)
		network=get(rec, 'NetworkSettings','Networks').itervalues().next()
		name = get(rec, 'Name')
		if not name:
			return None
		id = get(rec, 'Id')
		ip = get(network, 'IPAddress')
		return [name,ip]



monitor = DockerMonitor(docker.Client(DOCKER_SOCK, version='auto'))

monitor.run()			

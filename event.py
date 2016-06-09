#!/usr/bin/env python

import docker
import json
import urllib2
import hashlib
import subprocess
DOCKER_SOCK = 'unix:///docker.sock'



def get(d, *keys):
    empty = {}
    return reduce(lambda d, k: d.get(k, empty), keys, d) or None

class DockerMonitor(object):
	def __init__(self, client):
		self.client=client

	def run(self):
		events = self.client.events()
		for container in self.client.containers():
			if container["State"] == "running" :
				self.add_host(get(container,"Id"))
			print "%s %s" % (container["Names"],container["State"])
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

	def add_host(self,cid):
		info= self.inspect(cid)
		m = hashlib.md5()
		m.update(cid)
		hash = m.hexdigest()
		url="http://localhost/?hostname=%s.docker&myip=%s&uuid=%s.docker" % (info[0][1:],info[1],hash)
		password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_mgr.add_password(None, 'http://localhost/', 'root', 'root')
		auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		myopener = urllib2.build_opener(auth_handler)
		opened = urllib2.install_opener(myopener)
		urllib2.urlopen(url).read()

	def delete_host(self,cid):
		
		m = hashlib.md5()
		m.update(cid)
		hash = m.hexdigest()
		domainname=subprocess.check_output("dig +time=0 +tries=0 +short %s.docker TXT | cut -d \"\\\"\" -f2" % (hash),shell=True)
		password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_mgr.add_password(None, 'http://localhost/', 'root', 'root')
		auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		myopener = urllib2.build_opener(auth_handler)
		opened = urllib2.install_opener(myopener)
		
		url="http://localhost/delete?hostname=%s" % (domainname)
		urllib2.urlopen(url).read()
		url="http://localhost/delete?hostname=%s" % (hash+".docker")
		urllib2.urlopen(url).read()





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

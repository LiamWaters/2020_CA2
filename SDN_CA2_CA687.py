#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from mininet.util import dumpNodeConnections
from subprocess import call


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( net, **params ):
        super( LinuxRouter, net).config( **params )
        # Enable forwarding on the router
        net.cmd( 'sysctl net.ipv4.ip_forward=1' )
        net.cmdPrint('iptables --table nat --append POSTROUTING --out-interface r0-eth3 -j MASQUERADE')

    def terminate( net ):
        net.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, net ).terminate()
    

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding routers\n' )

    router = net.addHost( 'r0', cls=LinuxRouter, ip='192.168.1.1/24')

    info( '*** Adding controllers\n' )

    CFWD0=net.addController(name='CFWD0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=9091)

    CPT0=net.addController(name='CPT0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    CLB0=net.addController(name='CLB0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=9090)

    info( '*** Add switches\n')

    s0 = net.addSwitch('s0')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    e0 = net.addSwitch('e0')

    core0 = net.addSwitch('core0', cls=OVSKernelSwitch)

    lb0 = net.addSwitch('lb0', cls=OVSKernelSwitch)
    lb1 = net.addSwitch('lb1', cls=OVSKernelSwitch)
    lb2 = net.addSwitch('lb2', cls=OVSKernelSwitch)


    info( '*** Add hosts\n')

    extu1 = net.addHost('extu1', ip='192.168.1.100/24', defaultRoute='via 192.168.1.1' )

    intu1 = net.addHost('intu1', ip='10.0.0.10', defaultRoute='via 10.0.0.1' )

    web0 = net.addHost('web0', ip='10.0.1.11', defaultRoute='via 10.0.0.1')

    web1 = net.addHost('web1', cls=Host, ip='10.0.1.2', defaultRoute='via 10.0.0.1')
    web2 = net.addHost('web2', cls=Host, ip='10.0.1.3', defaultRoute='via 10.0.0.1')
    web3 = net.addHost('web3', cls=Host, ip='10.0.1.4', defaultRoute='via 10.0.0.1')
    web4 = net.addHost('web4', cls=Host, ip='10.0.1.5', defaultRoute='via 10.0.0.1')

    info( '*** Add links\n')

    net.addLink( e0, router, intfName2='r0-eth1', params2={ 'ip' : '192.168.1.1/24' } )  
    net.addLink( s0, router, intfName2='r0-eth2', params2={ 'ip' : '10.0.0.1/8' } )

    net.addLink(extu1, e0, cls = TCLink, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True )

    net.addLink(s0, s1, cls = TCLink, bw=10, delay='100ms', loss=25, max_queue_size=1000, use_htb=True )
    net.addLink(s0, s2, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(s1, s3, cls = TCLink, bw=10, delay='100ms', loss=25, max_queue_size=1000, use_htb=True )
    net.addLink(s2, s3, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )

    net.addLink(s3, intu1, cls = TCLink, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True )

    net.addLink(s3, core0)

    net.addLink(core0, web0, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(core0, lb0, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )

    net.addLink(lb0, lb1, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(lb0, lb2, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(lb1, web1, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(lb1, web2, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(lb2, web3, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
    net.addLink(lb2, web4, cls = TCLink, bw=1000, delay='1ms', loss=0, max_queue_size=1000, use_htb=True )
 

    info( '*** Starting network\n')

    net.build()

    info( '*** Starting controllers\n')

    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')

    net.get('e0').start([CFWD0])

    net.get('s0').start([CPT0])
    net.get('s1').start([CPT0])
    net.get('s2').start([CPT0])
    net.get('s3').start([CPT0])

    net.get('core0').start([CFWD0])

    net.get('lb0').start([CLB0])
    net.get('lb1').start([CFWD0])
    net.get('lb2').start([CFWD0]) 

    info( '*** Post configure hosts\n')

    print "starting web services on web0", web0.cmd('python -m SimpleHTTPServer 80 >& /tmp/http.log &')
    print "starting web services on web1", web1.cmd('python -m SimpleHTTPServer 80 >& /tmp/http.log &')
    print "starting web services on web2", web2.cmd('python -m SimpleHTTPServer 80 >& /tmp/http.log &')
    print "starting web services on web3", web3.cmd('python -m SimpleHTTPServer 80 >& /tmp/http.log &')
    print "starting web services on web4", web4.cmd('python -m SimpleHTTPServer 80 >& /tmp/http.log &')

    print "Dumping host connections"

    dumpNodeConnections( net.hosts )

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()


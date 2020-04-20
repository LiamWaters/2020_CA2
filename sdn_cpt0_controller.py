# Liam Waters 2020 Customised Controller (CPT0) was based on a design from Chih-Heng Ke http://csie.nqu.edu.tw/smallko/sdn/mySDN.pdf

from pox.core import core

import pox.openflow.libopenflow_01 as of

from pox.lib.util import dpidToStr





log = core.getLogger()

s0_dpid=0

s1_dpid=0

s2_dpid=0

s3_dpid=0





def _handle_ConnectionUp (event):



	global s0_dpid, s1_dpid, s2_dpid, s3_dpid



	print "ConnectionUp: ", dpidToStr(event.connection.dpid)



	#remember the connection dpid for switch



	for m in event.connection.features.ports:

		if m.name == "s0-eth1":

			s0_dpid = event.connection.dpid

			print "s0_dpid=", s0_dpid

		elif m.name == "s1-eth1":

			s1_dpid = event.connection.dpid

			print "s1_dpid=", s1_dpid

		elif m.name == "s2-eth1":

			s2_dpid = event.connection.dpid

			print "s2_dpid=", s2_dpid

		elif m.name == "s3-eth1":

			s3_dpid = event.connection.dpid

			print "s3_dpid=", s3_dpid



def _handle_PacketIn (event):

	global s0_dpid, s1_dpid, s2_dpid, s3_dpid

	

	print "PacketIn: ", dpidToStr(event.connection.dpid)

	

	if event.connection.dpid==s0_dpid:



		msg = of.ofp_flow_mod()

		msg.priority =1

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0806

		msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))

		event.connection.send(msg)



# All external traffic out port 1 on s0 switch



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.0.1"

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "192.168.1.100"

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "192.168.1.1"

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



# All 10.0.0.x traffic out port 1 on s0 switch to s1



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.0.10"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



# All 10.0.1.x traffic out port 2 on s0 switch to s2



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.1.1"

		msg.actions.append(of.ofp_action_output(port = 3))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.1.11"

		msg.actions.append(of.ofp_action_output(port = 3))

		event.connection.send(msg)



	elif event.connection.dpid==s1_dpid:



# Forward all traffic from port 1 to port 2 on s1



		msg = of.ofp_flow_mod()

		msg.priority =1

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.in_port =1

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



# Forward all traffic from port 2 to port 1 on s1



		msg = of.ofp_flow_mod()

		msg.priority =1

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.in_port =2

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



	elif event.connection.dpid==s2_dpid:



# Forward all traffic from port 1 to port 2 on s2



		msg = of.ofp_flow_mod()

		msg.priority =1

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.in_port =1

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



# Forward all traffic from port 2 to port 1 on s2



		msg = of.ofp_flow_mod()

		msg.priority =1

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.in_port =2

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



	elif event.connection.dpid==s3_dpid:



		msg = of.ofp_flow_mod()

		msg.priority =1

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0806

		msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))

		event.connection.send(msg)



# All internal 10.0.0.x traffic out port 3 on s3 switch



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.0.10"

		msg.actions.append(of.ofp_action_output(port = 3))

		event.connection.send(msg)





# All 10.0.1.x (web traffic) traffic back internally on port 4 by s3 switch



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.1.1"

		msg.actions.append(of.ofp_action_output(port = 4))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_dst = "10.0.1.11"

		msg.actions.append(of.ofp_action_output(port = 4))

		event.connection.send(msg)



# All external traffic from 10.0.1.x out port 2 on s3 switch back to s2



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.1.1"

		msg.match.nw_dst = "10.0.0.1"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.1.1"

		msg.match.nw_dst = "192.168.1.100"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.1.1"

		msg.match.nw_dst = "192.168.1.1"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.1.11"

		msg.match.nw_dst = "10.0.0.1"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.1.11"

		msg.match.nw_dst = "192.168.1.100"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.1.11"

		msg.match.nw_dst = "192.168.1.1"

		msg.actions.append(of.ofp_action_output(port = 2))

		event.connection.send(msg)





# All external traffic from 10.0.0.x out port 1 on s3 switch back to s1



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.0.10"

		msg.match.nw_dst = "10.0.0.1"

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.0.10"

		msg.match.nw_dst = "192.168.1.100"

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



		msg = of.ofp_flow_mod()

		msg.priority =10

		msg.idle_timeout = 0

		msg.hard_timeout = 0

		msg.match.dl_type = 0x0800

		msg.match.nw_src="10.0.0.10"

		msg.match.nw_dst = "192.168.1.1"

		msg.actions.append(of.ofp_action_output(port = 1))

		event.connection.send(msg)



def launch ():

	core.openflow.addListenerByName("ConnectionUp",_handle_ConnectionUp)

	core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
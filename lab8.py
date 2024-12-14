import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.internet_apps

# Create 4 nodes
nodes = ns.network.NodeContainer()
nodes.Create(4)

# Set up the Internet stack on nodes
stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

# Configure point-to-point links with bandwidth and delay
p2p_1 = ns.point_to_point.PointToPointHelper()
p2p_1.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
p2p_1.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))

p2p_2 = ns.point_to_point.PointToPointHelper()
p2p_2.SetDeviceAttribute("DataRate", ns.core.StringValue("1.7Mbps"))
p2p_2.SetChannelAttribute("Delay", ns.core.StringValue("20ms"))

# Create net devices and channels for links
devices_n0_n2 = p2p_1.Install(nodes.Get(0), nodes.Get(2))
devices_n1_n2 = p2p_1.Install(nodes.Get(1), nodes.Get(2))
devices_n2_n3 = p2p_2.Install(nodes.Get(2), nodes.Get(3))

# Set DropTail queue max size for each link
queue_size = ns.network.QueueSize("10p")
devices_n0_n2.Get(1).SetQueueSize(queue_size)
devices_n1_n2.Get(1).SetQueueSize(queue_size)
devices_n2_n3.Get(1).SetQueueSize(queue_size)

# Assign IP addresses
address = ns.internet.Ipv4AddressHelper()
address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n0_n2 = address.Assign(devices_n0_n2)

address.SetBase(ns.network.Ipv4Address("10.1.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n1_n2 = address.Assign(devices_n1_n2)

address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n2_n3 = address.Assign(devices_n2_n3)

# Set up TCP sink (receiver) at n3 and TCP source (sender) at n1
tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory",
                                            ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 8080))
sink_app = tcp_sink.Install(nodes.Get(3))
sink_app.Start(ns.core.Seconds(0.0))
sink_app.Stop(ns.core.Seconds(5.0))

tcp_source = ns.applications.OnOffHelper("ns3::TcpSocketFactory",
                                         ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 8080))
tcp_source.SetAttribute("DataRate", ns.core.StringValue("1Mbps"))
tcp_source.SetAttribute("PacketSize", ns.core.UintegerValue(1024))
source_app = tcp_source.Install(nodes.Get(1))
source_app.Start(ns.core.Seconds(0.5))
source_app.Stop(ns.core.Seconds(4.0))

# Attach FTP application to TCP source
ftp = ns.applications.FtpHelper("ns3::TcpSocketFactory")
ftp.SetAttribute("Remote", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 8080))
ftp_app = ftp.Install(nodes.Get(1))
ftp_app.Start(ns.core.Seconds(0.5))
ftp_app.Stop(ns.core.Seconds(4.0))

# Set up UDP source at n0 to n3 with CBR
udp_source = ns.applications.OnOffHelper("ns3::UdpSocketFactory",
                                         ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 8090))
udp_source.SetAttribute("DataRate", ns.core.StringValue("100kbps"))
udp_source.SetAttribute("PacketSize", ns.core.UintegerValue(1024))
udp_app = udp_source.Install(nodes.Get(0))
udp_app.Start(ns.core.Seconds(0.1))
udp_app.Stop(ns.core.Seconds(4.5))

udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory",
                                            ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 8090))
sink_udp = udp_sink.Install(nodes.Get(3))
sink_udp.Start(ns.core.Seconds(0.0))
sink_udp.Stop(ns.core.Seconds(5.0))

# Enable tracing with color differentiation (using Pcap)
p2p_1.EnablePcap("tcp_flow", devices_n1_n2.Get(1), True)
p2p_1.EnablePcap("udp_flow", devices_n0_n2.Get(1), True)

# Run the simulation
ns.core.Simulator.Stop(ns.core.Seconds(5.0))
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()
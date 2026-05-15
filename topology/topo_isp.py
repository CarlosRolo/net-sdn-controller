from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class ISPTopo(Topo):
    def build(self):
        info('*** Creando topologia ISP con 20 nodos\n')

        s1 = self.addSwitch('s1', dpid='0000000000000001')
        s2 = self.addSwitch('s2', dpid='0000000000000002')
        s3 = self.addSwitch('s3', dpid='0000000000000003')
        s4 = self.addSwitch('s4', dpid='0000000000000004')

        # Todos los hosts en la misma subred 10.0.0.x
        for i in range(1, 6):
            h = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24', mac=f'00:00:00:00:01:{i:02x}')
            self.addLink(h, s1)

        for i in range(6, 11):
            h = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24', mac=f'00:00:00:00:02:{i:02x}')
            self.addLink(h, s2)

        for i in range(11, 16):
            h = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24', mac=f'00:00:00:00:03:{i:02x}')
            self.addLink(h, s3)

        for i in range(16, 21):
            h = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24', mac=f'00:00:00:00:04:{i:02x}')
            self.addLink(h, s4)

        # Links entre switches
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)
        self.addLink(s4, s1)
        self.addLink(s1, s3)

def run():
    setLogLevel('info')
    topo = ISPTopo()
    net = Mininet(
        topo=topo,
        controller=RemoteController('c0', ip='127.0.0.1', port=6633),
        switch=OVSSwitch,
        autoSetMacs=False
    )
    net.start()
    info('*** Topologia ISP levantada\n')
    info('*** 4 switches, 20 hosts, subred 10.0.0.0/24\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()

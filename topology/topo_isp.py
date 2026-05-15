from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class ISPTopo(Topo):
    def build(self):
        info('*** Creando topologia ISP con 20 nodos\n')

        # 4 switches core
        s1 = self.addSwitch('s1', dpid='0000000000000001')
        s2 = self.addSwitch('s2', dpid='0000000000000002')
        s3 = self.addSwitch('s3', dpid='0000000000000003')
        s4 = self.addSwitch('s4', dpid='0000000000000004')

        # Zona 1 — 5 hosts (clientes residenciales)
        for i in range(1, 6):
            h = self.addHost(f'h{i}', ip=f'10.0.1.{i}/24')
            self.addLink(h, s1)

        # Zona 2 — 5 hosts (clientes empresariales)
        for i in range(6, 11):
            h = self.addHost(f'h{i}', ip=f'10.0.2.{i-5}/24')
            self.addLink(h, s2)

        # Zona 3 — 5 hosts (servidores)
        for i in range(11, 16):
            h = self.addHost(f'h{i}', ip=f'10.0.3.{i-10}/24')
            self.addLink(h, s3)

        # Zona 4 — 5 hosts (red de gestión)
        for i in range(16, 21):
            h = self.addHost(f'h{i}', ip=f'10.0.4.{i-15}/24')
            self.addLink(h, s4)

        # Links entre switches (core mesh)
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
        autoSetMacs=True
    )
    net.start()
    info('*** Topologia ISP levantada\n')
    info('*** 4 switches, 20 hosts, conectados a ODL en 127.0.0.1:6633\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()

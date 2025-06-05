from mininet.net import Mininet
from mininet.node import Controller
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel

class TwoHostOneSwitchTopo(Topo):
    def build(self):
        # Create a switch
        switch = self.addSwitch('s1')

        # Create two hosts
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')

        # Connect the hosts to the switch
        self.addLink(host1, switch)
        self.addLink(host2, switch)

def run():
    topo = TwoHostOneSwitchTopo()
    net = Mininet(topo=topo, controller=Controller)

    net.start()
    print("Running CLI, type 'exit' or Ctrl+D to quit.")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()

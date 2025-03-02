from scapy.all import sniff, IP, TCP, UDP, ICMP
from collections import defaultdict
import time
import pandas as pd
import sys

# Global variables for flow tracking
flows = defaultdict(lambda: {
    'start_time': None,
    'end_time': None,
    'src_bytes': 0,
    'dst_bytes': 0,
    'packets': 0,
    'flags': set(),
    'services': set(),
    'wrong_fragment': 0,
    'serror': 0,  # SYN errors
    'rerror': 0,  # REJ errors
})

# Feature extraction function
def extract_features(packet):
    if IP in packet:  # Filter IPv4 packets
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        src_port = packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else 0
        dst_port = packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else 0

        # Flow key
        flow_key = (src_ip, dst_ip, src_port, dst_port, proto)

        # Update flow information
        if flows[flow_key]['start_time'] is None:
            flows[flow_key]['start_time'] = time.time()
        flows[flow_key]['end_time'] = time.time()
        flows[flow_key]['src_bytes'] += len(packet[IP].payload)
        flows[flow_key]['packets'] += 1

        # Track TCP flags
        if TCP in packet:
            flags = str(packet[TCP].flags)
            flows[flow_key]['flags'].add(flags)
            if flags == 'S':  # SYN flag
                flows[flow_key]['serror'] += 1
            if flags == 'R':  # RST flag
                flows[flow_key]['rerror'] += 1

        # Track services (destination ports)
        flows[flow_key]['services'].add(dst_port)

        # Track wrong fragments
        if packet[IP].frag != 0:
            flows[flow_key]['wrong_fragment'] += 1

# Packet capture callback
def packet_callback(packet):
    if IP in packet:  # Only process IPv4 packets
        print(f"Packet captured: {packet.summary()}")  # Debugging: Print packet summary
        extract_features(packet)

# Start sniffing
def start_feature_extraction(iface):
    print(f"Starting packet capture on {iface}...")
    try:
        sniff(iface=iface, prn=packet_callback, timeout=30)  # Capture for 30 seconds
    except Exception as e:
        print(f"Error during packet capture: {e}")
    print("Packet capture stopped.")

    # Convert flows to features
    features_list = []
    for flow_key, flow_data in flows.items():
        src_ip, dst_ip, src_port, dst_port, proto = flow_key

        # Calculate derived features
        total_flows = len(flows)
        same_srv_flows = sum(1 for key in flows if key[3] == dst_port)  # Flows to the same service
        diff_srv_flows = total_flows - same_srv_flows  # Flows to different services
        same_src_port_flows = sum(1 for key in flows if key[2] == src_port)  # Flows from the same source port

        # Calculate rates
        same_srv_rate = same_srv_flows / total_flows if total_flows > 0 else 0
        diff_srv_rate = diff_srv_flows / total_flows if total_flows > 0 else 0
        dst_host_same_srv_rate = same_srv_flows / total_flows if total_flows > 0 else 0
        dst_host_same_src_port_rate = same_src_port_flows / total_flows if total_flows > 0 else 0
        dst_host_srv_serror_rate = flow_data['serror'] / flow_data['packets'] if flow_data['packets'] > 0 else 0

        # Protocol type (ICMP)
        protocol_type_icmp = 1 if proto == 1 else 0  # ICMP protocol number is 1

        # Flags (S0, SF)
        flag_S0 = 1 if 'S' in flow_data['flags'] and 'A' not in flow_data['flags'] else 0
        flag_SF = 1 if 'S' in flow_data['flags'] and 'A' in flow_data['flags'] else 0

        # Create feature dictionary
        features = {
            'src_bytes': flow_data['src_bytes'],
            'dst_bytes': flow_data['dst_bytes'],
            'wrong_fragment': flow_data['wrong_fragment'],
            'count': total_flows,
            'srv_count': same_srv_flows,
            'same_srv_rate': same_srv_rate,
            'diff_srv_rate': diff_srv_rate,
            'dst_host_same_srv_rate': dst_host_same_srv_rate,
            'dst_host_same_src_port_rate': dst_host_same_src_port_rate,
            'dst_host_srv_serror_rate': dst_host_srv_serror_rate,
            'Protocol_type_icmp': protocol_type_icmp,
            'flag_S0': flag_S0,
            'flag_SF': flag_SF,
        }
        features_list.append(features)

    # Save features to CSV
    if features_list:
        df = pd.DataFrame(features_list)
        df.to_csv('extracted_features.csv', index=False)
        print("Features saved to extracted_features.csv")
    else:
        print("No features extracted. Check if packets were captured.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 extract_features.py <interface>")
        sys.exit(1)
    iface = sys.argv[1]
    start_feature_extraction(iface)
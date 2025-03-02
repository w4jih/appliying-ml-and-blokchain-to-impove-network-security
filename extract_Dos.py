"""from scapy.all import sniff, IP, TCP, UDP
from collections import defaultdict
import time
import pandas as pd
import sys

# Global variables for flow tracking
flows = defaultdict(lambda: {
    'src_bytes': 0,
    'dst_bytes': 0,
    'packets': 0,
    'rerror': 0,  # REJ errors (RST flag)
    'services': set(),  # Track destination ports (services)
    'dst_host_count': 0,  # Number of flows to the same destination host
    'dst_host_srv_count': 0,  # Number of flows to the same service on the destination host
    'dst_host_rerror': 0,  # REJ errors for the destination host
})

# Feature extraction function
def extract_features(packet):
    if IP in packet:  # Filter IPv4 packets
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        src_port = packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else 0
        dst_port = packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else 0

        # Flow key (bidirectional)
        forward_flow_key = (src_ip, dst_ip, src_port, dst_port, proto)
        reverse_flow_key = (dst_ip, src_ip, dst_port, src_port, proto)

        # Update forward flow information
        flows[forward_flow_key]['src_bytes'] += len(packet[IP].payload)
        flows[forward_flow_key]['packets'] += 1

        # Update reverse flow information (for dst_bytes)
        flows[reverse_flow_key]['dst_bytes'] += len(packet[IP].payload)

        # Track TCP flags (RST for REJ errors)
        if TCP in packet and 'R' in str(packet[TCP].flags):
            flows[forward_flow_key]['rerror'] += 1

        # Track services (destination ports)
        flows[forward_flow_key]['services'].add(dst_port)

        # Track destination host and service counts
        for flow_key in flows:
            if flow_key[1] == dst_ip:  # Same destination host
                flows[flow_key]['dst_host_count'] += 1
                if flow_key[3] == dst_port:  # Same service on the destination host
                    flows[flow_key]['dst_host_srv_count'] += 1
                if 'R' in str(packet[TCP].flags) if TCP in packet else False:  # REJ errors for the destination host
                    flows[flow_key]['dst_host_rerror'] += 1

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
        rerror_rate = flow_data['rerror'] / flow_data['packets'] if flow_data['packets'] > 0 else 0
        dst_host_same_srv_rate = flow_data['dst_host_srv_count'] / flow_data['dst_host_count'] if flow_data['dst_host_count'] > 0 else 0
        dst_host_diff_srv_rate = 1 - dst_host_same_srv_rate
        dst_host_same_src_port_rate = same_src_port_flows / flow_data['dst_host_count'] if flow_data['dst_host_count'] > 0 else 0
        dst_host_srv_diff_host_rate = diff_srv_flows / total_flows if total_flows > 0 else 0
        dst_host_rerror_rate = flow_data['dst_host_rerror'] / flow_data['dst_host_count'] if flow_data['dst_host_count'] > 0 else 0

        # Service types (eco_i, private)
        service_eco_i = 1 if dst_port == 7 else 0  # Echo service
        service_private = 1 if dst_port in range(49152, 65536) else 0  # Private/dynamic ports

        # Create feature dictionary
        features = {
            'src_bytes': flow_data['src_bytes'],
            'dst_bytes': flow_data['dst_bytes'],
            'count': total_flows,
            'rerror_rate': rerror_rate,
            'dst_host_count': flow_data['dst_host_count'],
            'dst_host_srv_count': flow_data['dst_host_srv_count'],
            'dst_host_same_srv_rate': dst_host_same_srv_rate,
            'dst_host_diff_srv_rate': dst_host_diff_srv_rate,
            'dst_host_same_src_port_rate': dst_host_same_src_port_rate,
            'dst_host_srv_diff_host_rate': dst_host_srv_diff_host_rate,
            'dst_host_rerror_rate': dst_host_rerror_rate,
            'service_eco_i': service_eco_i,
            'service_private': service_private,
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
        print("Usage: python3 extract_features.py <interface>")"""
        
from scapy.all import sniff, IP, TCP, UDP
from collections import defaultdict
import time
import pandas as pd
import sys

# Global variables for flow tracking
flows = defaultdict(lambda: {
    'src_bytes': 0,
    'dst_bytes': 0,
    'packets': 0,
    'rerror': 0,  # REJ errors (RST flag)
    'services': set(),  # Track destination ports (services)
    'dst_host_count': 0,  # Number of flows to the same destination host
    'dst_host_srv_count': 0,  # Number of flows to the same service on the destination host
    'dst_host_rerror': 0,  # REJ errors for the destination host
})

# Track flows per destination host and service
dst_host_services = defaultdict(lambda: defaultdict(int))

# Service mappings
SERVICE_MAPPINGS = {
    'eco_i': 7,  # Echo service
    'http': 80,  # HTTP service
    'ftp': 21,   # FTP service
    'private': range(49152, 65536),  # Private/dynamic ports
}

# Feature extraction function
def extract_features(packet):
    if IP in packet:  # Filter IPv4 packets
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        src_port = packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else 0
        dst_port = packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else 0

        # Flow key (bidirectional)
        forward_flow_key = (src_ip, dst_ip, src_port, dst_port, proto)
        reverse_flow_key = (dst_ip, src_ip, dst_port, src_port, proto)

        # Update forward flow information
        flows[forward_flow_key]['src_bytes'] += len(packet[IP].payload)
        flows[forward_flow_key]['packets'] += 1

        # Update reverse flow information (for dst_bytes)
        flows[reverse_flow_key]['dst_bytes'] += len(packet[IP].payload)

        # Track TCP flags (RST for REJ errors)
        if TCP in packet and 'R' in str(packet[TCP].flags):
            flows[forward_flow_key]['rerror'] += 1

        # Track services (destination ports)
        flows[forward_flow_key]['services'].add(dst_port)

        # Track destination host and service counts
        for flow_key in flows:
            if flow_key[1] == dst_ip:  # Same destination host
                flows[flow_key]['dst_host_count'] += 1
                if flow_key[3] == dst_port:  # Same service on the destination host
                    flows[flow_key]['dst_host_srv_count'] += 1
                if 'R' in str(packet[TCP].flags) if TCP in packet else False:  # REJ errors for the destination host
                    flows[flow_key]['dst_host_rerror'] += 1

        # Track flows per destination host and service
        dst_host_services[dst_ip][dst_port] += 1

# Calculate dst_host_srv_diff_host_rate
def calculate_dst_host_srv_diff_host_rate(dst_ip, dst_port):
    total_flows_to_host = sum(dst_host_services[dst_ip].values())
    if total_flows_to_host == 0:
        return 0
    same_service_flows = dst_host_services[dst_ip][dst_port]
    diff_service_flows = total_flows_to_host - same_service_flows
    return diff_service_flows / total_flows_to_host

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
        rerror_rate = flow_data['rerror'] / flow_data['packets'] if flow_data['packets'] > 0 else 0
        dst_host_same_srv_rate = flow_data['dst_host_srv_count'] / flow_data['dst_host_count'] if flow_data['dst_host_count'] > 0 else 0
        dst_host_diff_srv_rate = 1 - dst_host_same_srv_rate
        dst_host_same_src_port_rate = same_src_port_flows / flow_data['dst_host_count'] if flow_data['dst_host_count'] > 0 else 0
        dst_host_srv_diff_host_rate = calculate_dst_host_srv_diff_host_rate(dst_ip, dst_port)
        dst_host_rerror_rate = flow_data['dst_host_rerror'] / flow_data['dst_host_count'] if flow_data['dst_host_count'] > 0 else 0

        # Service types (eco_i, private)
        service_eco_i = 1 if dst_port == SERVICE_MAPPINGS['eco_i'] else 0
        service_private = 1 if dst_port in SERVICE_MAPPINGS['private'] else 0

        # Create feature dictionary
        features = {
            'src_bytes': flow_data['src_bytes'],
            'dst_bytes': flow_data['dst_bytes'],
            'count': total_flows,
            'rerror_rate': rerror_rate,
            'dst_host_count': flow_data['dst_host_count'],
            'dst_host_srv_count': flow_data['dst_host_srv_count'],
            'dst_host_same_srv_rate': dst_host_same_srv_rate,
            'dst_host_diff_srv_rate': dst_host_diff_srv_rate,
            'dst_host_same_src_port_rate': dst_host_same_src_port_rate,
            'dst_host_srv_diff_host_rate': dst_host_srv_diff_host_rate,
            'dst_host_rerror_rate': dst_host_rerror_rate,
            'service_eco_i': service_eco_i,
            'service_private': service_private,
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
    sys.exit(1)
    iface = sys.argv[1]
    start_feature_extraction(iface)
from scapy.all import sniff, TCP, IP

# A dictionary to track ongoing connections
handshake_tracker = {}

def detect_handshake(packet):
    if packet.haslayer(TCP):
        tcp_layer = packet[TCP]
        ip_layer = packet[IP]
        
        # Key to uniquely identify the connection
        connection_key = (ip_layer.src, ip_layer.dst, tcp_layer.sport, tcp_layer.dport)
        
        # Detect SYN (step 1)
        if tcp_layer.flags == 'S' or tcp_layer.flags == 'SEC':  # SYN flag
            handshake_tracker[connection_key] = 1  # Mark step 1 complete
            print(f"SYN packet detected from {ip_layer.src}:{tcp_layer.sport} to {ip_layer.dst}:{tcp_layer.dport}")
        
        # Detect SYN-ACK (step 2)
        elif tcp_layer.flags == 'SA':  # SYN-ACK flags
            # Reverse the connection key since the response is from server to client
            reverse_key = (ip_layer.dst, ip_layer.src, tcp_layer.dport, tcp_layer.sport)
            if handshake_tracker.get(reverse_key) == 1:  # Ensure SYN was seen
                handshake_tracker[reverse_key] = 2  # Mark step 2 complete
                print(f"SYN-ACK packet detected from {ip_layer.src}:{tcp_layer.sport} to {ip_layer.dst}:{tcp_layer.dport}")
        
        # Detect ACK (step 3)
        elif tcp_layer.flags == 'A':  # ACK flag
            if handshake_tracker.get(connection_key) == 2:  # Ensure SYN-ACK was seen
                print(f"Three-way handshake complete between {ip_layer.src}:{tcp_layer.sport} and {ip_layer.dst}:{tcp_layer.dport}")
                # Remove connection from the tracker to keep memory usage low
                handshake_tracker.pop(connection_key, None)

# Start sniffing on the desired network interface (replace 'eth0' with your interface)
print("Sniffing for SYN-ACK three-way handshake...")
sniff(filter="tcp", iface="enp0s3", prn=detect_handshake)
  

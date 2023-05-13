"""
DNS Resolver

This script resolves a given domain using a specified DNS resolver. It supports DNS over UDP (User Datagram Protocol),
DNS over TLS (Transport Layer Security), and DNS over HTTPS (Hypertext Transfer Protocol Secure) methods for resolving
the domain.

Usage:
    python resolver.py <DNS resolver> <domain>

Arguments:
    <DNS resolver> (optional):
        - The DNS resolver to use for resolving the domain. It can be provided as:
            - An IP address: The script will use UDP to send the DNS query to the specified IP address.
            - A domain name: The script will use DNS over TLS (DOT) to send the DNS query to the specified domain.
            - A DOH URL (starting with 'https'): The script will use DNS over HTTPS (DOH) to send the DNS query.

    <domain> (required):
        - The domain to be resolved. It should be provided as a fully qualified domain name (FQDN).

Examples:
    python resolver.py 8.8.8.8 example.com
        - Resolves the domain 'example.com' using the DNS resolver at IP address '8.8.8.8' via UDP.

    python resolver.py dns.example.com example.com
        - Resolves the domain 'example.com' using the DNS resolver at 'dns.example.com' via DNS over TLS (DOT).

    python resolver.py https://dns.example.com/dns-query example.com
        - Resolves the domain 'example.com' using the DNS resolver at 'https://dns.example.com/dns-query' via DNS over HTTPS (DOH).

Note:
    - If only the DNS resolver is not provided, the script will use the system's default resolver
      and attempt to resolve the domain using UDP.

Dependencies:
    - The script requires the 'dnspython' library to be installed. You can install it using pip:
        pip install dnspython

"""

import subprocess
import sys
import re
import socket
import dns.query
import dns.resolver
import urllib.parse
from concurrent.futures import ThreadPoolExecutor


def resolve(domain, DnsHostname, DnsIP, QueryMethod):
    """
    Resolves the given domain using the specified DNS resolver.

    Args:
        domain (str): The domain to be resolved.
        DnsHostname (str): The hostname of the DNS resolver.
        DnsIP (str): The IP address of the DNS resolver.
        QueryMethod (str): The method used for DNS resolution (DOT, DOH, or UDP).

    Returns:
        None

    Raises:
        Exception: If an error occurs during resolution.

    """
    try:
        if QueryMethod == 'DOT':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+', dns.query.tls(dns.message.make_query(dns.name.from_text(
                domain), dns.rdatatype.A), DnsIP, server_hostname=DnsHostname, timeout=5).to_text())

        elif QueryMethod == 'DOH':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+', dns.query.https(dns.message.make_query(
                dns.name.from_text(domain), dns.rdatatype.A), DnsHostname, timeout=5).to_text())

        elif QueryMethod == 'UDP':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+', dns.query.udp(dns.message.make_query(
                dns.name.from_text(domain), dns.rdatatype.A), DnsIP, timeout=5).to_text())

        if ipaddr:
            #print("Resolved IP address for domain '{}' using {} on {}: \n{}".format(domain, QueryMethod, DnsIP if QueryMethod == 'UDP' else DnsHostname, ipaddr))
            print("Resolved IP address for domain '{}' using {} on {}: ".format(domain, QueryMethod, DnsIP if QueryMethod == 'UDP' else DnsHostname))
            
            # Create a thread pool executor with a maximum number of threads
            with ThreadPoolExecutor() as executor:
                # Submit ping tasks to the executor
                ping_tasks = [executor.submit(ping_ip, ip) for ip in ipaddr]
                
                # Retrieve the results from the completed tasks
                for task, ip in zip(ping_tasks, ipaddr):
                    ping_ms = task.result()
                    print("{} (Ping: {} ms)".format(ip, ping_ms))

        else:
            print("Could not resolve an IP address for domain '{}' using {} on {}".format(domain, QueryMethod, DnsIP if QueryMethod == 'UDP' else DnsHostname))
    except Exception as e:
        print("Error during resolution: {}".format(e))

def ping_ip(ip):
    try:
        # Execute the ping command once and capture the output
        if sys.platform.startswith('win'):
            command = ['ping', '-n', '1', ip]  # Windows uses -n option to specify number of pings
        else:
            command = ['ping', '-c', '1', ip]  # Unix-like systems use -c option to specify number of pings

        result = subprocess.run(command, capture_output=True, text=True)
        
        # Parse the output to retrieve the latency (ms)
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines:
            if 'time=' in line:
                latency = re.findall(r'time=(\d+\.?\d*)', line)
                if latency:
                    return latency[0]
        return "N/A"  # If ping failed or latency not found
    except:
        return "N/A"  # If ping execution failed
    

def setDNS(i):
    """
    Sets the DNS resolver details based on the input.

    Args:
        i (str): The input for DNS resolver (either a DOH URL, domain, or IP address).

    Returns:
        tuple: A tuple containing the DnsHostname, DnsIP, and QueryMethod.

    """
    DnsHostname = None
    DnsIP = None
    QueryMethod = None

    if i.startswith('https'):  # Input is a DOH URL
        DnsHostname = i
        QueryMethod = "DOH"
    else:
        try:
            DnsIP = socket.gethostbyname(i)
            if DnsIP == i:  # Input is an IP address
                QueryMethod = "UDP"
            else:  # Input is a domain
                DnsHostname = i
                QueryMethod = "DOT"
        except:
            print("Input DNS failed. Using Default DNS")
            DnsIP = socket.gethostbyname(socket.gethostname())  # Default DNS
            QueryMethod = "UDP"  # Default method
    
    return DnsHostname, DnsIP, QueryMethod




if __name__ == '__main__':
    if len(sys.argv) < 2:
        # If no command-line arguments provided
        print("Please provide the DNS resolver and domain to resolve as command line arguments.")
        sys.exit(1)
    elif len(sys.argv) < 3:
        # Only the DNS resolver provided, use system default resolver
        domain = sys.argv[1]
        DnsIP = dns.resolver.Resolver().nameservers[-1]
        DnsHostname = None
        QueryMethod = "UDP"
    elif len(sys.argv) == 3: 
        # DNS resolver and domain provided
        DnsHostname, DnsIP, QueryMethod = setDNS(sys.argv[1])
        domain = sys.argv[2]

    resolve(domain, DnsHostname, DnsIP, QueryMethod)


    
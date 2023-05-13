import sys
import re
import itertools
import socket
import time
from collections import Counter

import dns.resolver
import dns.query
import dns.message
import urllib.request
from urllib.parse import urlparse
# DnsHostname = 'dns.quad9.net'
#DnsIP='8.8.8.8'
#DnsHostname='https://1.1.1.2/dns-query'
# DnsHostname='https://blitz.ahadns.com/1:2.8.20.22'
# DnsHostname='https://blitz.ahadns.com/1:1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27'
# DnsIP ='103.247.36.36' # DNSFilter
#DnsHostname='https://doh.z-w.ca'
DnsHostname='7ee455.dns.nextdns.io'



def resolve(domain):
    global DnsHostname
    global DnsIP
    global QueryMethod

    # Reject if just IP address, not domain
    if (re.findall('\d+\.\d+\.\d+\.\d+', domain)):
        return

    try:
        if QueryMethod == 'DOT':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+', dns.query.tls(dns.message.make_query(dns.name.from_text(
                domain), dns.rdatatype.A), DnsIP, server_hostname=DnsHostname, timeout=5).to_text())[0]

        elif QueryMethod == 'DOH':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+', dns.query.https(dns.message.make_query(
                dns.name.from_text(domain), dns.rdatatype.A), DnsHostname, timeout=5).to_text())[0]

        elif QueryMethod == 'UDP':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+', dns.query.udp(dns.message.make_query(
                dns.name.from_text(domain), dns.rdatatype.A), DnsIP, timeout=5).to_text())[0]

        print("{} with {} on {}: {}".format(domain, QueryMethod, DnsIP if QueryMethod == 'UDP' else DnsHostname, ipaddr))
        #time.sleep(1)
        return(ipaddr)
    except:
        pass


def setDNS(i):
    global DnsHostname
    global DnsIP

    # if sys input DNS resolver domain/IP is wrong, just use system resolver
    try:
        HostIP = socket.gethostbyname(i)
    except:
        print("Input DNS failed. Use Default DNS")
        return

    DnsIP = HostIP

    # Detect if sys input is IP address for UDP, or domain for DOT/DOH
    if HostIP == i:
        try:
            del DnsHostname
        except:
            pass
    else:
        DnsHostname = i


def main():
    # Set DNS from sys input (if exists)
    if len(sys.argv) >= 2:
        server = sys.argv[1]
        domain = sys.argv[2]
    else:
        print("Input: dns-server, domain")
        exit()

    setDNS(i)
    

    # If DNS IP not defined earlier or sys input, use system default resolver
    try:
        DnsIP
    except NameError:
        dnsresolver = dns.resolver.Resolver()
        DnsIP = dnsresolver.nameservers[0]

    # Final try: check if there is a defined DOT/DOH resolver. After that, set DNS query method
    try:
        DnsHostname
    except NameError:
        QueryMethod = "UDP"
        print("UDP: {}".format(DnsIP))
    else:
        DnsIP = socket.gethostbyname(urllib.parse.urlparse(DnsHostname).netloc if bool(re.search("^https", DnsHostname)) else DnsHostname)

        if bool(re.search('^https', DnsHostname)):
            QueryMethod = "DOH"
            print("DOH: {}".format(DnsHostname))
        else:
            QueryMethod = "DOT"
            print("DOT: {},{}".format(DnsHostname, DnsIP))

    # Add DNS IP to blocked IP
    BlockedIPs.append(DnsIP)

    # Read test url/domain list and remove duplicates
    data = list(set(itertools.chain.from_iterable(
        [urllib.request.urlopen(i).readlines() for i in feedurl])))

    # Perform DNS test. If possible, resolve domains in parallel. Also parse link into domain
    try:
        import concurrent.futures
    except ImportError:
        print("Single Thread ...")
        result = [resolve(urlparse(line.strip()).netloc.decode() if re.search("http", line.decode()) else line.decode().strip()) for line in data]
    else:
        print("Multiple Thread ...")
        #result = Parallel(n_jobs=10)(delayed(resolve)(urlparse(line.strip()).netloc.decode() if re.search("http", line.decode()) else line.decode().strip()) for line in data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_results = {executor.submit(resolve, urlparse(line.strip()).netloc.decode() if re.search("http", line.decode()) else line.decode().strip()): line for line in data}
            result = []
            for future in concurrent.futures.as_completed(future_results):
                result.append(future.result())




if __name__ == '__main__':
    main()




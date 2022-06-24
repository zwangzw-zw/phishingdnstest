from urllib.parse import urlparse
from collections import Counter

import urllib.request
import dns.resolver
import sys
import re
import itertools
import socket
import time


import dns.query, dns.message
#DnsHostname='testdevice-743511.dns.nextdns.io'
#DnsHostname='5dad78d6.d.adguard-dns.com'
DnsHostname='dns.quad9.net'
#DnsIP='8.8.8.8'
#DnsHostname='https://1.1.1.1/dns-query'
#DnsHostname='https://blitz.ahadns.com/1:2.8.20.22'
#DnsHostname='https://blitz.ahadns.com/1:1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27'
#DnsIP ='103.247.36.36' # DNSFilter

#feedurl=['https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-domains-NEW-today.txt']
#feedurl=['https://openphish.com/feed.txt']

feedurl=['https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-domains-NEW-today.txt',
        'https://openphish.com/feed.txt'
]

BlockedIPs=[
        '0.0.0.0',
        '127.0.0.1',
        '94.140.14.33', #Adguard
        '198.251.90.71' #DNSFilter
        ]




def resolve(domain):
    global DnsHostname
    global DnsIP
    global QueryMethod
    #DnsIP=DnsIP[0]
    if (re.findall('\d+\.\d+\.\d+\.\d+',domain)):
        #print("Invalid Domain {}".format(domain))
        return


    try:
#        print(QueryMethod,DnsIP)
        if QueryMethod == 'DOT':
#        ipaddr = dnsresolver.resolve(domain,'A').rrset[0].address
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+',dns.query.tls(dns.message.make_query(dns.name.from_text(domain),dns.rdatatype.A),DnsIP,server_hostname=DnsHostname,timeout=5).to_text())[0]
#            print(domain,ipaddr)
        elif QueryMethod == 'DOH':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+',dns.query.https(dns.message.make_query(dns.name.from_text(domain),dns.rdatatype.A),DnsHostname,timeout=5).to_text())[0]
#            print(domain,ipaddr)
        elif QueryMethod == 'UDP':
            ipaddr = re.findall('\d+\.\d+\.\d+\.\d+',dns.query.udp(dns.message.make_query(dns.name.from_text(domain),dns.rdatatype.A),DnsIP,timeout=5).to_text())[0]
#            if ipaddr != domain:
#                print(domain,ipaddr)
        #print("domain {} ip {}, method {}".format(domain,ipaddr,QueryMethod))
        #print("{} with {} on {}: {}".format(domain, QueryMethod, DnsIP if QueryMethod == 'UDP' else DnsHostname, ipaddr))
        time.sleep(1)
        return(ipaddr)
    except:
        pass



def setDNS(i):
    global DnsHostname
    global DnsIP

    try:
        HostIP = socket.gethostbyname(i)
    except:
        print("Input DNS failed. Use Default DNS")
        return

    DnsIP = HostIP

    if HostIP == i:
        #print("UDP from input, {}".format(DnsIP))
        try: 
            del DnsHostname
        except:
            pass
    else:
        DnsHostname = i
        #print("DOT from input, {}".format(DnsHostname))
        
    



if __name__ == '__main__':


    dnsresolver=dns.resolver.Resolver()



  #  try:
  #      DnsIP
  #  except:
  #      DnsIP=dnsresolver.nameservers[0]





    if len(sys.argv) >= 1:
        try:
            setDNS(sys.argv[1])
        except:
            pass

    try:
        DnsIP
    except NameError:
        DnsIP=dnsresolver.nameservers[0]

    try:
        DnsHostname
    except NameError:
        QueryMethod = "UDP"
        print("UDP: {}".format(DnsIP))
    else:
        DnsIP=socket.gethostbyname(urlparse(DnsHostname).netloc if bool(re.search("^https",DnsHostname)) else DnsHostname)

        if bool(re.search('^https',DnsHostname)):
            QueryMethod = "DOH"
            print("DOH: {}".format(DnsHostname))
        else:
            QueryMethod = "DOT"
            print("DOT: {},{}".format(DnsHostname,DnsIP))

    # Add DNS IP to blocked IP
    BlockedIPs.append(DnsIP)

   
    # Read list and remove duplicate
    data=list(set(itertools.chain.from_iterable([urllib.request.urlopen(i).readlines() for i in feedurl])))

   
    
    try:
        from joblib import Parallel, delayed
    except:
        print("Single Thread ...")
        result=[resolve(urlparse(line.strip()).netloc.decode() if bool(re.search("http",line.decode())) else line.decode().strip()) for line in data]
    else:
        print("Multiple Thread ...")
        result=Parallel(n_jobs=10) (delayed(resolve)(urlparse(line.strip()).netloc.decode() if bool(re.search("http",line.decode())) else line.decode().strip()) for line in data)
    
    
    result = list(filter(lambda x: x is not None, result))
    #DNSBlocked=sum([Counter(result).get(v) for v in BlockedIPs])
    
    DNSBlocked=sum([result.count(x) for x in BlockedIPs])
    #result.count('94.140.14.33')
    #DNSBlocked=result.count('0.0.0.0')
    ValidDomains=len(result)#-result.count(None)

    print("Blocked IP range: {}".format(BlockedIPs))
    print("Most commonly blocked IPs: {}".format(Counter(result).most_common(10)))
    #print('Adguard: {}; DNS: {}; Total: {}; Blocked: {:.0%}; Resolver: {}'.format(AGBlocked,DNSBlocked, ValidDomains, (AGBlocked+DNSBlocked)/ValidDomains, dnsresolver.nameservers[0]))
    print('Blocked {}; Total: {}; Blocked: {:.0%}; Resolver: {}'.format(DNSBlocked, ValidDomains, (DNSBlocked)/ValidDomains, DnsIP if QueryMethod == 'UDP' else DnsHostname))
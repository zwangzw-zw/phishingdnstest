from urllib.parse import urlparse
import urllib.request
import dns.resolver
import sys
#import socket   #if using systmem resolver


dnsresolver=dns.resolver.Resolver()

try:
    dnsresolver.nameservers = sys.argv[1].split()
except:
    pass

#if sys.argv[1] != '':
#    dnsresolver.nameservers = sys.argv[1].split()

print(dnsresolver.nameservers[0])

ValidDomains, AGBlocked, DNSBlocked = 0, 0, 0

feed=urllib.request.urlopen("https://openphish.com/feed.txt")
data=feed.readlines()

for line in data:
#    line = line.strip().decode('utf-8').replace(",","")
    domain=urlparse(line).netloc.decode('utf-8')
#    try:
#        ipaddr=socket.gethostbyname(domain)
#    except socket.gaierror:
#        pass

    try:
        ipaddr=dnsresolver.resolve(domain,'A').rrset[0].address
    except:
        pass

    if ipaddr != domain:
        ValidDomains += 1
        if ipaddr == '94.140.14.33':
                AGBlocked += 1
        elif ipaddr == '0.0.0.0':
                DNSBlocked += 1

print('Adguard: {}; DNS: {}; Total: {}; Blocked: {:.0%}; Resolver: {}'.format(AGBlocked,DNSBlocked, ValidDomains, (AGBlocked+DNSBlocked)/ValidDomains, dnsresolver.nameservers[0]))

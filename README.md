# DNS Resolver Project

## Introduction

This Python project is designed to perform DNS queries for a list of domains and check if they are blocked by a specified DNS server. The project supports DNS over HTTPS (DOH), DNS over TLS (DOT), and standard UDP-based DNS queries. It also calculates the percentage of domains blocked by the DNS server and lists the most common non-blocked IP addresses.

The DNS server can be specified as a command-line argument when running the script. If no DNS server is specified, the script will use the first DNS server listed in the system's DNS resolver.

## Dependencies

This project requires Python 3 and the following Python packages:

- dnspython
- urllib3
- concurrent.futures

You can install these dependencies using pip:

```
pip install dnspython urllib3 futures
```

## Usage

To run the script, use the following command:

```
python dns_resolver.py [DNS server]
```

Replace `[DNS server]` with the hostname or IP address of the DNS server you want to use. This argument is optional.

The script will print the results to the console. You can redirect the output to a file using the `>` operator:

```
python dns_resolver.py > results.txt
```

## Customization

You can customize the list of blocked IP addresses and the feed URL list by modifying the `BlockedIPs` and `feedurl` variables in the script.

## Output

The script will print the following information:

- The blocked IP range
- The number of blocked domains
- The total number of valid domains
- The percentage of blocked domains
- The DNS resolver used for the queries
- The top 10 most common non-blocked IP addresses

## License

This project is open source and available under the [BSD 3-Clause License](LICENSE).


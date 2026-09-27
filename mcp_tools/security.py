"""SSRF protection and URL validation for MCP tools.

Blocks requests to localhost, loopback, private/reserved IP ranges,
and non-HTTP(S) schemes. Required by the Developer Handoff security
requirements before the inspect_page tool is publicly exposed.
"""

import ipaddress
import socket
from urllib.parse import urlparse


class SSRFError(Exception):
    """Raised when a URL fails SSRF validation."""
    pass


# Private and reserved IP ranges to block
BLOCKED_RANGES = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0", "[::]", "[::1]"}


def validate_url(url: str) -> str:
    """Validate a URL for SSRF safety.

    Checks scheme, hostname, and resolved IP addresses against known
    private/reserved ranges. Returns the validated URL on success.

    Raises:
        SSRFError: If the URL fails any safety check.
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise SSRFError(f"Blocked scheme: {parsed.scheme}. Only http/https allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("No hostname in URL.")

    if hostname.lower() in BLOCKED_HOSTNAMES:
        raise SSRFError(f"Blocked hostname: {hostname}")

    # Resolve hostname and check every returned IP
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        infos = socket.getaddrinfo(hostname, port)
    except socket.gaierror:
        raise SSRFError(f"Cannot resolve hostname: {hostname}")

    for _family, _type, _proto, _canonname, sockaddr in infos:
        ip_str = sockaddr[0]
        ip = ipaddress.ip_address(ip_str)
        for network in BLOCKED_RANGES:
            if ip in network:
                raise SSRFError(
                    f"Blocked IP range: {ip_str} resolves into {network}"
                )

    return url

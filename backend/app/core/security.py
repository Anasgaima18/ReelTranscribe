"""
Security and SSRF protection utilities for ReelTranscribe.
"""
import ipaddress
import socket
from urllib.parse import urlparse
from backend.app.core.errors import InvalidURLError, UnsupportedURLError, SSRFSecurityError

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "instance-data",
    "169.254.169.254",
    "metadata.azure.com",
    "kubernetes.default.svc"
}

ALLOWED_SCHEMES = {"http", "https"}


def is_ip_allowed(ip_str: str) -> bool:
    """
    Validates that an IP address is a globally routable public address.
    Rejects private, loopback, link-local, multicast, and reserved ranges.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
        # Specific check for AWS/GCP/Azure link-local metadata address
        if str(ip) == "169.254.169.254":
            return False
        return True
    except ValueError:
        return False


def validate_url_security(url: str) -> str:
    """
    Strictly validates a URL against SSRF and unauthorized scheme attacks.
    Returns the sanitized URL if valid, raises AppError otherwise.
    """
    if not url or not isinstance(url, str):
        raise InvalidURLError("URL must be a non-empty string.")

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        raise InvalidURLError("Malformed URL could not be parsed.")

    scheme = parsed.scheme.lower()
    if not scheme:
        raise InvalidURLError("URL is missing a valid scheme (e.g., https://).")
    if scheme not in ALLOWED_SCHEMES:
        raise UnsupportedURLError(f"Unsupported URL scheme '{scheme}'. Only HTTP/HTTPS are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise InvalidURLError("URL is missing a valid hostname.")

    hostname_lower = hostname.lower()

    if hostname_lower in BLOCKED_HOSTNAMES or hostname_lower.endswith(".local"):
        raise SSRFSecurityError(f"Access to blocked hostname '{hostname}' is prohibited.")

    # Check if hostname is an explicit IP literal
    try:
        if not is_ip_allowed(hostname_lower):
            raise SSRFSecurityError(f"Access to private/internal IP '{hostname}' is prohibited.")
    except ValueError:
        pass

    # Resolve DNS to verify all destination IPs
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for entry in addr_info:
            sockaddr = entry[4]
            ip_candidate = sockaddr[0]
            if not is_ip_allowed(ip_candidate):
                raise SSRFSecurityError(
                    f"Hostname '{hostname}' resolves to private/internal IP '{ip_candidate}', which is prohibited."
                )
    except socket.gaierror:
        # If DNS resolution fails, raise InvalidURLError
        raise InvalidURLError(f"Could not resolve hostname '{hostname}'.")
    except SSRFSecurityError:
        raise
    except Exception as e:
        raise InvalidURLError(f"DNS validation error for hostname '{hostname}': {str(e)}")

    return url

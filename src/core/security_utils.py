"""
Security utilities voor input validatie en sanitization.
"""
import re
import html
from urllib.parse import urlparse


CANONICAL_SERVICE_URLS = {
    "microsoft_admin": "https://admin.microsoft.com",
    "intune_admin": "https://intune.microsoft.com",
    "azure_admin": "https://portal.azure.com",
    "google_admin": "https://admin.google.com",
    "easy4u": "https://easy4u.nl/admin/",
}


LOCKED_URL_SERVICES = set(CANONICAL_SERVICE_URLS)


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize een string input om XSS te voorkomen.
    
    Args:
        value: De input string
        max_length: Maximale lengte van de string
        
    Returns:
        Gezuiverde string
    """
    if not isinstance(value, str):
        return ""
    
    # Trim whitespace
    value = value.strip()
    
    # Limiteer lengte
    if len(value) > max_length:
        value = value[:max_length]
    
    # Escape HTML special characters (voorkomt XSS)
    value = html.escape(value)
    
    return value


def validate_email(email: str) -> bool:
    """
    Valideer een e-mail adres.
    
    Args:
        email: E-mail adres om te valideren
        
    Returns:
        True als geldig, anders False
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basis e-mail regex validatie
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def validate_url(url: str) -> bool:
    """
    Valideer een URL.
    
    Args:
        url: URL om te valideren
        
    Returns:
        True als geldig, anders False
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url.strip())
        # Moet een scheme hebben (http/https) en netloc (domain)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def validate_hostname(hostname: str) -> bool:
    """
    Valideer een hostname of IP adres.
    
    Args:
        hostname: Hostname of IP adres
        
    Returns:
        True als geldig, anders False
    """
    if not hostname or not isinstance(hostname, str):
        return False
    
    hostname = hostname.strip()
    
    # IP adres validatie (IPv4)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, hostname):
        parts = hostname.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # Hostname validatie (basis)
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(hostname_pattern, hostname)) and len(hostname) <= 253


def validate_port(port: int | str) -> bool:
    """
    Valideer een poort nummer.
    
    Args:
        port: Poort nummer
        
    Returns:
        True als geldig (1-65535), anders False
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitize een file path om path traversal te voorkomen.
    
    Args:
        file_path: File path
        
    Returns:
        Gezuiverde file path
    """
    if not isinstance(file_path, str):
        return ""
    
    # Verwijder gevaarlijke characters
    file_path = file_path.strip()
    
    # Verwijder path traversal attempts
    file_path = file_path.replace('..', '')
    file_path = file_path.replace('//', '/')
    
    # Escape special characters
    file_path = html.escape(file_path)
    
    return file_path


def validate_service_name(service: str) -> bool:
    """
    Valideer een service naam.
    
    Args:
        service: Service naam
        
    Returns:
        True als geldig, anders False
    """
    valid_services = [
        "smartschool",
        "smartschool_admin",
        "microsoft_admin",
        "google_admin",
        "intune_admin",
        "azure_admin",
        "easy4u",
    ]
    return service in valid_services


def canonical_service_url(service: str) -> str:
    """Geef de officiële vaste URL terug voor services met gelockte portal-URL."""
    return CANONICAL_SERVICE_URLS.get(service, "")


def is_service_url_locked(service: str) -> bool:
    """Bepaal of de URL voor deze service niet vrij instelbaar mag zijn."""
    return service in LOCKED_URL_SERVICES


def normalize_service_url(service: str, url: str) -> str:
    """
    Normaliseer service-URL's.

    Voor admin portals en Easy4U forceren we de officiële URL om phishing,
    typo's en ongewenste redirects te vermijden.
    """
    if is_service_url_locked(service):
        return canonical_service_url(service)

    if not validate_url(url):
        return ""
    return url.strip()


def preserve_existing_secret(new_value: str | None, existing_value: str | None = None) -> str:
    """
    Gebruik een nieuw geheim als het expliciet is ingevuld, anders behoud het oude.
    """
    if new_value is None:
        return existing_value or ""
    if isinstance(new_value, str) and new_value != "":
        return new_value
    return existing_value or ""


def sanitize_json_input(data: dict, allowed_keys: list[str]) -> dict:
    """
    Sanitize JSON input data en filter alleen toegestane keys.
    
    Args:
        data: Input dictionary
        allowed_keys: Lijst van toegestane keys
        
    Returns:
        Gezuiverde dictionary met alleen toegestane keys
    """
    if not isinstance(data, dict):
        return {}
    
    sanitized = {}
    for key in allowed_keys:
        if key in data:
            value = data[key]
            if isinstance(value, str):
                sanitized[key] = sanitize_string(value)
            elif isinstance(value, (int, float)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
    
    return sanitized

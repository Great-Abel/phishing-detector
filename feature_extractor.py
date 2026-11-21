from urllib.parse import urlparse
import re
import ipaddress

SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "account", "update",
    "confirm", "bank", "paypal", "signin", "password"
]


def is_ip_address(domain):
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False


def extract_features(url):
    url = str(url).strip()

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    features = {
        "url_length": len(url),
        "domain_length": len(domain),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_question_marks": url.count("?"),
        "num_equal_signs": url.count("="),
        "num_slashes": url.count("/"),
        "num_digits": sum(char.isdigit() for char in url),
        "has_at_symbol": int("@" in url),
        "has_https": int(parsed.scheme == "https"),
        "has_ip_address": int(is_ip_address(domain)),
        "has_suspicious_word": int(
            any(word in url.lower() for word in SUSPICIOUS_WORDS)
        ),
        "path_length": len(path),
        "num_special_chars": len(re.findall(r"[^a-zA-Z0-9]", url))
    }

    return features
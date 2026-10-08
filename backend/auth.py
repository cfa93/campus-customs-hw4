"""Password hashing and verification for Campus Customs accounts.

Passwords are never stored in plain text. We store a PBKDF2-HMAC-SHA256 hash
in a self-describing format so the verifier knows exactly how to recompute it:

    pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
"""

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Return a self-describing PBKDF2-SHA256 hash for a new account."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against a stored hash in our 4-field format.

    Returns False for any hash we can't parse (for example seed rows created by
    a different, unknown scheme) rather than raising.
    """
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
    # Constant-time compare so timing doesn't leak how much of the hash matched.
    return hmac.compare_digest(candidate, expected)

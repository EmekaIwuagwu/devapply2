"""
Credential encryption helpers for LinkedIn (and future platform) credentials.

Uses Fernet symmetric encryption (from the cryptography package).
The encryption key is derived from JWT_SECRET_KEY via SHA-256 + base64url,
so no extra environment variable is required for a default setup.

To use a dedicated key (recommended for production), set:
    LINKEDIN_ENCRYPT_KEY=<32-byte base64url-encoded key>

Generate one with:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)


def _get_fernet():
    from cryptography.fernet import Fernet
    from app.config import settings

    raw_key = getattr(settings, "LINKEDIN_ENCRYPT_KEY", None)
    if raw_key:
        key = raw_key.encode() if isinstance(raw_key, str) else raw_key
    else:
        # Derive a stable 32-byte key from JWT_SECRET_KEY
        digest = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()
        key = base64.urlsafe_b64encode(digest)

    return Fernet(key)


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a plaintext credential string. Returns a base64url token."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_credential(ciphertext: str) -> str:
    """Decrypt an encrypted credential token. Returns the original plaintext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()


def safe_decrypt(ciphertext: str) -> str:
    """Decrypt, returning empty string on any error (e.g. wrong key, corrupted data)."""
    try:
        return decrypt_credential(ciphertext)
    except Exception as e:
        logger.warning(f"Credential decryption failed: {e}")
        return ""

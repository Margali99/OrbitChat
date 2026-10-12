import base64
import os
from cryptography.fernet import Fernet
from app.config import settings

def _get_fernet() -> Fernet:
    secret = settings.key_encryption_secret
    if not secret:
        # Fallback secret for local testing
        secret = "orbit_default_32byte_secret_key!"
    
    # Fernet requires 32 url-safe base64-encoded bytes
    if len(secret) == 44 and secret.endswith("="):
        try:
            return Fernet(secret.encode())
        except Exception:
            pass
            
    # Hash/pad to 32 bytes and urlsafe base64 encode
    raw_key = secret.ljust(32)[:32].encode()
    b64_key = base64.urlsafe_b64encode(raw_key)
    return Fernet(b64_key)

def encrypt_key(plain_key: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain_key.encode()).decode()

def decrypt_key(encrypted_key: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted_key.encode()).decode()

from typing import Dict, Optional, Union, Tuple
import logging
from dataclasses import dataclass
import json
import hashlib
import base64
import os
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

@dataclass
class EncryptionConfig:
    key_derivation_salt: bytes
    key_derivation_iterations: int = 100000
    key_length: int = 32
    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    min_key_length: int = 32
    allow_key_rotation: bool = True
    store_key_metadata: bool = True
    compression_enabled: bool = True
    compression_level: int = 6
    backup_enabled: bool = True
    backup_interval_hours: int = 24

class EncryptionEngine:
    def __init__(self, config: Optional[EncryptionConfig] = None):
        self.config = config or EncryptionConfig(
            key_derivation_salt=os.urandom(16)
        )
        self.logger = logging.getLogger(__name__)
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption parameters and key derivation."""
        self.backend = default_backend()
        self._setup_key_derivation()

    def _setup_key_derivation(self):
        """Setup key derivation function."""
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.config.key_length,
            salt=self.config.key_derivation_salt,
            iterations=self.config.key_derivation_iterations,
            backend=self.backend
        )

    def derive_key(self, password: str) -> bytes:
        """Derive an encryption key from a password."""
        return base64.urlsafe_b64encode(
            self.kdf.derive(password.encode())
        )

    def encrypt_data(
        self,
        data: Union[str, bytes, Dict],
        key: bytes,
        metadata: Optional[Dict] = None
    ) -> Tuple[bytes, Dict]:
        """Encrypt data with associated metadata."""
        if isinstance(data, (str, Dict)):
            data = json.dumps(data).encode()

        # Generate a random IV
        iv = os.urandom(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()

        # Add associated data if provided
        if metadata:
            encryptor.authenticate_additional_data(
                json.dumps(metadata).encode()
            )

        # Encrypt the data
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Get the authentication tag
        tag = encryptor.tag

        # Combine IV, ciphertext, and tag
        encrypted_data = iv + tag + ciphertext

        # Create encryption metadata
        encryption_metadata = {
            "algorithm": self.config.algorithm,
            "iv_length": len(iv),
            "tag_length": len(tag),
            "timestamp": datetime.utcnow().isoformat(),
            "key_version": self._get_key_version(),
            "compression": self.config.compression_enabled,
            "compression_level": self.config.compression_level
        }

        if metadata:
            encryption_metadata.update(metadata)

        return encrypted_data, encryption_metadata

    def decrypt_data(
        self,
        encrypted_data: bytes,
        key: bytes,
        metadata: Optional[Dict] = None
    ) -> Union[str, bytes, Dict]:
        """Decrypt data and verify its integrity."""
        # Extract IV, tag, and ciphertext
        iv_length = 12  # AES-GCM uses 12-byte IV
        tag_length = 16  # AES-GCM uses 16-byte tag
        iv = encrypted_data[:iv_length]
        tag = encrypted_data[iv_length:iv_length + tag_length]
        ciphertext = encrypted_data[iv_length + tag_length:]

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()

        # Add associated data if provided
        if metadata:
            decryptor.authenticate_additional_data(
                json.dumps(metadata).encode()
            )

        # Decrypt the data
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Try to decode as JSON if it looks like JSON
        try:
            return json.loads(decrypted_data.decode())
        except json.JSONDecodeError:
            return decrypted_data

    def rotate_key(self, old_key: bytes, new_password: str) -> bytes:
        """Rotate the encryption key."""
        if not self.config.allow_key_rotation:
            raise ValueError("Key rotation is not enabled")

        # Derive new key
        new_key = self.derive_key(new_password)

        # Update key metadata
        self._update_key_metadata(new_key)

        return new_key

    def _update_key_metadata(self, key: bytes):
        """Update metadata for the current key."""
        key_hash = hashlib.sha256(key).hexdigest()
        metadata = {
            "key_hash": key_hash,
            "created_at": datetime.utcnow().isoformat(),
            "rotation_days": self.config.key_rotation_days,
            "algorithm": self.config.algorithm
        }
        
        # Store key metadata if enabled
        if self.config.store_key_metadata:
            self._store_metadata(metadata)

    def _get_key_version(self) -> str:
        """Get the current key version."""
        return hashlib.sha256(
            self.config.key_derivation_salt
        ).hexdigest()[:8]

    def _store_metadata(self, metadata: Dict):
        """Store encryption metadata."""
        # Implementation would depend on storage backend
        pass

    def verify_key_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Verify the strength of a password."""
        issues = []
        
        # Check minimum length
        if len(password) < self.config.min_key_length:
            issues.append(
                f"Password must be at least {self.config.min_key_length} characters"
            )
        
        # Check for common patterns
        if password.isalpha() or password.isnumeric():
            issues.append("Password should contain both letters and numbers")
        
        # Check for special characters
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password should contain special characters")
        
        # Check for common passwords
        if self._is_common_password(password):
            issues.append("Password is too common")
        
        return len(issues) == 0, issues

    def _is_common_password(self, password: str) -> bool:
        """Check if a password is in a list of common passwords."""
        # Implementation would check against a list of common passwords
        return False

    def generate_backup_key(self) -> bytes:
        """Generate a backup encryption key."""
        return os.urandom(self.config.key_length)

    def create_backup(
        self,
        data: bytes,
        backup_key: bytes,
        metadata: Optional[Dict] = None
    ) -> Tuple[bytes, Dict]:
        """Create an encrypted backup of data."""
        backup_metadata = {
            "backup_timestamp": datetime.utcnow().isoformat(),
            "backup_version": "1.0",
            "original_size": len(data),
            "compression_enabled": self.config.compression_enabled
        }
        
        if metadata:
            backup_metadata.update(metadata)
        
        return self.encrypt_data(data, backup_key, backup_metadata)

    def restore_backup(
        self,
        backup_data: bytes,
        backup_key: bytes,
        metadata: Optional[Dict] = None
    ) -> bytes:
        """Restore data from a backup."""
        return self.decrypt_data(backup_data, backup_key, metadata)

    def get_encryption_status(self) -> Dict:
        """Get the current status of the encryption system."""
        return {
            "algorithm": self.config.algorithm,
            "key_rotation": {
                "enabled": self.config.allow_key_rotation,
                "interval_days": self.config.key_rotation_days
            },
            "compression": {
                "enabled": self.config.compression_enabled,
                "level": self.config.compression_level
            },
            "backup": {
                "enabled": self.config.backup_enabled,
                "interval_hours": self.config.backup_interval_hours
            },
            "key_derivation": {
                "iterations": self.config.key_derivation_iterations,
                "key_length": self.config.key_length
            }
        }

    def validate_encryption_config(self) -> Tuple[bool, List[str]]:
        """Validate the encryption configuration."""
        issues = []
        
        # Check key length
        if self.config.key_length < 32:
            issues.append("Key length should be at least 32 bytes")
        
        # Check iterations
        if self.config.key_derivation_iterations < 100000:
            issues.append(
                "Key derivation iterations should be at least 100000"
            )
        
        # Check compression level
        if not 0 <= self.config.compression_level <= 9:
            issues.append("Compression level must be between 0 and 9")
        
        # Check backup interval
        if self.config.backup_interval_hours < 1:
            issues.append("Backup interval must be at least 1 hour")
        
        return len(issues) == 0, issues 
"""
CalTopoCredentialHelper - Helper for encrypting/decrypting CalTopo API credentials.

Provides secure storage of Team ID and Credential Secret using encryption.
"""

import base64
import hashlib
import os
from PySide6.QtCore import QSettings


class CalTopoCredentialHelper:
    """Helper class for managing encrypted CalTopo API credentials."""

    def __init__(self):
        """Initialize the credential helper."""
        self.settings = QSettings("ADIAT", "CalTopoAPI")
        self._encryption_key = self._get_encryption_key()

    def _get_encryption_key(self):
        """Generate a system-specific encryption key.

        Returns:
            bytes: Encryption key derived from system information
        """
        # Use a combination of system-specific data to create a key
        # This ensures the key is consistent per system but not easily guessable
        system_data = (
            os.path.expanduser("~") +  # User home directory
            os.environ.get("COMPUTERNAME", "") +  # Windows computer name
            os.environ.get("USERNAME", "")  # Username
        ).encode('utf-8')

        # Create a 32-byte key using SHA-256
        key = hashlib.sha256(system_data).digest()
        return key

    def _simple_encrypt(self, plaintext):
        """Simple XOR-based encryption (not cryptographically secure but sufficient for this use case).

        For production, consider using cryptography.fernet or similar.

        Args:
            plaintext (str): Text to encrypt

        Returns:
            str: Base64-encoded encrypted text
        """
        if not plaintext:
            return ""

        key = self._encryption_key
        plaintext_bytes = plaintext.encode('utf-8')

        # XOR encryption with key cycling
        encrypted = bytearray()
        for i, byte in enumerate(plaintext_bytes):
            encrypted.append(byte ^ key[i % len(key)])

        # Return base64-encoded result
        return base64.b64encode(bytes(encrypted)).decode('utf-8')

    def _simple_decrypt(self, ciphertext):
        """Simple XOR-based decryption.

        Args:
            ciphertext (str): Base64-encoded encrypted text

        Returns:
            str: Decrypted text
        """
        if not ciphertext:
            return ""

        try:
            encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
            key = self._encryption_key

            # XOR decryption (same as encryption for XOR)
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % len(key)])

            return bytes(decrypted).decode('utf-8')
        except Exception:
            return ""

    def save_credentials(self, team_id, credential_id, credential_secret):
        """Save encrypted credentials to settings.

        Args:
            team_id (str): Team ID
            credential_id (str): Credential ID
            credential_secret (str): Credential Secret (will be encrypted)
        """
        self.settings.setValue("team_id", team_id)
        self.settings.setValue("credential_id", credential_id)
        self.settings.setValue("credential_secret_encrypted", self._simple_encrypt(credential_secret))
        self.settings.sync()

    def get_credentials(self):
        """Retrieve and decrypt credentials from settings.

        Returns:
            tuple: (team_id, credential_id, credential_secret) or (None, None, None) if not found
        """
        team_id = self.settings.value("team_id")
        credential_id = self.settings.value("credential_id")
        encrypted_secret = self.settings.value("credential_secret_encrypted")

        if not team_id or not credential_id or not encrypted_secret:
            return None, None, None

        credential_secret = self._simple_decrypt(encrypted_secret)
        return team_id, credential_id, credential_secret

    def has_credentials(self):
        """Check if credentials are stored.

        Returns:
            bool: True if credentials exist, False otherwise
        """
        team_id, credential_id, credential_secret = self.get_credentials()
        return team_id is not None and credential_id is not None and credential_secret is not None

    def clear_credentials(self):
        """Clear stored credentials."""
        self.settings.remove("team_id")
        self.settings.remove("credential_id")
        self.settings.remove("credential_secret_encrypted")
        self.settings.sync()

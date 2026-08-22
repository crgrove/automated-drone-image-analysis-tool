"""
Comprehensive tests for CalTopoCredentialHelper.

Tests credential encryption, storage, and retrieval.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QSettings
from core.services.export.CalTopoCredentialHelper import CalTopoCredentialHelper


@pytest.fixture
def credential_helper(isolated_qsettings):
    """A credential helper backed by throwaway settings.

    These tests call save_credentials(); against the default backing store
    that overwrites the developer's real CalTopo API credentials.
    """
    return CalTopoCredentialHelper(settings=isolated_qsettings)


@pytest.fixture
def sample_credentials():
    """Sample credentials for testing."""
    return {
        'team_id': 'ABC123',
        'credential_id': 'cred_id_123',
        'credential_secret': 'test_secret_key_12345678901234567890'
    }


def test_credential_helper_initialization(credential_helper):
    """Test CalTopoCredentialHelper initialization."""
    assert credential_helper is not None
    assert credential_helper.settings is not None
    assert credential_helper._encryption_key is not None
    assert len(credential_helper._encryption_key) == 32  # SHA-256 produces 32 bytes


def test_get_encryption_key(credential_helper):
    """Test encryption key generation."""
    key1 = credential_helper._get_encryption_key()
    key2 = credential_helper._get_encryption_key()

    # Same system should produce same key
    assert key1 == key2
    assert len(key1) == 32
    assert isinstance(key1, bytes)


def test_simple_encrypt_decrypt(credential_helper):
    """Test encryption and decryption round-trip."""
    plaintext = "test_secret_12345"

    encrypted = credential_helper._simple_encrypt(plaintext)
    assert encrypted != plaintext
    assert encrypted is not None
    assert len(encrypted) > 0

    decrypted = credential_helper._simple_decrypt(encrypted)
    assert decrypted == plaintext


def test_simple_encrypt_decrypt_empty_string(credential_helper):
    """Test encryption/decryption with empty string."""
    plaintext = ""

    encrypted = credential_helper._simple_encrypt(plaintext)
    assert encrypted == ""

    decrypted = credential_helper._simple_decrypt(encrypted)
    assert decrypted == ""


def test_simple_encrypt_decrypt_unicode(credential_helper):
    """Test encryption/decryption with unicode characters."""
    plaintext = "test_秘密_🔐_123"

    encrypted = credential_helper._simple_encrypt(plaintext)
    decrypted = credential_helper._simple_decrypt(encrypted)

    assert decrypted == plaintext


def test_simple_decrypt_invalid_base64(credential_helper):
    """Test decryption with invalid base64."""
    invalid_ciphertext = "not_valid_base64!!!"

    decrypted = credential_helper._simple_decrypt(invalid_ciphertext)
    assert decrypted == ""


def test_save_credentials(credential_helper, sample_credentials):
    """Test saving credentials."""
    credential_helper.save_credentials(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    # Verify credentials were saved
    team_id = credential_helper.settings.value("team_id")
    credential_id = credential_helper.settings.value("credential_id")
    encrypted_secret = credential_helper.settings.value("credential_secret_encrypted")

    assert team_id == sample_credentials['team_id']
    assert credential_id == sample_credentials['credential_id']
    assert encrypted_secret is not None
    assert encrypted_secret != sample_credentials['credential_secret']  # Should be encrypted


def test_get_credentials(credential_helper, sample_credentials):
    """Test retrieving credentials."""
    # Save credentials first
    credential_helper.save_credentials(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    # Retrieve credentials
    team_id, credential_id, credential_secret = credential_helper.get_credentials()

    assert team_id == sample_credentials['team_id']
    assert credential_id == sample_credentials['credential_id']
    assert credential_secret == sample_credentials['credential_secret']


def test_get_credentials_not_found(credential_helper):
    """Test retrieving credentials when none are stored."""
    # Clear any existing credentials
    credential_helper.clear_credentials()

    team_id, credential_id, credential_secret = credential_helper.get_credentials()

    assert team_id is None
    assert credential_id is None
    assert credential_secret is None


def test_has_credentials_true(credential_helper, sample_credentials):
    """Test has_credentials when credentials exist."""
    credential_helper.save_credentials(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert credential_helper.has_credentials() is True


def test_has_credentials_false(credential_helper):
    """Test has_credentials when no credentials exist."""
    credential_helper.clear_credentials()

    assert credential_helper.has_credentials() is False


def test_has_credentials_partial(credential_helper, sample_credentials):
    """Test has_credentials when only partial credentials exist."""
    credential_helper.clear_credentials()
    credential_helper.settings.setValue("team_id", sample_credentials['team_id'])
    # Missing credential_id and secret

    assert credential_helper.has_credentials() is False


def test_clear_credentials(credential_helper, sample_credentials):
    """Test clearing credentials."""
    # Save credentials first
    credential_helper.save_credentials(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    # Verify they exist
    assert credential_helper.has_credentials() is True

    # Clear them
    credential_helper.clear_credentials()

    # Verify they're gone
    assert credential_helper.has_credentials() is False
    team_id, credential_id, credential_secret = credential_helper.get_credentials()
    assert team_id is None
    assert credential_id is None
    assert credential_secret is None


def test_credential_storage_is_isolated_from_real_user_settings(credential_helper):
    """Saving fixture credentials must not touch the developer's own config.

    This suite calls save_credentials() with fixture values. Against the real
    QSettings backend (HKCU\\Software\\ADIAT\\CalTopoAPI on Windows) that
    silently overwrites the user's actual CalTopo API credentials, which then
    fail to authenticate until they are re-entered by hand. conftest redirects
    QSettings into a temp directory; this test guards that redirection.
    """
    assert credential_helper.settings.format() == QSettings.IniFormat
    location = credential_helper.settings.fileName().replace("\\", "/")
    assert "adiat-test-qsettings-" in location
    assert "HKEY_CURRENT_USER" not in location

    # And the real store is genuinely a different object/location.
    real_helper = CalTopoCredentialHelper()
    assert real_helper.settings.fileName() != credential_helper.settings.fileName()


def test_has_credentials_false_when_secret_is_not_base64(credential_helper):
    """A stored secret that can never sign a request counts as absent.

    Reproduces the field failure: a non-base64 value in the Secret field made
    has_credentials() report True, so the credential dialog never reappeared
    and the only way to correct it was editing QSettings by hand.
    """
    credential_helper.clear_credentials()
    credential_helper.save_credentials('ABC123', 'cred_id_123', '2GmR7xQp!wZ#4kLd')

    # The value round-trips through storage unchanged...
    _, _, stored_secret = credential_helper.get_credentials()
    assert stored_secret == '2GmR7xQp!wZ#4kLd'

    # ...but it is not usable, so the app must prompt again.
    assert credential_helper.has_credentials() is False


def test_has_credentials_true_for_valid_base64_secret(credential_helper):
    """A real base64 secret is still reported as present (no regression)."""
    import base64

    credential_helper.clear_credentials()
    secret = base64.b64encode(b'a-real-looking-hmac-key-0123456789').decode()
    credential_helper.save_credentials('ABC123', 'cred_id_123', secret)

    assert credential_helper.has_credentials() is True


def test_has_credentials_false_when_secret_decrypts_empty(credential_helper):
    """A corrupt stored blob decrypts to "" and must not count as present."""
    credential_helper.clear_credentials()
    credential_helper.settings.setValue("team_id", 'ABC123')
    credential_helper.settings.setValue("credential_id", 'cred_id_123')
    credential_helper.settings.setValue("credential_secret_encrypted", "not_valid_base64!!!")
    credential_helper.settings.sync()

    assert credential_helper._simple_decrypt("not_valid_base64!!!") == ""
    assert credential_helper.has_credentials() is False


def test_save_and_retrieve_multiple_times(credential_helper, sample_credentials):
    """Test saving and retrieving credentials multiple times."""
    # Save first set
    credential_helper.save_credentials(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    team_id1, cred_id1, cred_secret1 = credential_helper.get_credentials()

    # Save different credentials
    credential_helper.save_credentials(
        "XYZ789",
        "cred_id_456",
        "different_secret"
    )

    team_id2, cred_id2, cred_secret2 = credential_helper.get_credentials()

    assert team_id2 == "XYZ789"
    assert cred_id2 == "cred_id_456"
    assert cred_secret2 == "different_secret"
    assert team_id2 != team_id1

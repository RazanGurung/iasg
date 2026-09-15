"""Encrypted field types.

Keys come from the environment (FIELD_ENCRYPTION_KEY, CREDENTIAL_VAULT_KEY)
and must never be stored in the database. A key kept beside the ciphertext
protects nothing.

Two separate keys on purpose: protected identifiers and portal credentials
have different blast radii.
"""
# Implement with cryptography.fernet, or migrate to SQL Server Always
# Encrypted. Decide before the first write path ships — see docs/security.md.

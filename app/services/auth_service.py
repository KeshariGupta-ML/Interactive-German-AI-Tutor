import bcrypt


class AuthService:
    """Modern password security system using the native bcrypt library directly."""

    def hash_password(self, password: str) -> str:
        """Converts a plain text password into a secure hash string."""
        # 1. Convert the plain text string into standard utf-8 bytes
        password_bytes = password.encode('utf-8')

        # 2. Generate a random salt and compute the hash
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)

        # 3. Decode back to a standard string format to save cleanly into SQLite
        return hashed_bytes.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Compares an entered password with the saved database hash string."""
        try:
            # Convert both inputs to byte arrays for standard verification
            plain_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')

            # Returns a boolean True/False
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception:
            return False
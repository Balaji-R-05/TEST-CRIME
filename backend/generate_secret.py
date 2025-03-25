import secrets

# Generate a secure random secret key
secret_key = secrets.token_hex(32)
print(f"Your new JWT secret: {secret_key}")
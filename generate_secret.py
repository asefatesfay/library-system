#!/usr/bin/env python3
"""
Generate a secure JWT secret key for the library system.
Run this script to generate a new secret key for production use.
"""

import secrets

def generate_jwt_secret():
    """Generate a cryptographically secure JWT secret key"""
    # Generate a URL-safe 32-byte secret key
    secret_key = secrets.token_urlsafe(32)
    return secret_key

if __name__ == "__main__":
    secret = generate_jwt_secret()
    print("Generated JWT Secret Key:")
    print(f"JWT_SECRET_KEY={secret}")
    print("\nTo use this secret:")
    print("1. Copy the secret key above")
    print("2. Add it to your GitHub repository secrets as 'JWT_SECRET_KEY'")
    print("3. For local development, add it to a .env file")

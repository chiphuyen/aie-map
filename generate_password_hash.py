#!/usr/bin/env python3
"""
Utility script to generate a bcrypt password hash for the admin password.
Run this script to generate a hash for your chosen password.
"""
from passlib.context import CryptContext
import getpass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash():
    print("AIE Map - Admin Password Hash Generator")
    print("=" * 40)
    print("\nThis script will generate a secure bcrypt hash for your admin password.")
    print("The hash should be stored in your .env file as ADMIN_PASSWORD_HASH")
    print("\nIMPORTANT: Never share or commit your actual password or .env file!\n")
    
    while True:
        password = getpass.getpass("Enter admin password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters long. Please try again.")
            continue
            
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords don't match. Please try again.")
            continue
            
        break
    
    print("\nGenerating hash...")
    password_hash = pwd_context.hash(password)
    
    print("\n" + "=" * 40)
    print("Password hash generated successfully!")
    print("\nAdd this to your .env file:")
    print(f"\nADMIN_PASSWORD_HASH={password_hash}")
    print("\n" + "=" * 40)
    print("\nAlso add a secure session key:")
    print("SESSION_SECRET_KEY=<generate-a-random-string-here>")
    print("\nYou can generate a secure key with:")
    print("python -c \"import secrets; print(secrets.token_urlsafe(32))\"")

if __name__ == "__main__":
    generate_hash()
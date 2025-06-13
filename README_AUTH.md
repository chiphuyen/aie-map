# Authentication Setup for AIE Map

This document explains how to set up authentication for the AIE Map admin features.

## Quick Setup

1. **Generate a password hash**:
   ```bash
   python generate_password_hash.py
   ```
   Follow the prompts to create a secure admin password. The script will output a hash.

2. **Create a `.env` file** in the project root:
   ```bash
   cp .env.example .env
   ```

3. **Edit the `.env` file** and add:
   - The password hash from step 1
   - A secure session secret key (the script will show you how to generate one)

4. **Install new dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Security Features

- **Password hashing**: Uses bcrypt for secure password storage
- **Session management**: Secure session cookies with expiration
- **Rate limiting**: Prevents brute force attacks (5 attempts, 15-minute cooldown)
- **IP tracking**: Sessions are tied to IP addresses
- **HTTPS recommended**: Set `secure=True` in production for secure cookies

## Admin Features

Once authenticated, admins can:
- Edit any review (location, text, URLs, etc.)
- Delete reviews
- Access edit buttons on all review displays

## Environment Variables

Required in `.env`:
- `ADMIN_PASSWORD_HASH`: Bcrypt hash of the admin password
- `SESSION_SECRET_KEY`: Random string for session security

Optional:
- `SESSION_EXPIRE_HOURS`: Session duration (default: 24)
- `MAX_LOGIN_ATTEMPTS`: Before rate limiting (default: 5)
- `LOGIN_COOLDOWN_MINUTES`: Rate limit duration (default: 15)

## Important Security Notes

1. **Never commit `.env` file** - it's in .gitignore
2. **Use a strong password** - at least 8 characters
3. **Change the default session key** - use the generated one
4. **Use HTTPS in production** - for secure cookies
5. **Regularly rotate passwords** - especially if shared

## Accessing Admin Features

1. Navigate to `/admin/login`
2. Enter the admin password
3. Once logged in, edit buttons will appear on all reviews
4. Session persists for 24 hours (configurable)
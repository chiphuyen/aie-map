# Quick Authentication Setup

1. **Stop the current server** (Ctrl+C)

2. **Generate admin password hash**:
   ```bash
   python generate_password_hash.py
   ```
   Enter your desired admin password when prompted.

3. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add:
   - The password hash from step 2
   - A session secret key (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

4. **Restart the server**:
   ```bash
   python app.py
   ```

5. **Access admin features**:
   - Go to http://localhost:8000/admin/login
   - Enter your admin password
   - Edit buttons will appear on all reviews when logged in

## Troubleshooting

If you get "file not found" errors:
- Make sure you've restarted the server after changes
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify the templates directory exists and contains admin_login.html
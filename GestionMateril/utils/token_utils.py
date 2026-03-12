# myapp/utils/token_utils.py

import secrets
from datetime import timedelta
from django.utils import timezone

def generate_reset_token():
    return secrets.token_hex(3)  # exemple : 6 caractères hexadécimaux

def get_token_expiration(minutes=10):
    return timezone.now() + timedelta(minutes=minutes)
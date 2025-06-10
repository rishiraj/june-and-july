# backend/settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'api',
    'corsheaders',
]

MIDDLEWARE = [
    # ...
    'corsheaders.middleware.CorsMiddleware', # Add this
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Allow all origins for development. In production, restrict this to your domain.
CORS_ALLOW_ALL_ORIGINS = True

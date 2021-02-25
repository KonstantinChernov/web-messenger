"""
ASGI config for my_web_messenger project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# from channels.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_web_messenger.settings')

application = get_asgi_application()

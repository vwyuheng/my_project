# app/routes/__init__.py
from app.routes.main import main_bp
from app.routes.api import api_bp

__all__ = ['main_bp', 'api_bp']
# src/utils.py
import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('chatbot.log'),
            logging.StreamHandler()
        ]
    )

def validate_data_path(path: Path) -> bool:
    """Valide l'existence d'un chemin de données"""
    return path.exists() and path.stat().st_size > 0

def format_response(response: dict) -> str:
    """Formate une réponse pour l'affichage"""
    return f"{response['answer']}\n\n(Confiance: {response['confidence']:.2f})"
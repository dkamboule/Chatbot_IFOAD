# run.py
#!/usr/bin/env python3
"""
Script principal pour lancer le projet Chatbot IFOAD-UJKZ
"""

import argparse
import sys
from pathlib import Path

# Ajout du chemin src
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from data_collector import DataCollector
from data_preprocessor import DataPreprocessor
from utils import setup_logging
from config.settings import PROCESSED_DATA_DIR


def initialize_project():
    """Initialise la structure du projet si nécessaire"""
    from init_project import initialize_project_structure
    initialize_project_structure()

def collect_data():
    """Lance la collecte des données"""
    print("🚀 Lancement de la collecte des données...")
    collector = DataCollector()
    return collector.collect_from_website()

def preprocess_data():
    """Lance le prétraitement des données"""
    print("🔧 Prétraitement des données...")
    preprocessor = DataPreprocessor()
    return preprocessor.prepare_training_data()

def train_chatbot():
    """Lance l'entraînement du chatbot"""
    print("🧠 Entraînement du chatbot...")
    
    # Vérification que les données existent
    data_path = PROCESSED_DATA_DIR / "training_data.csv"
    if not data_path.exists():
        print("❌ Fichier de données non trouvé. Lancez d'abord : python run.py preprocess")
        return None
    
    try:
        from chatbot_engine import ChatbotEngine
        chatbot = ChatbotEngine()
        print("✅ Chatbot entraîné avec succès!")
        return chatbot
    except Exception as e:
        print(f"❌ Erreur lors de l'entraînement : {e}")
        print("💡 Vérifiez que le fichier training_data.csv contient des données valides")
        return None

def run_app():
    """Lance l'application Streamlit"""
    print("🌐 Lancement de l'application web...")
    import subprocess
    import os
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def main():
    """Fonction principale"""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Chatbot IFOAD-UJKZ")
    parser.add_argument(
        "command", 
        choices=["init", "collect", "preprocess", "train", "run", "all"],
        help="Commande à exécuter"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        initialize_project()
    elif args.command == "collect":
        initialize_project()  # S'assure que la structure existe
        collect_data()
    elif args.command == "preprocess":
        initialize_project()
        preprocess_data()
    elif args.command == "train":
        initialize_project()
        train_chatbot()
    elif args.command == "run":
        run_app()
    elif args.command == "all":
        initialize_project()
        collect_data()
        preprocess_data()
        train_chatbot()
        run_app()

if __name__ == "__main__":
    main()
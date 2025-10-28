# run.py
#!/usr/bin/env python3
"""
Script principal pour lancer le projet Chatbot IFOAD-UJKZ
"""

import argparse
import sys
import signal
import subprocess
from pathlib import Path

# Ajout du chemin src
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from config.settings import PROCESSED_DATA_DIR
from data_collector import DataCollector
from data_preprocessor import DataPreprocessor
from utils import setup_logging

# Variable globale pour le processus
streamlit_process = None

def signal_handler(sig, frame):
    """Gère l'interruption Ctrl+C"""
    print("\n🛑 Arrêt demandé...")
    if streamlit_process:
        print("Fermeture de l'application Streamlit...")
        streamlit_process.terminate()
        streamlit_process.wait(timeout=5)
    print("✅ Arrêt complet réussi")
    sys.exit(0)

def initialize_project():
    """Initialise la structure du projet si nécessaire"""
    try:
        from init_project import initialize_project_structure
        initialize_project_structure()
    except ImportError:
        print("⚠️ Script d'initialisation non trouvé, création des dossiers manuelle...")
        # Création manuelle des dossiers
        directories = ["src", "config", "data/raw", "data/processed", "tests"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        print("✅ Structure de dossiers créée")

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
    global streamlit_process
    
    print("🌐 Lancement de l'application web...")
    print("💡 L'application va s'ouvrir dans votre navigateur")
    print("💡 Pour quitter : Fermez l'onglet du navigateur ET appuyez sur Ctrl+C ici")
    
    try:
        # Configuration du gestionnaire de signal
        signal.signal(signal.SIGINT, signal_handler)
        
        # Lancement de Streamlit
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--browser.serverAddress", "localhost"
        ])
        
        # Attente du processus
        streamlit_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'application...")
        if streamlit_process:
            streamlit_process.terminate()
        print("✅ Application arrêtée")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        if streamlit_process:
            streamlit_process.terminate()

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
        initialize_project()
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
# run.py
#!/usr/bin/env python3
"""
Script principal avec menu interactif pour le projet Chatbot IFOAD-UJKZ
"""

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

# Import des utilitaires réseau
try:
    from utils import display_network_info
except ImportError:
    # Fallback si le fichier n'existe pas
    def display_network_info(port=8501):
        print(f"\n📍 Application accessible sur : http://localhost:{port}")
        print("🌐 Pour l'accès externe, configurez votre firewall et utilisez votre IP publique")
# Variable globale pour le processus
streamlit_process = None

def signal_handler(sig, frame):
    """Gère l'interruption Ctrl+C - Retour au menu au lieu de quitter"""
    print("\n\n🔄 Retour au menu principal... (Ctrl+C)")
    if streamlit_process:
        print("Fermeture de l'application Streamlit...")
        streamlit_process.terminate()
        streamlit_process.wait(timeout=5)
    # Ne pas appeler sys.exit(), on laisse le programme continuer

def display_menu():
    """Affiche le menu interactif"""
    print("\n" + "="*50)
    print("🤖 CHATBOT IFOAD-UJKZ - MENU PRINCIPAL")
    print("="*50)
    print("1️⃣  - Initialiser le projet (créer la structure)")
    print("2️⃣  - Collecter les données (web scraping)")
    print("3️⃣  - Prétraiter les données")
    print("4️⃣  - Entraîner le chatbot")
    print("5️⃣  - Lancer l'application web")
    print("6️⃣  - Tout exécuter (1-2-3-4-5)")
    print("0️⃣  - Quitter")
    print("💡 Ctrl+C - Retour au menu à tout moment")
    print("-"*50)

def get_user_choice():
    """Demande et valide le choix de l'utilisateur"""
    while True:
        try:
            choice = input("\n🎯 Votre choix (0-6) : ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6']:
                return int(choice)
            else:
                print("❌ Choix invalide. Veuillez entrer un nombre entre 0 et 6.")
        except KeyboardInterrupt:
            print("\n🔄 Retour au menu...")
            return -1  # Code spécial pour retour au menu
        except:
            print("❌ Entrée invalide. Veuillez entrer un nombre.")

def initialize_project():
    """Initialise la structure du projet si nécessaire"""
    print("\n📁 Initialisation de la structure du projet...")
    try:
        from init_project import initialize_project_structure
        initialize_project_structure()
        return True
    except ImportError:
        print("⚠️ Script d'initialisation non trouvé, création des dossiers manuelle...")
        # Création manuelle des dossiers
        directories = ["src", "config", "data/raw", "data/processed", "tests"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        print("✅ Structure de dossiers créée")
        return True
    except KeyboardInterrupt:
        print("\n🔄 Initialisation interrompue - Retour au menu")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        return False

def collect_data():
    """Lance la collecte des données"""
    print("\n🌐 Collecte des données...")
    try:
        collector = DataCollector()
        result = collector.collect_from_website()
        return result is not None
    except KeyboardInterrupt:
        print("\n🔄 Collecte interrompue - Retour au menu")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la collecte : {e}")
        return False

def preprocess_data():
    """Lance le prétraitement des données"""
    print("\n🔧 Prétraitement des données...")
    try:
        preprocessor = DataPreprocessor()
        result = preprocessor.prepare_training_data()
        return result is not None
    except KeyboardInterrupt:
        print("\n🔄 Prétraitement interrompue - Retour au menu")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du prétraitement : {e}")
        return False

def train_chatbot():
    """Lance l'entraînement du chatbot"""
    print("\n🧠 Entraînement du chatbot...")
    
    # Vérification que les données existent
    data_path = PROCESSED_DATA_DIR / "training_data.csv"
    if not data_path.exists():
        print("❌ Fichier de données non trouvé. Lancez d'abord l'option 3 (Prétraitement)")
        return False
    
    try:
        from chatbot_engine import ChatbotEngine
        chatbot = ChatbotEngine()
        print("✅ Chatbot entraîné avec succès!")
        return True
    except KeyboardInterrupt:
        print("\n🔄 Entraînement interrompue - Retour au menu")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'entraînement : {e}")
        print("💡 Vérifiez que le fichier training_data.csv contient des données valides")
        return False

def run_app():
    """Lance l'application Streamlit accessible depuis l'exterieur"""
    global streamlit_process
    
    print("\n🌐 Lancement de l'application web...")
    print("💡 L'application va s'ouvrir dans votre navigateur")
    
    try:
        # Configuration du gestionnaire de signal
        signal.signal(signal.SIGINT, signal_handler)
        
        # Lancement de Streamlit avec configuration pour accès externe
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",  # ✅ Permet l'accès depuis l'extérieur
            "--server.headless", "true",    # ✅ Mode headless pour serveur
            "--browser.serverAddress", "localhost"
        ])
        
        # Petite pause pour laisser Streamlit démarrer
        import time
        time.sleep(2)
        
        # Affichage des informations de connexion
        display_network_info(8501)
        
        print("\n⚠️  IMPORTANT : Configuration réseau requise")
        print("• Vérifiez que le port 8501 est ouvert dans votre firewall")
        print("• Si vous êtes derrière un routeur, configurez la redirection de port")
        print("• Testez depuis un autre appareil sur le même réseau")
        print("• Pour Internet, utilisez votre IP publique")
        
        # Attente du processus
        streamlit_process.wait()
        print("\n🔄 Retour au menu principal...")
        
    except KeyboardInterrupt:
        print("\n🔄 Retour au menu...")
        if streamlit_process:
            streamlit_process.terminate()
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        if streamlit_process:
            streamlit_process.terminate()
            streamlit_process = None


def execute_all():
    """Exécute toutes les étapes en séquence"""
    print("\n🚀 Exécution de toutes les étapes...")
    
    try:
        print("\n📁 Étape 1/5 : Initialisation...")
        if not initialize_project():
            return False
        
        print("\n🌐 Étape 2/5 : Collecte des données...")
        if not collect_data():
            return False
        
        print("\n🔧 Étape 3/5 : Prétraitement...")
        if not preprocess_data():
            return False
        
        print("\n🧠 Étape 4/5 : Entraînement...")
        if not train_chatbot():
            return False
        
        print("\n🌐 Étape 5/5 : Lancement de l'application...")
        run_app()
        return True
        
    except KeyboardInterrupt:
        print("\n🔄 Processus complet interrompu - Retour au menu")
        return False

def main():
    """Fonction principale avec menu interactif"""
    setup_logging()
    
    # Configuration du gestionnaire de signal global
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🤖 Bienvenue dans le Chatbot IFOAD-UJKZ !")
    print("💡 Appuyez sur Ctrl+C à tout moment pour revenir au menu")
    
    while True:
        try:
            display_menu()
            choice = get_user_choice()
            
            # Si Ctrl+C a été utilisé dans get_user_choice
            if choice == -1:
                continue
                
            if choice == 0:
                print("\n👋 Au revoir !")
                break
                
            elif choice == 1:
                initialize_project()
                
            elif choice == 2:
                initialize_project()  # S'assure que la structure existe
                collect_data()
                
            elif choice == 3:
                preprocess_data()
                
            elif choice == 4:
                train_chatbot()
                
            elif choice == 5:
                run_app()
                
            elif choice == 6:
                execute_all()
            
            # Pause avant de revenir au menu (sauf si l'utilisateur a quitté)
            if choice != 5 and choice != 6:  # Les options 5 et 6 gèrent leur propre flux
                try:
                    input("\n⏎ Appuyez sur Entrée pour revenir au menu...")
                except KeyboardInterrupt:
                    print("\n🔄 Retour au menu...")
                    continue
                    
        except KeyboardInterrupt:
            print("\n🔄 Retour au menu...")
            continue
        except Exception as e:
            print(f"\n❌ Erreur inattendue : {e}")
            try:
                input("\n⏎ Appuyez sur Entrée pour continuer...")
            except KeyboardInterrupt:
                continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"\n❌ Erreur critique : {e}")
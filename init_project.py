# init_project.py
"""
Script d'initialisation du projet Chatbot IFOAD-UJKZ
Crée la structure de dossiers nécessaire
"""
from pathlib import Path
import sys

def initialize_project_structure():
    """Initialise la structure du projet"""
    print("🚀 Initialisation de la structure du projet...")
    
    # Liste des dossiers à créer
    directories = [
        "src",
        "config", 
        "data/raw",
        "data/processed",
        "tests"
    ]
    
    # Création des dossiers
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier créé : {directory}")
    
    # Création des fichiers __init__.py
    init_files = ["src/__init__.py", "tests/__init__.py"]
    
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write('# Package initialization\n')
            print(f"✅ Fichier créé : {init_file}")
    
    # Vérification que config/settings.py existe
    config_file = Path("config/settings.py")
    if not config_file.exists():
        # Création d'un fichier settings.py basique si absent
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write('''# config/settings.py
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Création des dossiers s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)

# Paramètres du modèle
MODEL_CONFIG = {
    "similarity_threshold": 0.3,
    "max_questions": 1000,
    "language": "french"
}

# URLs pour le web scraping
DATA_SOURCES = {
   "formations_courte_durée": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=51",
    "filières": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=171",
    "Journaliste_numérique": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=56",
    "communication_numérique": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=58",
    "formations_en_ligne": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=17"
}
''')
        print(f"✅ Fichier de configuration créé : config/settings.py")
    
    print("\n🎉 Structure du projet initialisée avec succès!")
    print("\n📋 Prochaines étapes :")
    print("1. Installer les dépendances : pip install -r requirements.txt")
    print("2. Lancer le projet complet : python run.py all")
    print("3. Ou lancer étape par étape :")
    print("   - python run.py collect")
    print("   - python run.py preprocess")
    print("   - python run.py train")
    print("   - python run.py run")

if __name__ == "__main__":
    initialize_project_structure()
    
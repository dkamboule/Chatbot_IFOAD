# check_data.py
import pandas as pd
from pathlib import Path

def check_data():
    """Vérifie l'état des données"""
    data_path = Path("data/processed/training_data.csv")
    
    if not data_path.exists():
        print("❌ training_data.csv n'existe pas")
        return False
    
    try:
        df = pd.read_csv(data_path)
        print(f"✅ Données chargées : {len(df)} lignes")
        print(f"✅ Colonnes : {list(df.columns)}")
        print(f"✅ Aperçu :")
        print(df.head(3))
        return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

if __name__ == "__main__":
    check_data()
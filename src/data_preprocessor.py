# src/data_preprocessor.py
import json
import re
from typing import Dict, List, Tuple
import pandas as pd
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR

class DataPreprocessor:
    """Classe pour le prétraitement des données du chatbot"""
    
    def __init__(self):
        self.raw_data_path = RAW_DATA_DIR / "ifoad_data.json"
        self.processed_data_path = PROCESSED_DATA_DIR / "training_data.csv"
        # Assure que les dossiers existent
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_raw_data(self) -> Dict:
        """Charge les données brutes"""
        try:
            with open(self.raw_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Fichier {self.raw_data_path} non trouvé")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON : {e}")
            return {}
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Supprime la ponctuation
        text = re.sub(r'\s+', ' ', text)      # Supprime les espaces multiples
        return text
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte"""
    # Liste basique de mots vides français
        french_stop_words = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'en', 'un', 'une', 'à', 'au', 'aux', 'dans', 'pour', 'par', 'sur', 'avec', 'est', 'son', 'ses', 'ces', 'cet', 'cette', 'qui', 'que', 'quoi', 'quand', 'où', 'comment', 'pourquoi'}
        
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Supprime la ponctuation
        text = re.sub(r'\s+', ' ', text)      # Supprime les espaces multiples
        
        # Suppression simple des mots vides
        words = text.split()
        words = [word for word in words if word not in french_stop_words and len(word) > 2]
        text = ' '.join(words)
        
        return text

    
    def expand_questions(self, base_question: str) -> List[str]:
        """Génère des variations de questions"""
        variations = [base_question]
        
        # Nettoyage de la question de base
        clean_question = self.clean_text(base_question)
        if clean_question != base_question:
            variations.append(clean_question)
        
        # Patterns de reformulation
        reformulations = {
            "qu'est ce que": ["c'est quoi", "définition de", "explique moi", "présentation", "que signifie"],
            "comment": ["quelle est la procédure pour", "méthode pour", "démarche pour", "façon de", "processus pour"],
            "quels": ["quelles sont les", "liste des", "énumère les", "donne moi les", "quelles"],
            "quelles": ["quels sont les", "liste des", "énumère les", "donne moi les"],
            "quelle": ["quel est le", "quel", "donne moi la"],
            "pourquoi": ["raison pour", "cause de", "motivation pour"],
            "quand": ["à quelle date", "délai pour", "moment où"],
            "où": ["endroit où", "lieu pour", "adresse de"]
        }
        
        for pattern, alternatives in reformulations.items():
            if pattern in base_question:
                for alt in alternatives:
                    new_question = base_question.replace(pattern, alt)
                    variations.append(new_question)
                    # Ajoute aussi la version nettoyée
                    variations.append(self.clean_text(new_question))
        
        # Ajout de formulations avec ponctuation différente
        punctuation_variations = [
            base_question + "?",
            base_question + " !",
            "savoir " + base_question,
            "je veux savoir " + base_question,
            "j'aimerais connaître " + base_question
        ]
        variations.extend(punctuation_variations)
        
        # Suppression des doublons
        return list(set(variations))
    
    def prepare_training_data(self) -> pd.DataFrame:
        """Prépare les données pour l'entraînement"""
        print("🔧 Début du prétraitement des données...")
        
        raw_data = self.load_raw_data()
        if not raw_data:
            print("❌ Aucune donnée à prétraiter")
            return pd.DataFrame()
        
        training_pairs = []
        
        for category, qa_pairs in raw_data.items():
            print(f"  📁 Traitement de la catégorie : {category}")
            for question, answer in qa_pairs.items():
                # Nettoyage
                clean_question = self.clean_text(question)
                clean_answer = answer
                
                # Expansion des questions
                question_variations = self.expand_questions(clean_question)
                
                for variation in question_variations:
                    training_pairs.append({
                        'category': category,
                        'question': variation,
                        'answer': clean_answer,
                        'original_question': question
                    })
        
        if not training_pairs:
            print("❌ Aucune paire question-réponse générée")
            return pd.DataFrame()
        
        df = pd.DataFrame(training_pairs)
        
        # Suppression des doublons
        df = df.drop_duplicates(subset=['question'])
        
        # Sauvegarde
        try:
            df.to_csv(self.processed_data_path, index=False, encoding='utf-8')
            print(f"✅ Données préparées sauvegardées dans {self.processed_data_path}")
            print(f"📊 {len(df)} paires question-réponse générées")
            print(f"📁 Catégories : {df['category'].nunique()}")
            
            # Aperçu des données
            print("\n📋 Aperçu des données :")
            for category in df['category'].unique():
                count = len(df[df['category'] == category])
                print(f"   • {category}: {count} questions")
                
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
        
        return df
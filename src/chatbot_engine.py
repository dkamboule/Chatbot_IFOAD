# src/chatbot_engine.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Tuple, Dict, List
from config.settings import MODEL_CONFIG, PROCESSED_DATA_DIR

class ChatbotEngine:
    """Moteur principal du chatbot avec NLP"""
    
    def __init__(self):
        self.data_path = PROCESSED_DATA_DIR / "training_data.csv"
        self.vectorizer = TfidfVectorizer(
        stop_words=None,  # ✅ Correction
        lowercase=True,
        max_features=1000
        )
        self.qa_data = None
        self.question_vectors = None
        self._load_and_train()
    
    def _load_and_train(self):
        """Charge les données et entraîne le modèle"""
        print("Chargement et entraînement du chatbot...")
        
        # Chargement des données
        self.qa_data = pd.read_csv(self.data_path)
        
        # Entraînement du vectoriseur
        questions = self.qa_data['question'].tolist()
        self.question_vectors = self.vectorizer.fit_transform(questions)
        
        print(f"Chatbot entraîné sur {len(questions)} questions")
    
    def find_best_match(self, user_question: str) -> Tuple[str, float, str]:
        """Trouve la meilleure correspondance"""
        user_vector = self.vectorizer.transform([user_question])
        similarities = cosine_similarity(user_vector, self.question_vectors)
        best_match_idx = np.argmax(similarities)
        best_score = similarities[0, best_match_idx]
        
        best_question = self.qa_data.iloc[best_match_idx]['question']
        best_answer = self.qa_data.iloc[best_match_idx]['answer']
        category = self.qa_data.iloc[best_match_idx]['category']
        
        return best_answer, best_score, category
    
    def get_response(self, user_question: str) -> Dict:
        """Obtient une réponse structurée"""
        if not user_question.strip():
            return {
                "answer": "Veuillez poser une question sur IFOAD-UJKZ.",
                "confidence": 0.0,
                "category": "unknown",
                "suggestions": self._get_suggestions()
            }
        
        answer, confidence, category = self.find_best_match(
            user_question.lower()
        )
        
        if confidence < MODEL_CONFIG["similarity_threshold"]:
            return {
                "answer": self._get_fallback_response(),
                "confidence": confidence,
                "category": "unknown",
                "suggestions": self._get_suggestions()
            }
        
        return {
            "answer": answer,
            "confidence": confidence,
            "category": category,
            "suggestions": self._get_related_suggestions(category)
        }
    
    def _get_fallback_response(self) -> str:
        """Réponse par défaut quand la question n'est pas comprise"""
        return (
            "Je n'ai pas bien compris votre question. "
            "Voici ce que je peux vous expliquer :\n\n"
            "• Les formations proposées par IFOAD-UJKZ\n"
            "• Les conditions d'admission et d'inscription\n"
            "• Les frais de scolarité et modalités de paiement\n"
            "• Le déroulement des cours en ligne\n"
            "• Les contacts et informations pratiques\n\n"
            "visitez notre site web : https://www.ifoad-ujkz.net/formationenligne/course//index.php?categoryid=17\n\n"
            "Pouvez-vous reformuler votre question ?"
        )
    
    def _get_suggestions(self) -> List[str]:
        """Suggestions générales"""
        return [
            "Quelles formations proposez-vous ?",
            "Comment s'inscrire ?",
            "Quels sont les frais de scolarité ?",
            "Quels sont les prérequis pour l'admission ?",
            "Quelle est l'histoire d'IFOAD-UJKZ ?",
            "Comment vous contacter ?"
        ]
    
    def _get_related_suggestions(self, category: str) -> List[str]:
        """Suggestions par catégorie"""
        categories_suggestions = {
            "formations": [
                "Y a-t-il des formations en alternance ?",
                "Quelle est la durée des formations ?"
            ],
            "admission": [
                "Quels documents fournir ?",
                "Y a-t-il des sessions d'admission ?"
            ],
            "frais": [
                "Y a-t-il des bourses disponibles ?",
                "Puis-je payer en plusieurs fois ?"
            ],
            "histoire": [
                "Qui a fondé IFOAD-UJKZ ?",
                "Quels sont les moments clés de l'histoire d'IFOAD-UJKZ ?"
            ],
            "contact": [
                "Comment vous contacter ?",
                "Quels sont les horaires d'ouverture ?"
            ]

        }
        return categories_suggestions.get(category, self._get_suggestions())
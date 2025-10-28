# src/data_collector.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from typing import Dict, List
import time
from config.settings import RAW_DATA_DIR, DATA_SOURCES

class DataCollector:
    """Classe pour collecter les données depuis diverses sources"""
    
    def __init__(self):
        self.raw_data_path = RAW_DATA_DIR / "ifoad_data.json"
        # Assure que le dossier existe
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def collect_from_website(self) -> Dict[str, str]:
        """
        Simule la collecte de données depuis le site web IFOAD-UJKZ
        Dans un vrai projet, implémenterait le web scraping
        """
        print("Collecte des données depuis le site IFOAD-UJKZ...")
        
        # Données simulées structurées
        qa_data = {
            "informations_generales": {
                "qu'est ce que ifoad ujkz": "IFOAD-UJKZ est un Institut de Formation Ouverte et à Distance spécialisé dans les domaines de l'informatique, du management et du digital. Nous offrons des formations diplômantes adaptées aux besoins du marché.",
                "présentation ifoad ujkz": "Nous sommes un établissement d'enseignement supérieur public, spécialisé dans la formation à distance depuis 2010. Notre mission est de rendre l'éducation accessible à tous.",
                "qui êtes vous": "IFOAD-UJKZ est un institut de formation en ligne proposant des cursus dans le numérique, le management et le digital avec des diplômes reconnus par l'État."
            },
            "formations": {
                "quelles formations proposez vous": "Nous proposons :\n- Licence Informatique (3 ans)\n- Master en Data Science (2 ans)\n- Bachelor en Développement Web (3 ans)\n- Formation en Cybersécurité (1 an)\n- MBA Digital Marketing (1 an)",
                "liste des formations": "Voici notre catalogue complet :\n• Licence Informatique - 180 ECTS\n• Master Data Science - 120 ECTS\n• Bachelor Développement Web - 180 ECTS\n• Formation Cybersécurité - 60 ECTS\n• MBA Digital Marketing - 60 ECTS",
                "quelles sont les formations disponibles": "Nos formations couvrent les domaines du numérique : informatique, data science, développement web, cybersécurité et marketing digital.",
                "catalogue formations": "Notre catalogue inclut des formations de niveau Bac à Bac+5 dans les métiers du numérique et du digital."
            },
            "admission": {
                "comment s'inscrire": "L'inscription se fait en 4 étapes :\n1. Création de compte étudiant sur notre plateforme(https://www.campusfaso.bf/)\n2. Dépôt des documents requis (CV, diplômes et relevé de notes, lettre de motivation, Extrait de naissance, pièce identité etc)\n3. Entretien motivationnel avec un responsable pédagogique\n4. Paiement des frais d'inscription et signature du contrat",
                "procédure inscription": "La procédure d'inscription est entièrement dématérialisée. Vous recevrez un accusé de réception sous 48h.",
                "quels sont les prérequis pour l'admission": "Prérequis selon la formation :\n- Licence : Baccalauréat ou équivalent\n- Master : Licence (180 ECTS) ou équivalent\n- Expérience professionnelle appréciée pour les formations continues",
                "conditions d'admission": "L'admission est soumise à l'étude du dossier académique et à un entretien motivationnel. Certaines formations peuvent requérir des tests techniques.",
                "quels documents fournir": "Documents requis pour l'inscription :\n- CV à jour\n- Lettre de motivation\n- Copies certifiées des diplômes\n- Pièce d'identité recto-verso\n- Photo d'identité récente\n- Justificatif de domicile de moins de 3 mois"
            },
            "frais": {
                "quels sont les frais de scolarité": "Nos tarifs pour l'année universitaire :\n- Licence Informatique admis au test (zone UEMAO): (Etudiants: 16 500 FCFA/an, Particuliers: 51 500 FCFA/an)\n- Licence Informatique admis au test (hors UEMAO):252 000 FCFA/an\n- Licence Informatique admis sur titre (zone UEMAO): (Etudiants: 250 000 + 16 500 FCFA/an, particuliers: 250 000 + 51 500FCFA/an)\n- Master Data Science (zone UEMAO) : (Etudiants:700 000 + 16 500FCFA/an, particulier: 700 000 + 51 500/an)\n- Master Data Science (hors UEMAO) : (Etudiants:700 000 + 252 000FCFA/an)- Bachelor Développement Web : 250 000 FCFA/an\n- Formation Cybersécurité : 250 000 FCFA/an\n- MBA Digital Marketing : 250 000 FCFA/an",
                "tarifs formations": "Les frais de scolarité incluent l'accès à la plateforme pédagogique, le suivi tutoré et les ressources d'apprentissage. Des frais de dossier de 90€ s'ajoutent à la première inscription.",
                "modalités de paiement": "Plusieurs modalités de paiement sont possibles :\n- Paiement en intégralité (5% de réduction)\n- Paiement en 3 fois sans frais\n- Paiement en 10 fois (frais de gestion de 50€)\n- Financement CPF possible",
                "bourses aides financières": "Nous proposons :\n- Bourses sur critères sociaux\n- Aides au mérite\n- Financement CPF\n- Paiement en plusieurs fois\n- Conventions avec Pôle Emploi"
            },
            "pédagogie": {
                "comment se déroulent les cours": "Nos formations sont 100% en ligne avec :\n- Vidéos pédagogiques accessibles 24h/24\n- Classes virtuelles en direct avec les professeurs\n- Exercices pratiques et études de cas\n- Support individualisé des tuteurs\n- Projets collaboratifs en groupe",
                "modalités d'enseignement": "L'enseignement mixe asynchrone (vidéos, ressources) et synchrone (classes virtuelles). Un tuteur dédié suit votre progression.",
                "y a t il des examens en présentiel": "Oui, il y a quelques examens en présentiel, mais la plupart des examens peuvent être passés à distance sous surveillance virtuelle. Des centres d'examen sont disponibles dans les grandes villes pour ceux qui préfèrent le présentiel.",
                "suivi pédagogique": "Chaque étudiant bénéficie d'un tuteur référent qui assure un suivi personnalisé et répond à ses questions sous 24h."
            },
            "international": {
                "acceptez vous les étudiants internationaux": "Oui, nous accueillons des étudiants du monde entier. Tous les cours sont dispensés en français. Un test de niveau de français (TCF, DELF) peut être requis pour les non-francophones.",
                "étudiants étrangers": "Les étudiants internationaux doivent fournir en plus :\n- Passeport valide\n- Visa étudiant si nécessaire\n- Traduction certifiée des diplômes\n- Attestation de niveau de français",
                "cours en français": "Oui, tous nos cours sont en français. Un niveau Bac est recommandé pour suivre dans de bonnes conditions."
            },
            "contact": {
                "comment vous contacter": "Plusieurs moyens nous contacter :\n- Email : urbain.traore@ujkz.fr\n- Téléphone : (+226) 63 37 52 57 (lun-ven 9h-18h)\n- Chat en direct sur notre site\n- Réseaux sociaux :https://www.ujkz.bf/ifoad/\n- Formulaire de contact en ligne",
                "adresse ifoad ujkz": "IFOAD-UJKZ\n03 BP 7130 Ouaga 03\nKadiogo Burkina Faso",
                "horaires d'ouverture": "Notre service client est disponible :\n- Lundi au vendredi : 8h-18h\n- Samedi : 8h-12h\n- Urgences pédagogiques : 7j/7 via la plateforme"
            }
        }
        

        # Sauvegarde des données brutes
        try:
            with open(self.raw_data_path, 'w', encoding='utf-8') as f:
                json.dump(qa_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Données collectées et sauvegardées dans {self.raw_data_path}")
            print(f"📊 Statistiques : {sum(len(cat) for cat in qa_data.values())} questions-réponses collectées")
            return qa_data
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return {}
    
    def collect_from_api(self) -> Dict:
        """Collecte des données depuis une API (exemple)"""
        print("🌐 Tentative de collecte depuis API...")
        try:
            # Simulation d'appel API
            response = requests.get(DATA_SOURCES["formations_api"], timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print("⚠️ API non disponible, utilisation des données simulées")
                return {}
        except Exception as e:
            print(f"⚠️ Erreur API : {e}, utilisation des données simulées")
            return {}
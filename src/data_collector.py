# src/data_collector.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from typing import Dict, List
import time
import re
from config.settings import RAW_DATA_DIR, DATA_SOURCES

class DataCollector:
    """Classe pour collecter les données depuis diverses sources"""
    
    def __init__(self):
        self.raw_data_path = RAW_DATA_DIR / "ifoad_data.json"
        # Assure que le dossier existe
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_ifoad_website(self) -> Dict[str, str]:
        """
        Web scraping du site IFOAD-UJKZ
        """
        print("🌐 Début du web scraping du site IFOAD-UJKZ...")
        
        qa_data = {}
        
        try:
            # URL du site IFOAD-UJKZ (à adapter selon le vrai site)
            base_url = "https://www.ifoad-ujkz.net/formationenligne/course//index.php?categoryid=17"
            
            # Tentative de scraping des pages principales
            pages_to_scrape = {
                "formations": f"{base_url}formations/",
                "admission": f"{base_url}admission/", 
                "frais": f"{base_url}frais-scolarite/",
                "contact": f"{base_url}contact/"
            }
            
            for section, url in pages_to_scrape.items():
                try:
                    print(f"📄 Scraping de la page: {section}")
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extraction des informations selon la section
                        if section == "formations":
                            qa_data.update(self._extract_formations(soup))
                        elif section == "admission":
                            qa_data.update(self._extract_admission(soup))
                        elif section == "frais":
                            qa_data.update(self._extract_frais(soup))
                        elif section == "contact":
                            qa_data.update(self._extract_contact(soup))
                            
                        time.sleep(2)  # Respectful delay
                        
                except Exception as e:
                    print(f"⚠️ Erreur lors du scraping de {section}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Erreur générale du web scraping: {e}")
            
        return qa_data
    
    def _extract_formations(self, soup) -> Dict[str, str]:
        """Extrait les informations sur les formations"""
        formations_data = {}
        
        try:
            # Recherche des sections de formations
            formations_sections = soup.find_all(['div', 'section'], class_=re.compile(r'formation|course|program', re.I))
            
            if not formations_sections:
                # Fallback: recherche de listes
                formations_list = soup.find_all(['ul', 'ol'])
                for formation_list in formations_list:
                    items = formation_list.find_all('li')
                    for item in items:
                        text = item.get_text(strip=True)
                        if any(keyword in text.lower() for keyword in ['licence', 'master', 'bachelor', 'mba', 'formation']):
                            formations_data[f"formation {text}"] = f"Description de la formation: {text}"
            
            # Extraction des titres et descriptions
            titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for title in titles:
                text = title.get_text(strip=True)
                if any(keyword in text.lower() for keyword in ['licence', 'master', 'historique', 'formation', 'programme']):
                    # Trouve le paragraphe suivant
                    next_elem = title.find_next_sibling()
                    description = ""
                    while next_elem and next_elem.name in ['p', 'div']:
                        description += next_elem.get_text(strip=True) + " "
                        next_elem = next_elem.find_next_sibling()
                    
                    if description:
                        formations_data[f"qu'est ce que {text}"] = f"{text}: {description.strip()}"
                        
        except Exception as e:
            print(f"⚠️ Erreur extraction formations: {e}")
            
        return {"formations": formations_data} if formations_data else {}
    
    def _extract_admission(self, soup) -> Dict[str, str]:
        """Extrait les informations sur l'admission"""
        admission_data = {}
        
        try:
            # Recherche d'informations sur l'admission
            content = soup.get_text().lower()
            
            if 'admission' in content or 'inscription' in content:
                # Extraction des étapes d'admission
                steps = soup.find_all(['li', 'p', 'div'], string=re.compile(r'étape|step|procédure', re.I))
                for step in steps[:5]:  # Limite à 5 étapes
                    step_text = step.get_text(strip=True)
                    admission_data[f"étape admission {len(admission_data)+1}"] = step_text
                
                # Documents requis
                doc_elements = soup.find_all(string=re.compile(r'document|pièce|fournir', re.I))
                for doc_elem in doc_elements[:3]:
                    parent = doc_elem.parent
                    if parent:
                        admission_data["documents requis"] = parent.get_text(strip=True)
                        
        except Exception as e:
            print(f"⚠️ Erreur extraction admission: {e}")
            
        return {"admission": admission_data} if admission_data else {}
    
    def _extract_frais(self, soup) -> Dict[str, str]:
        """Extrait les informations sur les frais"""
        frais_data = {}
        
        try:
            # Recherche de prix et frais
            price_pattern = re.compile(r'\d+[\s\.,]?\d*\s*(FCFA|€|euro|francs?)', re.I)
            price_elements = soup.find_all(string=price_pattern)
            
            for elem in price_elements[:5]:
                text = elem.get_text(strip=True)
                frais_data[f"frais {len(frais_data)+1}"] = text
                
        except Exception as e:
            print(f"⚠️ Erreur extraction frais: {e}")
            
        return {"frais": frais_data} if frais_data else {}
    
    def _extract_contact(self, soup) -> Dict[str, str]:
        """Extrait les informations de contact"""
        contact_data = {}
        
        try:
            # Recherche d'emails
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
            if emails:
                contact_data["email contact"] = f"Email: {emails[0]}"
            
            # Recherche de numéros de téléphone
            phones = re.findall(r'[\+\(]?[1-9][\d\s\(\)\.-]{8,}\d', soup.get_text())
            if phones:
                contact_data["téléphone"] = f"Téléphone: {phones[0]}"
                
            # Recherche d'adresse
            address_keywords = ['adresse', 'address', 'siège', 'localisation']
            for keyword in address_keywords:
                elem = soup.find(string=re.compile(keyword, re.I))
                if elem and elem.parent:
                    contact_data["adresse"] = elem.parent.get_text(strip=True)
                    break
                    
        except Exception as e:
            print(f"⚠️ Erreur extraction contact: {e}")
            
        return {"contact": contact_data} if contact_data else {}
    
    def get_simulated_data(self) -> Dict[str, str]:
        """
        Données simulées enrichies en fallback si le web scraping échoue
        """
        print("🔄 Utilisation des données simulées enrichies...")
    
        qa_data = {
            "Historique": {
                "en quelle année ifoad a vu le jour ?": "L'Institut de Formations Ouverte à Distance a été créé dans le cadre du Plan stratégique 2013-2020 de l'Université Thomas Sankara (UTS), anciennement Université Ouaga II.\n Cette initiative visait à diversifier l'offre de formation de l'université en utilisant les technologies de l'information et de la communication pour offrir des formations à distance, tant diplômantes que certifiantes.\n Le projet a été initié par l'UTS et a bénéficié du soutien des expériences individuelles d'enseignants depuis 2010. ",
                "dans quel context l'ifoad a été créé": "Plan stratégique de l'Université Thomas Sankara (UTS):La création de l'IFOAD s'inscrit directement dans le Plan stratégique 2013-2020 de l'Université Thomas Sankara (UTS) (qui était alors l'Université Ouaga II).\n Axe stratégique : L'objectif était de mettre en œuvre l'axe 2 du plan, consacré à l'amélioration de la qualité des programmes d'enseignement et à la mise en place du système LMD (Licence-Master-Doctorat). ",
                "quels sont les objectifs principaux de l'ifoad ": "1.Développement et diversification de l'offre de formation de l'UTS : L'IFOAD a permis d'élargir les possibilités de formation à distance.\n 2. Accroissement de l'autofinancement de l'UTS : Le modèle de l'IFOAD devait contribuer à augmenter les ressources financières de l'université.\n 3. Augmentation de la capacité d'accueil : En proposant des formations en ligne, l'IFOAD a aidé à accueillir davantage de nouveaux bacheliers. ",
                "comment s'est deroulée la mise en oeuvre": "La mise en oeuvre a commencer par les Technologies de l'information et de la communication (TIC) : L'UTS a encouragé l'utilisation des TIC dans l'enseignement dès sa création, ce qui a conduit au développement de plateformes comme celles de l'Agence universitaire de la Francophonie (AUF). \n ensuite par Expériences d'enseignants : Les initiatives et le travail des enseignants ont été soutenus par l'université pour aboutir à la création de formations sur ces plateformes à partir de 2010. \n et la Formation continue : L'IFOAD fonctionne comme une interface entre le savoir académique et le savoir-faire professionnel, proposant des formations à distance continues. ",
                "qui a fondé l'ifoad": "L'IFOAD a été initié par l'Université Thomas Sankara (anciennement Université Ouaga II) dans le cadre de son plan stratégique, avec le soutien actif d'enseignants passionnés par les technologies éducatives depuis 2010.",
                "évolution de l'ifoad au fil des années": "Depuis 2010, l'IFOAD est passé de quelques formations pilotes à un catalogue complet de formations diplômantes et certifiantes, en constante évolution pour répondre aux besoins du marché.",
                "partenaires de l'ifoad": "L'IFOAD collabore avec l'Agence Universitaire de la Francophonie (AUF) et d'autres institutions pour enrichir son offre de formation et ses plateformes technologiques."
            },
            "informations_generales": {
                "qu'est ce que ifoad ujkz": "IFOAD-UJKZ est un Institut de Formation Ouverte et à Distance, rattaché à l'Université Joseph Ki-Zerbo, spécialisé dans les domaines de l'informatique, du management et du digital. Nous offrons des formations diplômantes adaptées aux besoins du marché.",
                "présentation ifoad ujkz": "Nous sommes un établissement d'enseignement supérieur public, spécialisé dans la formation à distance depuis 2010. Notre mission est de rendre l'éducation accessible à tous.",
                "qui êtes vous": "IFOAD-UJKZ est un institut de formation en ligne proposant des cursus dans le numérique, le management et le digital avec des diplômes reconnus par l'État.",
                "quelle est la vision de l'ifoad": "Notre vision est de devenir le leader de la formation à distance en Afrique francophone, en offrant des formations de qualité accessibles à tous.",
                "quelle est la mission de l'ifoad": "Notre mission est de démocratiser l'accès à l'enseignement supérieur grâce aux technologies numériques et de former des professionnels compétents pour le marché du travail.",
                "valeurs de l'ifoad": "Excellence académique, Innovation pédagogique, Accessibilité, Professionnalisme et Engagement envers la réussite étudiante.",
                "avantages de l'ifoad": "Flexibilité des horaires, Accessibilité depuis n'importe où, Formations adaptées au marché, Encadrement personnalisé et Diplômes reconnus."
            },
            "formations": {
                "quelles formations proposez vous": "Nous proposons :\n- Licence (Informatique, Journalisme numérique et Communication numérique) (3 ans)\n- Master en Data Science (2 ans)\n- Formations de courte durée",
                "liste des formations": "Voici notre catalogue complet :\n• Licence en Informatique appliquée, Communication numérique, Journalisme numérique\n• Master en Data Science\n• Formations courtes : \n - Développement Web\n - Cybersécurité\n - Marketing Digital\n - Programmation en C\n - Développement mobile\n - Administration Moodle\n - H5P\n - Compétences numériques\n - KoboToolbox\n - Power BI\n - Python pour les Sciences de Données",
                "quelles sont les formations disponibles": "Nos formations couvrent les domaines du numérique : informatique, data science, développement web, cybersécurité et marketing digital.",
                "catalogue formations": "Notre catalogue inclut des formations de niveau Bac à Bac+5 dans les métiers du numérique et du digital.",
                "durée des formations": "Licence : 3 ans (6 semestres)\nMaster : 2 ans (4 semestres)\nFormations courtes : 3 à 6 mois selon le programme",
                "diplômes délivrés": "Diplômes nationaux reconnus par l'État : Licence et Master. Attestations de formation pour les formations courtes.",
                "nouvelles formations prévues": "Nous prévoyons de lancer prochainement des formations en Intelligence Artificielle, Blockchain et Cloud Computing.",
                "formation en informatique appliquée": "La licence en informatique appliquée forme aux métiers du développement, de la gestion de bases de données et de l'administration des systèmes.",
                "formation en data science": "Le master en data science prépare aux métiers de data analyst, data scientist et spécialiste en intelligence artificielle.",
                "formations courtes certifiantes": "Nos formations courtes permettent d'acquérir des compétences spécifiques rapidement, avec une attestation de formation reconnue."
            },
            "admission": {
                "comment s'inscrire": "L'inscription se fait en 4 étapes :\n1. Création de compte étudiant sur notre plateforme(https://www.campusfaso.bf/)\n2. Dépôt des documents requis (CV, diplômes et relevé de notes, lettre de motivation, Extrait de naissance, pièce identité etc)\n3. Entretien motivationnel avec un responsable pédagogique\n4. Paiement des frais d'inscription et signature du contrat",
                "procédure inscription": "La procédure d'inscription est entièrement dématérialisée. Vous recevrez un accusé de réception par email.",
                "quels sont les prérequis pour l'admission": "Prérequis selon la formation :\n- Licence : Baccalauréat ou équivalent, réussir au test d'entrée ou s'inscrire sur titre\n- Master : Licence ou équivalent et être préselectionné\n- Expérience professionnelle appréciée pour les formations de courte durée",
                "conditions d'admission": "L'admission est soumise à l'étude du dossier académique et à un entretien motivationnel. Certaines formations peuvent requérir des tests techniques.",
                "quels documents fournir": "Documents requis pour l'inscription :\n- CV à jour\n- Lettre de motivation\n- Copies certifiées des diplômes à partir du Baccalauréat et les relevés de notes\n- Document d'identité\n- des Photos d'identité récente\n- Extrait de naissance et tout autre document spécifique selon la formation",
                "calendrier des admissions": "Les admissions sont ouvertes deux fois par an :\n- Session principale : Septembre\n- Session secondaire : Janvier",
                "test d'entrée": "Le test d'entrée évalue les compétences de base en culture générale, logique et selon la formation, en informatique.",
                "entretien motivationnel": "L'entretien permet d'évaluer votre motivation, votre projet professionnel et votre adéquation avec la formation choisie.",
                "admission sur titre": "L'admission sur titre est possible pour les candidats titulaires d'un diplôme équivalent, sans passer le test d'entrée.",
                "délai de traitement des dossiers": "Le traitement des dossiers d'admission prend généralement 2 à 3 semaines après le dépôt complet."
            },
            "frais": {
                "quels sont les frais de scolarité": "Nos tarifs pour l'année universitaire :\n- Licence Informatique admis au test (zone UEMAO): (Etudiants: 16 500 FCFA/an, Particuliers: 51 500 FCFA/an)\n- Licence Informatique admis au test (hors UEMAO):252 000 FCFA/an\n- Licence Informatique admis sur titre (zone UEMAO): (Etudiants: 250 000 + 16 500 FCFA/an, particuliers: 250 000 + 51 500FCFA/an)\n- Master Data Science (zone UEMAO) : (Etudiants:700 000 + 16 500FCFA/an, particulier: 700 000 + 51 500/an)\n- Master Data Science (hors UEMAO) : (Etudiants:700 000 + 252 000FCFA/an)- Bachelor Développement Web : 250 000 FCFA/an\n- Formation Cybersécurité : 250 000 FCFA/an\n- MBA Digital Marketing : 250 000 FCFA/an",
                "tarifs formations": "Les frais de scolarité incluent l'accès à la plateforme pédagogique, le suivi tutoré et les ressources d'apprentissage. Des frais de dossier de 90€ s'ajoutent à la première inscription.",
                "modalités de paiement": "Plusieurs modalités de paiement sont possibles :\n- Paiement en intégralité\n- Paiement en trois (3) tranches ",
                "bourses aides financières": "Nous ne proposons pas de bourses, mais les étudiants peuvent bénéficier de bourses nationales ou des institutions partenaires de l'État.\n La plupart des étudiants auto-financent leur formation.",
                "frais de dossier": "Les frais de dossier sont de 25 000 FCFA pour toutes les formations et ne sont pas remboursables.",
                "paiement en tranches": "Le paiement en trois tranches :\n- 1ère tranche : 40% à l'inscription\n- 2ème tranche : 30% au début du 2ème semestre\n- 3ème tranche : 30% au milieu du 2ème semestre",
                "remboursement des frais": "Les frais de scolarité ne sont pas remboursables sauf en cas de force majeure dûment justifiée.",
                "frais formations courtes": "Les formations courtes varient entre 50 000 FCFA et 200 000 FCFA selon la durée et la spécialité."
            },
            "pédagogie": {
                "comment se déroulent les cours": "Nos formations sont 100% en ligne avec :\n- Vidéos pédagogiques accessibles 24h/24\n- Classes virtuelles en direct avec les professeurs\n- Exercices pratiques et études de cas\n- Support individualisé des tuteurs\n- Projets collaboratifs en groupe",
                "modalités d'enseignement": "L'enseignement mixe asynchrone (vidéos, ressources) et synchrone (classes virtuelles). Un tuteur dédié suit votre progression.",
                "y a t il des examens en présentiel": "Oui, il y a quelques examens en présentiel, mais la plupart des examens peuvent être passés à distance sous surveillance virtuelle. Des centres d'examen sont disponibles dans les grandes villes pour ceux qui préfèrent le présentiel.",
                "suivi pédagogique": "Chaque étudiant bénéficie d'un tuteur référent qui assure un suivi personnalisé et répond à ses questions sous 24h.",
                "plateforme d'enseignement": "Nous utilisons la plateforme Moodle enrichie d'outils collaboratifs pour un apprentissage optimal.",
                "charge de travail": "La charge de travail est estimée à 15-20 heures par semaine pour les formations diplômantes.",
                "évaluation des apprentissages": "L'évaluation se fait par : contrôles continus, projets, examens finaux et participation aux activités pédagogiques.",
                "ressources pédagogiques": "Vidéos, PDF interactifs, quiz, forums de discussion, bibliothèque numérique et études de cas pratiques.",
                "travaux de groupe": "Les travaux de groupe sont encouragés pour développer l'esprit d'équipe et les compétences collaboratives.",
                "stage en entreprise": "Un stage en entreprise est obligatoire en fin de licence et de master pour une immersion professionnelle."
            },
            "international": {
                "acceptez vous les étudiants internationaux": "Oui, nous accueillons des étudiants du monde entier. Tous les cours sont dispensés en français. Un test de niveau de français (TCF, DELF) peut être requis pour les non-francophones.",
                "étudiants étrangers": "Les étudiants internationaux doivent fournir en plus :\n- Passeport valide\n- Visa étudiant si nécessaire\n- Traduction certifiée des diplômes\n- Attestation de niveau de français",
                "cours en français": "Oui, tous nos cours sont en français. Un niveau Bac est recommandé pour suivre dans de bonnes conditions.",
                "reconnaissance des diplômes à l'international": "Nos diplômes sont reconnus dans l'espace UEMOA et font l'objet de conventions de reconnaissance avec plusieurs pays.",
                "partenariats internationaux": "Nous développons des partenariats avec des universités européennes et africaines pour des échanges et doubles diplômes.",
                "équivalence des diplômes": "Service d'équivalence disponible pour les étudiants titulaires de diplômes étrangers."
            },
            "vie_etudiante": {
                "association des étudiants": "Les étudiants de l'IFOAD peuvent créer et animer des associations pour favoriser les échanges et l'entraide.",
                "événements étudiants": "Webinaires, hackathons, journées portes ouvertes virtuelles et rencontres professionnelles régulières.",
                "réseau des anciens": "Un réseau actif d'anciens étudiants pour le mentorat et les opportunités professionnelles.",
                "soutien psychologique": "Service d'écoute et de soutien psychologique disponible pour les étudiants en difficulté.",
                "sport et loisirs": "Bien qu'en ligne, nous encourageons les initiatives sportives et culturelles entre étudiants."
            },
            "débouchés_professionnels": {
                "débouchés après la licence informatique": "Développeur web/mobile, administrateur systèmes et réseaux, analyste programmeur, technicien informatique.",
                "débouchés après le master data science": "Data scientist, data analyst, consultant en intelligence artificielle, chef de projet data.",
                "débouchés formations courtes": "Spécialiste en cybersécurité, community manager, développeur fullstack, analyste Power BI.",
                "taux d'insertion professionnelle": "85% de nos diplômés trouvent un emploi dans les 6 mois suivant l'obtention de leur diplôme.",
                "entreprises partenaires": "Nous collaborons avec des entreprises locales et internationales pour les stages et l'insertion professionnelle.",
                "service carrière": "Accompagnement personnalisé pour la rédaction de CV, préparation aux entretiens et recherche d'emploi."
            },
            "contact": {
                "comment vous contacter": "Nous disposons de plusieurs moyens pour nous contacter :\n- Email : urbain.traore@ujkz.fr\n- Téléphone : (+226) 63 37 52 57 (lun-ven 9h-18h)\n- Chat en direct sur notre site\n- Réseaux sociaux :https://www.ujkz.bf/ifoad/\n- Formulaire de contact en ligne",
                "adresse ifoad ujkz": "IFOAD-UJKZ\n03 BP 7130 Ouaga 03\nKadiogo Burkina Faso",
                "horaires d'ouverture": "Notre service client est disponible :\n- Lundi au vendredi : 8h-18h\n- Samedi : 8h-12h\n- Urgences pédagogiques : 7j/7 via la plateforme",
                "responsable pédagogique": "Dr. Urbain Traoré - Responsable Pédagogique\nEmail : urbain.traore@ujkz.fr",
                "service administratif": "Pour les questions administratives : admin.ifoad@ujkz.fr",
                "service technique": "Support technique plateforme : support.ifoad@ujkz.fr",
                "réseaux sociaux": "Suivez-nous sur :\n- Facebook : IFOAD UJKZ\n- LinkedIn : IFOAD Université Joseph Ki-Zerbo\n- Twitter : @IFOAD_UJKZ"
            },
            "FAQ_generale": {
                "est-ce que les diplômes sont reconnus par l'état": "Oui, tous nos diplômes (Licence et Master) sont des diplômes nationaux reconnus par l'État burkinabè.",
                "peut-on travailler en même temps que suivre les cours": "Absolument ! La flexibilité de nos formations permet de concilier études et activité professionnelle.",
                "faut-il être fort en informatique pour suivre les formations": "Non, nos formations sont accessibles à tous. Nous proposons des modules d'initiation pour les débutants.",
                "quelle est la différence avec une formation en présentiel": "Même qualité d'enseignement mais avec une flexibilité horaire et géographique. Mêmes diplômes délivrés.",
                "comment est assurée la qualité de l'enseignement": "Par une équipe pédagogique qualifiée, des ressources de qualité et un système d'évaluation rigoureux.",
                "y a-t-il une limite d'âge pour s'inscrire": "Non, il n'y a pas de limite d'âge. Nous accueillons des étudiants de tous âges.",
                "peut-on suivre plusieurs formations en même temps": "Nous le déconseillons pour garantir la qualité de l'apprentissage, sauf pour des formations courtes complémentaires."
            }
        }
        
        return qa_data
    
    def collect_from_website(self) -> Dict[str, str]:
        """
        Collecte les données via web scraping avec fallback sur données simulées
        """
        print("🚀 Début de la collecte des données IFOAD-UJKZ...")
        
        # Tentative de web scraping
        scraped_data = self.scrape_ifoad_website()
        
        # Vérification si le scraping a récupéré des données
        if scraped_data and any(len(section) > 0 for section in scraped_data.values()):
            print("✅ Web scraping réussi!")
            qa_data = scraped_data
        else:
            print("⚠️ Web scraping échoué, utilisation des données simulées")
            qa_data = self.get_simulated_data()
        
        # Fusion des données (scraped + simulated pour compléter)
        final_data = self.merge_data(scraped_data, self.get_simulated_data())
        
        # Sauvegarde des données brutes
        try:
            with open(self.raw_data_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)
            
            total_questions = sum(len(cat) for cat in final_data.values())
            print(f"✅ Données sauvegardées dans {self.raw_data_path}")
            print(f"📊 Statistiques : {total_questions} questions-réponses collectées")
            print(f"📁 Catégories : {list(final_data.keys())}")
            
            return final_data
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return {}
    
    def merge_data(self, scraped_data: Dict, simulated_data: Dict) -> Dict:
        """Fusionne les données scrapées et simulées"""
        merged_data = {}
        
        # Pour chaque catégorie, on prend les données scrapées si elles existent, sinon les simulées
        all_categories = set(scraped_data.keys()) | set(simulated_data.keys())
        
        for category in all_categories:
            merged_data[category] = {}
            
            # Priorité aux données scrapées
            if category in scraped_data and scraped_data[category]:
                merged_data[category].update(scraped_data[category])
            
            # Complément avec données simulées
            if category in simulated_data:
                for key, value in simulated_data[category].items():
                    if key not in merged_data[category]:
                        merged_data[category][key] = value
        
        return merged_data
    
    def collect_from_api(self) -> Dict:
        """Collecte des données depuis une API (exemple)"""
        print("🌐 Tentative de collecte depuis API...")
        try:
            # Simulation d'appel API
            response = self.session.get(DATA_SOURCES["formations_api"], timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print("⚠️ API non disponible, utilisation des données simulées")
                return {}
        except Exception as e:
            print(f"⚠️ Erreur API : {e}, utilisation des données simulées")
            return {}
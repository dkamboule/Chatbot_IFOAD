# app.py
import streamlit as st
import sys
from pathlib import Path

# Ajout du chemin src
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from chatbot_engine import ChatbotEngine
from utils import setup_logging

class ChatbotApp:
    """Application Streamlit pour le chatbot"""
    
    def __init__(self):
        setup_logging()
        self.chatbot = ChatbotEngine()
        self.setup_page()
    
    def setup_page(self):
        """Configure la page Streamlit"""
        st.set_page_config(
            page_title="Chatbot IFOAD-UJKZ",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session(self):
        """Initialise l'état de la session"""
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
        if 'suggestions' not in st.session_state:
            st.session_state.suggestions = [
                "Quelles formations proposez-vous ?",
                "Comment s'inscrire ?",
                "Quels sont les frais de scolarité ?",
                "en quelle année ifoad a vu le jour ?",
                "Comment vous contacter ?"
            ]
    
    def display_header(self):
        """Affiche l'en-tête de l'application"""
        st.title("🤖 Chatbot d'Orientation - IFOAD-UJKZ")
        st.markdown("""
        **Votre assistant virtuel pour tout savoir sur nos formations à distance**
        
        📚 **Formations** • 🎓 **Admission** • 💰 **Frais** • 🌍 **International**
        """)
    
    def display_conversation(self):
        """Affiche l'historique de conversation"""
        st.markdown("### 💬 Conversation")
        
        for i, (question, response, is_user) in enumerate(st.session_state.conversation):
            if is_user:
                st.markdown(f"""
                <div style='text-align: right; margin: 10px; padding: 10px; 
                          background-color: #0078D4; color: white; border-radius: 10px;'>
                    <strong>Vous:</strong> {question}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='text-align: left; margin: 10px; padding: 10px; 
                          background-color: #F0F2F6; border-radius: 10px;'>
                    <strong>Assistant:</strong> {response['answer']}
                    <br><small>Catégorie: {response['category']} • 
                    Confiance: {response['confidence']:.2f}</small>
                </div>
                """, unsafe_allow_html=True)
    
    def display_suggestions(self):
        """Affiche les questions suggérées"""
        st.markdown("### 💡 Questions rapides")

        cols = st.columns(6)
        suggestions = [
            "Formations proposées",
            "Comment s'inscrire", 
            "Frais de scolarité",
            "Prérequis admission",
            "Nous contacter",
            "Année de création"
        ]
        
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"sugg_{i}"):
                    self.process_question(suggestion)
    
    def display_input(self):
        """Affiche la zone de saisie"""
        st.markdown("### 🎯 Posez votre question")
        
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Votre question:",
                placeholder="Ex: Quelles sont les conditions d'admission pour la licence ?",
                key="user_input",
                on_change=self._handle_enter_key
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Envoyer ↗️") and user_input:
                self.process_question(user_input)
                st.session_state.user_input = ""
            
            if st.button("Effacer 🗑️"):
                st.session_state.conversation = []
                st.rerun()
    
    def _handle_enter_key(self):
        """Gère l'appui sur la touche Entrée"""
        if st.session_state.user_input:
            self.process_question(st.session_state.user_input)
            st.session_state.user_input = ""
    def process_question(self, question: str):
        """Traite une question et met à jour la conversation"""
        response = self.chatbot.get_response(question)
        
        # Ajoute la question utilisateur
        st.session_state.conversation.append((question, None, True))
        # Ajoute la réponse du chatbot
        st.session_state.conversation.append(("", response, False))
        
        # Met à jour les suggestions
        st.session_state.suggestions = response['suggestions']
        
        st.rerun()
    
    def display_sidebar(self):
        """Affiche la barre latérale avec les informations"""
        with st.sidebar:
            st.header("ℹ️ À propos")
            st.markdown("""
            **IFOAD-UJKZ**
            
            Institut de Formation Ouverte et à Distance
            Université Joseph Ki-Zerbo, Burkina Faso
            spécialisé dans les métiers du numérique.
            
            📧 curbain.traore@ujkz.fr
            📞 (+226) 63 37 52 57
            🌐 https://www.ifoad-ujkz.net/formationenligne/course//index.php?categoryid=17
            
            ---
            """)
            
            st.markdown("### 📊 Statistiques")
            st.info(f"💬 {len(st.session_state.conversation)//2} échanges")
            
            if st.session_state.conversation:
                last_response = st.session_state.conversation[-1][2]
                if not last_response:  # Si c'est une réponse du bot
                    confidence = st.session_state.conversation[-1][1]['confidence']
                    st.metric("Confiance dernière réponse", f"{confidence:.2f}")
    
    def run(self):
        """Lance l'application"""
        self.initialize_session()
        self.display_header()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self.display_conversation()
            self.display_suggestions()
            self.display_input()
        
        with col2:
            self.display_sidebar()

def main():
    """Fonction principale"""
    app = ChatbotApp()
    app.run()

if __name__ == "__main__":
    main()
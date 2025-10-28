# src/network_utils.py
import socket
import requests
from typing import Optional
import time

def get_local_ip() -> str:
    """Retourne l'adresse IP locale"""
    try:
        # Crée une socket pour trouver l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_public_ip() -> Optional[str]:
    """Tente de récupérer l'IP publique"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return None

def check_port_open(host: str, port: int) -> bool:
    """Vérifie si un port est accessible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex((host, port))
            return result == 0
    except:
        return False

def setup_logging(port: int = 8501):
    """Affiche les informations de connexion réseau"""
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print("\n" + "="*60)
    print("🌍 INFORMATIONS DE CONNEXION RÉSEAU")
    print("="*60)
    print(f"📍 Accès local : http://localhost:{port}")
    print(f"🏠 Accès réseau local : http://{local_ip}:{port}")
    
    # Test d'accessibilité locale
    if check_port_open(local_ip, port):
        print("✅ Port accessible sur le réseau local")
    else:
        print("❌ Port peut-être bloqué par le firewall")
    
    if public_ip:
        print(f"🌐 Accès INTERNET : http://{public_ip}:{port}")
        print("💡 Partagez cette URL pour tester depuis l'extérieur")
        
        # Test d'accessibilité publique (basique)
        print("🔍 Vérification de l'accessibilité publique...")
        if check_port_open(public_ip, port):
            print("✅ Application accessible depuis Internet !")
        else:
            print("❌ Configuration réseau requise pour l'accès Internet")
            print("   • Ouvrez le port 8501 dans votre firewall")
            print("   • Configurez la redirection de port sur votre routeur")
    else:
        print("🌐 Accès INTERNET : Impossible de détecter l'IP publique")
        print("💡 Vérifiez votre connexion Internet")
    
    print("="*60)
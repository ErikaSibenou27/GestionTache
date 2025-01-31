import pyrebase

# Configuration Firebase
firebase_config = {
    "apiKey": "AIzaSyC7R5e5Mw42WpD4CJDK7q_6do8JGFGW93U",
    "authDomain": "gestiontache-e7473.firebaseapp.com",
    "databaseURL": "https://gestiontache-e7473-default-rtdb.firebaseio.com/",
    "projectId": "gestiontache-e7473",
    "storageBucket": "gestiontache-e7473.firebasestorage.app",
    "messagingSenderId": "371996796633",
    "appId": "1:371996796633:web:35d53068e9a29595dc80c8",
    "measurementId": "G-NSGSB752E8"
}

# Connexion à Firebase
try:
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    print("Connexion réussie à Firebase")
except Exception as e:
    print(f"Erreur de connexion à Firebase : {e}")

from flask import Flask, render_template, request, redirect, url_for, flash,session
import datetime
import bcrypt 
from firebase_conn import db  # Importez l'objet `db` depuis votre fichier firebase_conn.py
import os



# Initialiser Flask
app = Flask(__name__)
app.secret_key = "b'q\x86\xc9\x19\xed\x81\xd3\x8dF\xd3*\xef\xbeC\x89\xee'" 



# Routes Flask

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connexion')
def conn():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')  
        email = request.form.get('email')
        password = request.form.get('password')

        # Charger les utilisateurs existants depuis Firebase
        users_ref = db.child("users").get().val()

        # Vérification du type des données retournées et traitement
        if isinstance(users_ref, dict):
            users_ref = {user_id: user for user_id, user in users_ref.items() if user is not None}
        elif isinstance(users_ref, list):
            users_ref = {i + 1: user for i, user in enumerate(users_ref) if user is not None}
        else:
            users_ref = {}  # Si users_ref est vide ou d'un type inconnu, on l'initialise en dictionnaire vide

        # Trouver le prochain ID à utiliser (par exemple, prendre l'ID max + 1)
        if users_ref:
            next_id = max(int(user_id) for user_id in users_ref.keys()) + 1
        else:
            next_id = 1  # Si la base est vide, on commence avec l'ID 1

        # Vérification si l'email existe déjà
        if any(isinstance(u, dict) and 'email' in u and u['email'] == email for u in users_ref.values()):
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('login'))
        # Hachage du mot de passe avant de le stocker
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Créer un nouvel utilisateur avec la structure requise
        new_user = {
            'id': next_id,  # Utilisation de l'ID généré
            'full_name': full_name,
            'email': email,
            'password': hashed_password,
            'status': 'offline',  # Statut par défaut
            'type': 'user',
            'date_creation': datetime.datetime.now().strftime("%Y-%m-%d"),  # Date de création
        }

        # Ajouter l'utilisateur dans Firebase avec l'ID généré
        db.child("users").child(str(next_id)).set(new_user)

        flash('Inscription réussie !', 'success')
        return redirect(url_for('login'))  # Rediriger vers la page de connexion après l'inscription

    return render_template('register.html')  # Rendre le formulaire d'inscription en cas de méthode GET

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Recherche des utilisateurs depuis Firebase
        users_ref = db.child("users").get().val()

        # Enlever les entrées 'None' ou autres données inutiles
        if users_ref:
            users_ref = [user for user in users_ref if user is not None]
        else:
            users_ref = []  # Si users_ref est vide, initialiser en liste vide

        # Si users_ref est une liste, on transforme cette liste en dictionnaire pour faciliter l'accès
        if isinstance(users_ref, list):
            users_ref = {str(i + 1): user for i, user in enumerate(users_ref)}

        # Recherche de l'utilisateur correspondant à l'email
        user = next((u for u in users_ref.values() if u['email'] == email), None)

        # Vérification du mot de passe avec bcrypt
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['logged_in'] = True
            session['user_type'] = user['type']  # Stocke le type d'utilisateur
            flash('Connexion réussie !', 'success')

            # Mettre à jour le statut de l'utilisateur en ligne
            user_ref = db.child("users").order_by_child("email").equal_to(email).get()
            if user_ref:
                # Récupérer l'ID de l'utilisateur
                user_id = list(user_ref.val().keys())[0]
                db.child("users").child(user_id).update({"status": "online"})

            # Redirige selon le type d'utilisateur
            if user['type'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user'))
        else:
            flash('Email ou mot de passe invalide.', 'danger')

        return redirect(url_for('index'))  # Retour à la page de connexion en cas d'échec

    return render_template('login.html')  # Gérer la méthode GET pour afficher le formulaire


# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email']
#         try:
#             # Essayer d'envoyer un email de réinitialisation
#             firebase.auth().send_password_reset_email(email)
#             flash("Un lien de réinitialisation a été envoyé à votre email.", "success")
#             return redirect(url_for('login'))
#         except firebase.FirebaseAuthenticationError:
#             # Gérer une erreur d'authentification si l'email est incorrect
#             flash("Cet email est invalide ou non enregistré.", "danger")
#         except Exception as e:
#             # Gérer toute autre exception générale
#             flash(f"Une erreur s'est produite: {str(e)}", "danger")
    
#     return render_template('forgot_password.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')



@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/user')
def user():
    return redirect(url_for('admin'))



@app.route('/gere_user')
def gere_user():
    return render_template('gere_user.html')


@app.route('/gere_projet')
def gere_projet():
    projets_ref = db.child("projets").get().val()

    # Vérifier si projets_ref est une liste et la convertir en dict
    if isinstance(projets_ref, list):
        projets_dict = {
            str(i): {k: v if v is not None else "Donnée manquante" for k, v in projet.items()}
            for i, projet in enumerate(projets_ref, start=1)
            if projet is not None
        }
    elif isinstance(projets_ref, dict):
        projets_dict = {
            key: {k: v if v is not None else "Donnée manquante" for k, v in projet.items()}
            for key, projet in projets_ref.items()
            if projet is not None
        }
    else:
        projets_dict = {}

    return render_template('gere_projet.html', projets=projets_dict)


@app.route('/save_projet', methods=['POST'])
def save_projet():
    name = request.form.get('name')  # Récupérer le nom du projet
    description = request.form.get('description')  # Récupérer la description
    date = request.form.get('date')  # Récupérer la date

    # Vérification que tous les champs sont remplis
    if not name or not description or not date:
        flash('Tous les champs sont obligatoires.', 'danger')
        return redirect(url_for('gere_projet')) 

    # Charger les projets existants depuis Firebase
    projets_ref = db.child("projets").get().val()

    # Vérification du type des données retournées et traitement
    if isinstance(projets_ref, dict):
        # Filtrer les clés pour ne conserver que celles qui peuvent être converties en int
        valid_keys = [int(key) for key in projets_ref.keys() if key.isdigit()]
        next_id = max(valid_keys, default=0) + 1  # Trouver le prochain ID
    else:
        projets_ref = {}  # Si projets_ref est vide ou d'un type inconnu, on l'initialise en dictionnaire vide
        next_id = 1  # Commencer avec l'ID 1

    # Création du projet avec les données du formulaire
    new_projet = {
        'id': next_id,  # Utilisation de l'ID généré
        'name': name,
        'description': description,
        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Date et heure de création
    }

    # Ajouter le projet dans Firebase avec l'ID généré
    db.child("projets").child(str(next_id)).set(new_projet)

    flash('Projet enregistré avec succès !', 'success')
    return redirect(url_for('gere_projet'))

@app.route('/edit_projet/<int:projet_id>', methods=['GET', 'POST'])
def modif_projet(projet_id):
    # Retrieve the project data from the database using the projet_id
    projet = db.child("projets").child(projet_id).get().val()

    if projet:
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            date = request.form.get('date')

            # Update the project data in the database
            db.child("projets").child(projet_id).update({
                'name': name,
                'description': description,
                'date_de_creation': date
            })

            flash('Projet modifié avec succès!', 'success')
            return redirect(url_for('gere_projet'))  # Redirect to a project list or another page
        else:
            # Show the project data in the form
            return render_template('edit_projet.html', projet=projet)
    else:
        flash("Le projet n'a pas été trouvé.", 'danger')
        return redirect(url_for('gere_projet'))

@app.route('/delete_projet/<string:projet_id>', methods=['GET'])
def delete_projet(projet_id):
    db.child("projets").child(projet_id).remove()
    flash('Projet supprimé avec succès !', 'success')
    return redirect(url_for('gere_projet'))

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/gere_tache')
def gere_tache():
    # Récupérer les projets et les tâches depuis Firebase
    projets = db.child("projets").get().val() or {}
    taches = db.child("tasks").get().val() or {}

    # Nettoyage des projets (suppression des None et remplacement des valeurs manquantes)
    if isinstance(projets, dict):
        projets = {
            key: {k: v if v is not None else "Donnée manquante" for k, v in projet.items()}
            for key, projet in projets.items() if projet is not None
        }
    elif isinstance(projets, list):
        projets = [projet for projet in projets if projet is not None]
    else:
        projets = []  # Si aucun projet n'existe

    # Nettoyage des tâches (même logique que pour les projets)
    if isinstance(taches, dict):
        taches = {
            key: {k: v if v is not None else "Donnée manquante" for k, v in tache.items()}
            for key, tache in taches.items() if tache is not None
        }
    elif isinstance(taches, list):
        taches = [tache for tache in taches if tache is not None]
    else:
        taches = []  # Si aucune tâche n'existe

    # Passer les données au template
    return render_template('gere_tache.html', projets=projets, taches=taches)


@app.route('/save_tache', methods=['POST'])
def save_tache():
    projet_id = request.form.get('projet')  # ID du projet associé
    name = request.form.get('name')  # Nom de la tâche
    description = request.form.get('description')  # Description
    date = request.form.get('date')  # Date de création
    statut = request.form.get('statut')  # Statut de la tâche

    # Vérification que tous les champs sont remplis
    if not projet_id or not name or not description or not date or not statut:
        flash('Tous les champs sont obligatoires.', 'danger')
        return redirect(url_for('gere_tache')) 

    # Charger les tâches existantes depuis Firebase
    taches_ref = db.child("tasks").get().val()

    # Vérification du type des données retournées et traitement
    if isinstance(taches_ref, dict):
        valid_keys = [int(key) for key in taches_ref.keys() if key.isdigit()]
        next_id = max(valid_keys, default=0) + 1  # Trouver le prochain ID
    else:
        taches_ref = {}  # Initialiser si vide
        next_id = 1  # Commencer avec l'ID 1

    # Création de la tâche avec les données du formulaire
    new_tache = {
        'id': next_id,  # Utilisation de l'ID généré
        'projet_id': projet_id,  # Associer à un projet
        'name': name,
        'description': description,
        'date_de_creation': date,
        'statut': statut
    }

    # Ajouter la tâche dans Firebase avec l'ID généré
    db.child("tasks").child(str(next_id)).set(new_tache)

    flash('Tâche enregistrée avec succès !', 'success')
    return redirect(url_for('gere_tache'))

@app.route('/edit_tache/<tache_id>', methods=['GET', 'POST'])
def edit_tache(tache_id):
    # Récupérer les projets disponibles
    projets = db.child("projets").get().val() or {}

    # Vérifier si 'projets' est une liste et la convertir en dictionnaire (si nécessaire)
    if isinstance(projets, list):
        projets = {str(i): projet for i, projet in enumerate(projets) if projet}

    if request.method == 'POST':
        titre = request.form.get('titre')
        description = request.form.get('description')
        projet_id = request.form.get('projet_id')
        statut = request.form.get('statut')
        date = request.form.get('date')

        # Mettre à jour la tâche dans Firebase
        db.child("tasks").child(tache_id).update({
            "titre": titre,
            "description": description,
            "projet_id": projet_id,
            "statut": statut,
            "date": date
        })

        return redirect(url_for('gere_tache'))

    # Récupérer les données actuelles de la tâche
    tache = db.child("tasks").child(tache_id).get().val()

    return render_template('edit_tache.html', tache=tache, tache_id=tache_id, projets=projets)

@app.route('/delete_tache/<tache_id>', methods=['POST'])
def delete_tache(tache_id):
    # Supprimer la tâche de Firebase
    db.child("tasks").child(tache_id).remove()
    return redirect(url_for('gere_tache'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/back_admin')
def back_admin():
    # Vous pouvez ajouter des données à afficher dans admin.html si nécessaire
    return render_template('admin.html')

if __name__ == '__main__':
   port = int(os.environ.get("PORT", 5000))  
   app.run(host="0.0.0.0", port=port, debug=True)

from flask import Blueprint, request, jsonify
from app.services.auth_service import inscrire_utilisateur, connecter_utilisateur, rafraichir_token, deconnecter_utilisateur, changer_mot_de_passe
from app.utils.validation import SchemaInscriptionUtilisateur, SchemaConnexionUtilisateur, valider_donnees_requete
from app.utils.security import token_requis
from app.utils.error_handler import ErreurRequeteInvalide

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint pour l'inscription d'un nouvel utilisateur"""
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaInscriptionUtilisateur, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Inscrire l'utilisateur
    resultat = inscrire_utilisateur(donnees_validees)
    
    return jsonify({
        'statut': 'succes',
        'message': 'Utilisateur inscrit avec succès',
        'utilisateur': resultat
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint pour la connexion d'un utilisateur"""
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaConnexionUtilisateur, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Connecter l'utilisateur
    resultat = connecter_utilisateur(donnees_validees)
    
    return jsonify({
        'statut': 'succes',
        'message': 'Connexion réussie',
        'utilisateur': resultat['utilisateur'],
        'tokens': resultat['tokens']
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Endpoint pour rafraîchir le token d'accès"""
    try:
        resultat = rafraichir_token()
        return jsonify({
            'statut': 'succes',
            'message': 'Token rafraîchi avec succès',
            'token_acces': resultat['token_acces']
        }), 200
    except Exception as e:
        return jsonify({
            'statut': 'erreur',
            'message': str(e)
        }), 401

@auth_bp.route('/logout', methods=['POST'])
@token_requis
def logout(utilisateur_actuel):
    """Endpoint pour la déconnexion d'un utilisateur"""
    resultat = deconnecter_utilisateur()
    return jsonify({
        'statut': 'succes',
        'message': resultat['message']
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@token_requis
def change_password(utilisateur_actuel):
    """Endpoint pour changer le mot de passe d'un utilisateur"""
    donnees = request.get_json()
    
    # Vérifier les données requises
    if not donnees or 'mot_de_passe_actuel' not in donnees or 'nouveau_mot_de_passe' not in donnees:
        raise ErreurRequeteInvalide("Les champs 'mot_de_passe_actuel' et 'nouveau_mot_de_passe' sont requis")
    
    # Changer le mot de passe
    resultat = changer_mot_de_passe(utilisateur_actuel, donnees)
    
    return jsonify({
        'statut': 'succes',
        'message': resultat['message']
    }), 200
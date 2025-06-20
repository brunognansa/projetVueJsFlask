from flask import Blueprint, request, jsonify
from app.models.user import Utilisateur
from app.utils.validation import SchemaMiseAJourUtilisateur, SchemaMiseAJourRoleUtilisateur, SchemaMiseAJourStatutUtilisateur, valider_donnees_requete
from app.utils.security import token_requis, admin_requis
from app.utils.database import obtenir_ou_404, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve, ErreurConflit

user_bp = Blueprint('users', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_requis
def obtenir_profil(utilisateur_actuel):
    """Endpoint pour obtenir le profil de l'utilisateur connecté"""
    return jsonify({
        'statut': 'succes',
        'utilisateur': utilisateur_actuel.vers_dict()
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@token_requis
def mettre_a_jour_profil(utilisateur_actuel):
    """Endpoint pour mettre à jour le profil de l'utilisateur connecté"""
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaMiseAJourUtilisateur, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Mettre à jour les champs
    if 'prenom' in donnees_validees:
        utilisateur_actuel.prenom = donnees_validees['prenom']
    if 'nom' in donnees_validees:
        utilisateur_actuel.nom = donnees_validees['nom']
    if 'email' in donnees_validees:
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        utilisateur_existant = Utilisateur.query.filter_by(email=donnees_validees['email']).first()
        if utilisateur_existant and utilisateur_existant.id != utilisateur_actuel.id:
            raise ErreurConflit("Cet email est déjà utilisé par un autre utilisateur")
        utilisateur_actuel.email = donnees_validees['email']
    if 'mot_de_passe' in donnees_validees:
        utilisateur_actuel.mot_de_passe = donnees_validees['mot_de_passe']
    
    valider_changements()
    
    return jsonify({
        'statut': 'succes',
        'message': 'Profil mis à jour avec succès',
        'utilisateur': utilisateur_actuel.vers_dict()
    }), 200

@user_bp.route('', methods=['GET'])
@admin_requis
def obtenir_utilisateurs(utilisateur_actuel):
    """Endpoint pour obtenir la liste des utilisateurs (admin seulement)"""
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)
    
    # Obtenir les utilisateurs paginés
    resultat = paginer_resultats(Utilisateur.query, page, par_page)
    
    return jsonify({
        'statut': 'succes',
        'utilisateurs': [utilisateur.vers_dict() for utilisateur in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200

@user_bp.route('/<int:utilisateur_id>/role', methods=['PUT'])
@admin_requis
def mettre_a_jour_role(utilisateur_actuel, utilisateur_id):
    """Endpoint pour mettre à jour le rôle d'un utilisateur (admin seulement)"""
    # Vérifier si l'utilisateur essaie de modifier son propre rôle
    if utilisateur_id == utilisateur_actuel.id:
        return jsonify({
            'statut': 'erreur',
            'message': 'Vous ne pouvez pas modifier votre propre rôle'
        }), 400
    
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaMiseAJourRoleUtilisateur, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Mettre à jour le rôle
    utilisateur.est_admin = donnees_validees['est_admin']
    valider_changements()
    
    return jsonify({
        'statut': 'succes',
        'message': 'Rôle utilisateur mis à jour avec succès',
        'utilisateur': utilisateur.vers_dict()
    }), 200

@user_bp.route('/<int:utilisateur_id>/status', methods=['PUT'])
@admin_requis
def mettre_a_jour_statut(utilisateur_actuel, utilisateur_id):
    """Endpoint pour activer/désactiver un compte utilisateur (admin seulement)"""
    # Vérifier si l'utilisateur essaie de modifier son propre statut
    if utilisateur_id == utilisateur_actuel.id:
        return jsonify({
            'statut': 'erreur',
            'message': 'Vous ne pouvez pas désactiver votre propre compte'
        }), 400
    
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaMiseAJourStatutUtilisateur, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Mettre à jour le statut
    utilisateur.est_actif = donnees_validees['est_actif']
    valider_changements()
    
    return jsonify({
        'statut': 'succes',
        'message': 'Statut utilisateur mis à jour avec succès',
        'utilisateur': utilisateur.vers_dict()
    }), 200
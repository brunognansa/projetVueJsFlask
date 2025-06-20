from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.loan import Emprunt
from app.models.book import Livre
from app.utils.validation import SchemaCreationEmprunt, SchemaRetourEmprunt, valider_donnees_requete
from app.utils.security import token_requis, admin_requis
from app.utils.database import ajouter_a_db, obtenir_ou_404, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve, ErreurConflit

loan_bp = Blueprint('loans', __name__)

@loan_bp.route('', methods=['POST'])
@token_requis
def creer_emprunt(utilisateur_actuel):
    """Endpoint pour emprunter un livre"""
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaCreationEmprunt, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Obtenir le livre
    livre = obtenir_ou_404(Livre, donnees_validees.get('livre_id'), "Livre non trouvé")
    
    # Vérifier si le livre est disponible
    if not livre.est_disponible():
        raise ErreurConflit("Ce livre n'est pas disponible pour l'emprunt")
    
    # Créer l'emprunt
    duree_emprunt = donnees_validees.get('duree_emprunt', 14)  # Défaut: 14 jours
    nouvel_emprunt = Emprunt(
        utilisateur_id=utilisateur_actuel.id,
        livre_id=livre.id,
        duree_emprunt=duree_emprunt
    )
    
    # Mettre à jour la disponibilité du livre
    livre.disponible -= 1
    
    # Sauvegarder les changements
    ajouter_a_db(nouvel_emprunt)
    valider_changements()
    
    return jsonify({
        'statut': 'succes',
        'message': 'Livre emprunté avec succès',
        'emprunt': nouvel_emprunt.vers_dict()
    }), 201

@loan_bp.route('/active', methods=['GET'])
@token_requis
def obtenir_emprunts_actifs(utilisateur_actuel):
    """Endpoint pour obtenir les emprunts actifs de l'utilisateur"""
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)
    
    # Obtenir les emprunts actifs (non retournés)
    requete = Emprunt.query.filter_by(
        utilisateur_id=utilisateur_actuel.id,
        date_retour_effective=None
    )
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return jsonify({
        'statut': 'succes',
        'emprunts': [emprunt.vers_dict() for emprunt in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200

@loan_bp.route('/history', methods=['GET'])
@token_requis
def obtenir_historique_emprunts(utilisateur_actuel):
    """Endpoint pour obtenir l'historique des emprunts de l'utilisateur"""
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)
    
    # Obtenir tous les emprunts de l'utilisateur
    requete = Emprunt.query.filter_by(utilisateur_id=utilisateur_actuel.id)
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return jsonify({
        'statut': 'succes',
        'emprunts': [emprunt.vers_dict() for emprunt in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200

@loan_bp.route('/<int:emprunt_id>/return', methods=['PATCH'])
@token_requis
def retourner_livre(utilisateur_actuel, emprunt_id):
    """Endpoint pour retourner un livre emprunté"""
    # Obtenir l'emprunt
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    
    # Vérifier si l'utilisateur est autorisé à retourner ce livre
    if emprunt.utilisateur_id != utilisateur_actuel.id and not utilisateur_actuel.est_admin:
        return jsonify({
            'statut': 'erreur',
            'message': 'Vous n\'êtes pas autorisé à retourner ce livre'
        }), 403
    
    # Vérifier si le livre a déjà été retourné
    if emprunt.est_retourne():
        return jsonify({
            'statut': 'erreur',
            'message': 'Ce livre a déjà été retourné'
        }), 400
    
    # Obtenir le livre
    livre = obtenir_ou_404(Livre, emprunt.livre_id, "Livre non trouvé")
    
    # Marquer le livre comme retourné
    emprunt.retourner_livre()
    
    # Mettre à jour la disponibilité du livre
    livre.disponible += 1
    
    # Sauvegarder les changements
    valider_changements()
    
    return jsonify({
        'statut': 'succes',
        'message': 'Livre retourné avec succès',
        'emprunt': emprunt.vers_dict()
    }), 200

@loan_bp.route('', methods=['GET'])
@admin_requis
def obtenir_tous_emprunts(utilisateur_actuel):
    """Endpoint pour obtenir tous les emprunts (admin seulement)"""
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)
    actif_seulement = request.args.get('actif_seulement', 'false').lower() == 'true'
    
    # Filtrer les emprunts
    requete = Emprunt.query
    if actif_seulement:
        requete = requete.filter_by(date_retour_effective=None)
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return jsonify({
        'statut': 'succes',
        'emprunts': [emprunt.vers_dict() for emprunt in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200
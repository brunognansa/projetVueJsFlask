from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.book import Livre
from app.utils.validation import SchemaLivre, SchemaMiseAJourLivre, valider_donnees_requete
from app.utils.security import token_requis, admin_requis
from app.utils.database import ajouter_a_db, obtenir_ou_404, supprimer_de_db, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve

book_bp = Blueprint('books', __name__)

@book_bp.route('', methods=['POST'])
@admin_requis
def creer_livre(utilisateur_actuel):
    """Endpoint pour créer un nouveau livre (admin seulement)"""
    donnees = request.get_json()

    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaLivre, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400

    # Créer le livre
    nouveau_livre = Livre(
        titre=donnees_validees.get('titre'),
        auteur=donnees_validees.get('auteur'),
        isbn=donnees_validees.get('isbn'),
        date_publication=donnees_validees.get('date_publication'),
        quantite=donnees_validees.get('quantite', 1),
        disponible=donnees_validees.get('quantite', 1),
        cree_le=datetime.utcnow()
    )

    ajouter_a_db(nouveau_livre)

    return jsonify({
        'statut': 'succes',
        'message': 'Livre créé avec succès',
        'livre': nouveau_livre.vers_dict()
    }), 201

@book_bp.route('', methods=['GET'])
def obtenir_livres():
    """Endpoint pour obtenir la liste des livres"""
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)

    # Obtenir les livres paginés
    resultat = paginer_resultats(Livre.query, page, par_page)

    return jsonify({
        'statut': 'succes',
        'livres': [livre.vers_dict() for livre in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200

@book_bp.route('/<int:livre_id>', methods=['GET'])
def obtenir_livre(livre_id):
    """Endpoint pour obtenir les détails d'un livre"""
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")

    return jsonify({
        'statut': 'succes',
        'livre': livre.vers_dict()
    }), 200

@book_bp.route('/<int:livre_id>', methods=['PUT'])
@admin_requis
def mettre_a_jour_livre(utilisateur_actuel, livre_id):
    """Endpoint pour mettre à jour un livre (admin seulement)"""
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")
    donnees = request.get_json()

    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaMiseAJourLivre, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400

    # Mettre à jour les champs
    if 'titre' in donnees_validees:
        livre.titre = donnees_validees['titre']
    if 'auteur' in donnees_validees:
        livre.auteur = donnees_validees['auteur']
    if 'isbn' in donnees_validees:
        livre.isbn = donnees_validees['isbn']
    if 'date_publication' in donnees_validees:
        livre.date_publication = donnees_validees['date_publication']
    if 'quantite' in donnees_validees:
        # Calculer la différence pour mettre à jour disponible
        difference = donnees_validees['quantite'] - livre.quantite
        livre.quantite = donnees_validees['quantite']
        livre.disponible += difference

    valider_changements()

    return jsonify({
        'statut': 'succes',
        'message': 'Livre mis à jour avec succès',
        'livre': livre.vers_dict()
    }), 200

@book_bp.route('/<int:livre_id>', methods=['DELETE'])
@admin_requis
def supprimer_livre(utilisateur_actuel, livre_id):
    """Endpoint pour supprimer un livre (admin seulement)"""
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")

    # Vérifier si le livre a des emprunts actifs
    emprunts_actifs = [e for e in livre.emprunts if not e.est_retourne()]
    if emprunts_actifs:
        return jsonify({
            'statut': 'erreur',
            'message': 'Impossible de supprimer un livre avec des emprunts actifs'
        }), 400

    supprimer_de_db(livre)

    return jsonify({
        'statut': 'succes',
        'message': 'Livre supprimé avec succès'
    }), 200

@book_bp.route('/search', methods=['GET'])
def rechercher_livres():
    """Endpoint pour rechercher des livres"""
    terme = request.args.get('terme', '')
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)

    if not terme:
        return jsonify({
            'statut': 'erreur',
            'message': 'Le paramètre de recherche "terme" est requis'
        }), 400

    # Rechercher les livres
    requete = Livre.query.filter(
        (Livre.titre.ilike(f'%{terme}%')) |
        (Livre.auteur.ilike(f'%{terme}%')) |
        (Livre.isbn.ilike(f'%{terme}%'))
    )

    resultat = paginer_resultats(requete, page, par_page)

    return jsonify({
        'statut': 'succes',
        'livres': [livre.vers_dict() for livre in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200

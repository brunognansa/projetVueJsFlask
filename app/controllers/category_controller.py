from flask import Blueprint, request, jsonify
from app.models.category import Categorie
from app.utils.validation import SchemaCategorie, SchemaMiseAJourCategorie, valider_donnees_requete
from app.utils.security import admin_requis
from app.utils.database import ajouter_a_db, obtenir_ou_404, supprimer_de_db, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve, ErreurConflit

category_bp = Blueprint('categories', __name__)

@category_bp.route('', methods=['POST'])
@admin_requis
def creer_categorie(utilisateur_actuel):
    """Endpoint pour créer une nouvelle catégorie (admin seulement)"""
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaCategorie, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Vérifier si la catégorie existe déjà
    categorie_existante = Categorie.query.filter_by(nom=donnees_validees.get('nom')).first()
    if categorie_existante:
        return jsonify({
            'statut': 'erreur',
            'message': 'Une catégorie avec ce nom existe déjà'
        }), 409
    
    # Créer la catégorie
    nouvelle_categorie = Categorie(
        nom=donnees_validees.get('nom'),
        description=donnees_validees.get('description', '')
    )
    
    ajouter_a_db(nouvelle_categorie)
    
    return jsonify({
        'statut': 'succes',
        'message': 'Catégorie créée avec succès',
        'categorie': nouvelle_categorie.vers_dict()
    }), 201

@category_bp.route('', methods=['GET'])
def obtenir_categories():
    """Endpoint pour obtenir la liste des catégories"""
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)
    
    # Obtenir les catégories paginées
    resultat = paginer_resultats(Categorie.query, page, par_page)
    
    return jsonify({
        'statut': 'succes',
        'categories': [categorie.vers_dict() for categorie in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }), 200

@category_bp.route('/<int:categorie_id>', methods=['GET'])
def obtenir_categorie(categorie_id):
    """Endpoint pour obtenir les détails d'une catégorie"""
    categorie = obtenir_ou_404(Categorie, categorie_id, "Catégorie non trouvée")
    
    return jsonify({
        'statut': 'succes',
        'categorie': categorie.vers_dict()
    }), 200

@category_bp.route('/<int:categorie_id>', methods=['PUT'])
@admin_requis
def mettre_a_jour_categorie(utilisateur_actuel, categorie_id):
    """Endpoint pour mettre à jour une catégorie (admin seulement)"""
    categorie = obtenir_ou_404(Categorie, categorie_id, "Catégorie non trouvée")
    donnees = request.get_json()
    
    # Valider les données
    donnees_validees = valider_donnees_requete(SchemaMiseAJourCategorie, donnees)
    if 'erreurs' in donnees_validees:
        return jsonify({'statut': 'erreur', 'erreurs': donnees_validees['erreurs']}), 400
    
    # Vérifier si le nom existe déjà pour une autre catégorie
    if 'nom' in donnees_validees and donnees_validees['nom'] != categorie.nom:
        categorie_existante = Categorie.query.filter_by(nom=donnees_validees['nom']).first()
        if categorie_existante:
            return jsonify({
                'statut': 'erreur',
                'message': 'Une catégorie avec ce nom existe déjà'
            }), 409
    
    # Mettre à jour les champs
    if 'nom' in donnees_validees:
        categorie.nom = donnees_validees['nom']
    if 'description' in donnees_validees:
        categorie.description = donnees_validees['description']
    
    valider_changements()
    
    return jsonify({
        'statut': 'succes',
        'message': 'Catégorie mise à jour avec succès',
        'categorie': categorie.vers_dict()
    }), 200

@category_bp.route('/<int:categorie_id>', methods=['DELETE'])
@admin_requis
def supprimer_categorie(utilisateur_actuel, categorie_id):
    """Endpoint pour supprimer une catégorie (admin seulement)"""
    categorie = obtenir_ou_404(Categorie, categorie_id, "Catégorie non trouvée")
    
    # Vérifier si la catégorie a des livres associés
    if categorie.livres:
        return jsonify({
            'statut': 'erreur',
            'message': 'Impossible de supprimer une catégorie avec des livres associés'
        }), 400
    
    supprimer_de_db(categorie)
    
    return jsonify({
        'statut': 'succes',
        'message': 'Catégorie supprimée avec succès'
    }), 200

@category_bp.route('/<int:categorie_id>/livres', methods=['GET'])
def obtenir_livres_par_categorie(categorie_id):
    """Endpoint pour obtenir les livres d'une catégorie spécifique"""
    categorie = obtenir_ou_404(Categorie, categorie_id, "Catégorie non trouvée")
    page = request.args.get('page', 1, type=int)
    par_page = request.args.get('par_page', 10, type=int)
    
    # Obtenir les livres de la catégorie
    from app.models.book import Livre
    requete = Livre.query.filter_by(categorie_id=categorie_id)
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return jsonify({
        'statut': 'succes',
        'categorie': categorie.vers_dict(),
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
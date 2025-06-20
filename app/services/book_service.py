from app.models.book import Livre
from app.utils.database import ajouter_a_db, obtenir_ou_404, supprimer_de_db, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve, ErreurConflit
from datetime import datetime

def creer_livre(donnees):
    """Créer un nouveau livre"""
    # Vérifier si l'ISBN existe déjà
    livre_existant = Livre.query.filter_by(isbn=donnees.get('isbn')).first()
    if livre_existant:
        raise ErreurConflit("Un livre avec cet ISBN existe déjà")
    
    # Créer le livre    
    nouveau_livre = Livre(
        titre=donnees.get('titre'),
        auteur=donnees.get('auteur'),
        isbn=donnees.get('isbn'),
        date_publication=donnees.get('date_publication'),
        quantite=donnees.get('quantite', 1),
        disponible=donnees.get('quantite', 1),
        cree_le=datetime.utcnow()
    )
    
    ajouter_a_db(nouveau_livre)
    
    return nouveau_livre.vers_dict()

def obtenir_livre(livre_id):
    """Obtenir les détails d'un livre par ID"""
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")
    return livre.vers_dict()

def obtenir_livres(page=1, par_page=10):
    """Obtenir la liste des livres paginée"""
    resultat = paginer_resultats(Livre.query, page, par_page)
    return {
        'livres': [livre.vers_dict() for livre in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }

def mettre_a_jour_livre(livre_id, donnees):
    """Mettre à jour les détails d'un livre"""
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")
    
    # Vérifier si l'ISBN est déjà utilisé par un autre livre
    if 'isbn' in donnees and donnees['isbn'] != livre.isbn:
        livre_existant = Livre.query.filter_by(isbn=donnees['isbn']).first()
        if livre_existant:
            raise ErreurConflit("Un livre avec cet ISBN existe déjà")
    
    # Mettre à jour les champs
    if 'titre' in donnees:
        livre.titre = donnees['titre']
    if 'auteur' in donnees:
        livre.auteur = donnees['auteur']
    if 'isbn' in donnees:
        livre.isbn = donnees['isbn']
    if 'date_publication' in donnees:
        livre.date_publication = donnees['date_publication']
    if 'quantite' in donnees:
        # Calculer la différence pour mettre à jour disponible
        difference = donnees['quantite'] - livre.quantite
        livre.quantite = donnees['quantite']
        livre.disponible += difference
    
    valider_changements()
    
    return livre.vers_dict()

def supprimer_livre(livre_id):
    """Supprimer un livre"""
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")
    
    # Vérifier si le livre a des emprunts actifs
    emprunts_actifs = [e for e in livre.emprunts if not e.est_retourne()]
    if emprunts_actifs:
        raise ErreurRequeteInvalide("Impossible de supprimer un livre avec des emprunts actifs")
    
    supprimer_de_db(livre)
    
    return {"message": "Livre supprimé avec succès"}

def rechercher_livres(terme, page=1, par_page=10):
    """Rechercher des livres par titre, auteur ou ISBN"""
    if not terme:
        raise ErreurRequeteInvalide("Le terme de recherche est requis")
    
    # Rechercher les livres
    requete = Livre.query.filter(
        (Livre.titre.ilike(f'%{terme}%')) |
        (Livre.auteur.ilike(f'%{terme}%')) |
        (Livre.isbn.ilike(f'%{terme}%'))
    )
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return {
        'livres': [livre.vers_dict() for livre in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }
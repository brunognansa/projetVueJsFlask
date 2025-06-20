from app import db
from sqlalchemy.exc import SQLAlchemyError
from app.utils.error_handler import ErreurServeur, ErreurNonTrouve, ErreurConflit

def valider_changements():
    """Valider les changements dans la base de données"""
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ErreurServeur(f"Erreur de base de données: {str(e)}")

def ajouter_a_db(element):
    """Ajouter un élément à la base de données"""
    try:
        db.session.add(element)
        valider_changements()
        return element
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ErreurServeur(f"Erreur lors de l'ajout à la base de données: {str(e)}")

def supprimer_de_db(element):
    """Supprimer un élément de la base de données"""
    try:
        db.session.delete(element)
        valider_changements()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ErreurServeur(f"Erreur lors de la suppression de la base de données: {str(e)}")

def obtenir_ou_404(modele, id, message="Ressource non trouvée"):
    """Obtenir un élément par ID ou lever une erreur 404"""
    element = modele.query.get(id)
    if not element:
        raise ErreurNonTrouve(message)
    return element

def obtenir_par_champ_ou_404(modele, champ, valeur, message="Ressource non trouvée"):
    """Obtenir un élément par un champ spécifique ou lever une erreur 404"""
    element = modele.query.filter_by(**{champ: valeur}).first()
    if not element:
        raise ErreurNonTrouve(message)
    return element

def verifier_unique_ou_409(modele, champ, valeur, message="La ressource existe déjà"):
    """Vérifier si la valeur d'un champ est unique ou lever une erreur 409"""
    element = modele.query.filter_by(**{champ: valeur}).first()
    if element:
        raise ErreurConflit(message)
    return True

def paginer_resultats(requete, page=1, par_page=10):
    """Paginer les résultats de requête"""
    try:
        pagine = requete.paginate(page=page, per_page=par_page, error_out=False)
        return {
            'elements': pagine.items,
            'page': pagine.page,
            'par_page': pagine.per_page,
            'total': pagine.total,
            'pages': pagine.pages,
            'a_suivant': pagine.has_next,
            'a_precedent': pagine.has_prev
        }
    except SQLAlchemyError as e:
        raise ErreurServeur(f"Erreur lors de la pagination des résultats: {str(e)}")

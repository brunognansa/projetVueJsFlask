from app.models.loan import Emprunt
from app.models.book import Livre
from app.models.user import Utilisateur
from app.utils.database import ajouter_a_db, obtenir_ou_404, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve, ErreurConflit, ErreurInterdit
from datetime import datetime

def creer_emprunt(utilisateur_id, donnees):
    """Créer un nouvel emprunt"""
    # Obtenir l'utilisateur
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    
    # Obtenir le livre
    livre_id = donnees.get('livre_id')
    livre = obtenir_ou_404(Livre, livre_id, "Livre non trouvé")
    
    # Vérifier si le livre est disponible
    if not livre.est_disponible():
        raise ErreurConflit("Ce livre n'est pas disponible pour l'emprunt")
    
    # Créer l'emprunt
    duree_emprunt = donnees.get('duree_emprunt', 14)  # Défaut: 14 jours
    nouvel_emprunt = Emprunt(
        utilisateur_id=utilisateur.id,
        livre_id=livre.id,
        duree_emprunt=duree_emprunt
    )
    
    # Mettre à jour la disponibilité du livre
    livre.disponible -= 1
    
    # Sauvegarder les changements
    ajouter_a_db(nouvel_emprunt)
    valider_changements()
    
    return nouvel_emprunt.vers_dict()

def obtenir_emprunt(emprunt_id):
    """Obtenir les détails d'un emprunt par ID"""
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    return emprunt.vers_dict()

def obtenir_emprunts_utilisateur(utilisateur_id, actifs_seulement=False, page=1, par_page=10):
    """Obtenir les emprunts d'un utilisateur"""
    # Obtenir l'utilisateur
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    
    # Filtrer les emprunts
    requete = Emprunt.query.filter_by(utilisateur_id=utilisateur.id)
    if actifs_seulement:
        requete = requete.filter_by(date_retour_effective=None)
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return {
        'emprunts': [emprunt.vers_dict() for emprunt in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }

def obtenir_tous_emprunts(actifs_seulement=False, page=1, par_page=10):
    """Obtenir tous les emprunts (admin seulement)"""
    # Filtrer les emprunts
    requete = Emprunt.query
    if actifs_seulement:
        requete = requete.filter_by(date_retour_effective=None)
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return {
        'emprunts': [emprunt.vers_dict() for emprunt in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }

def retourner_livre(emprunt_id, utilisateur_id):
    """Retourner un livre emprunté"""
    # Obtenir l'emprunt
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    
    # Obtenir l'utilisateur
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    
    # Vérifier si l'utilisateur est autorisé à retourner ce livre
    if emprunt.utilisateur_id != utilisateur.id and not utilisateur.est_admin:
        raise ErreurInterdit("Vous n'êtes pas autorisé à retourner ce livre")
    
    # Vérifier si le livre a déjà été retourné
    if emprunt.est_retourne():
        raise ErreurRequeteInvalide("Ce livre a déjà été retourné")
    
    # Obtenir le livre
    livre = obtenir_ou_404(Livre, emprunt.livre_id, "Livre non trouvé")
    
    # Marquer le livre comme retourné
    emprunt.retourner_livre()
    
    # Mettre à jour la disponibilité du livre
    livre.disponible += 1
    
    # Sauvegarder les changements
    valider_changements()
    
    return emprunt.vers_dict()

def obtenir_emprunts_en_retard(page=1, par_page=10):
    """Obtenir les emprunts en retard"""
    # Obtenir la date actuelle
    maintenant = datetime.utcnow()
    
    # Filtrer les emprunts en retard (date de retour prévue passée et non retournés)
    requete = Emprunt.query.filter(
        Emprunt.date_retour_prevue < maintenant,
        Emprunt.date_retour_effective == None
    )
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return {
        'emprunts': [emprunt.vers_dict() for emprunt in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }
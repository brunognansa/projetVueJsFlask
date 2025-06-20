from app.models.user import Utilisateur
from app.utils.database import ajouter_a_db, obtenir_ou_404, valider_changements, paginer_resultats
from app.utils.error_handler import ErreurRequeteInvalide, ErreurNonTrouve, ErreurConflit, ErreurInterdit
from app.utils.validation import valider_email_utilisateur
from datetime import datetime

def obtenir_utilisateur(utilisateur_id):
    """Obtenir les détails d'un utilisateur par ID"""
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    return utilisateur.vers_dict()

def obtenir_utilisateurs(page=1, par_page=10):
    """Obtenir la liste des utilisateurs paginée"""
    resultat = paginer_resultats(Utilisateur.query, page, par_page)
    return {
        'utilisateurs': [utilisateur.vers_dict() for utilisateur in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }

def mettre_a_jour_profil(utilisateur_id, donnees):
    """Mettre à jour le profil d'un utilisateur"""
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    
    # Mettre à jour les champs
    if 'prenom' in donnees:
        utilisateur.prenom = donnees['prenom']
    if 'nom' in donnees:
        utilisateur.nom = donnees['nom']
    if 'email' in donnees:
        # Valider le format de l'email
        if not valider_email_utilisateur(donnees['email']):
            raise ErreurRequeteInvalide("Format d'email invalide")
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        utilisateur_existant = Utilisateur.query.filter_by(email=donnees['email']).first()
        if utilisateur_existant and utilisateur_existant.id != utilisateur.id:
            raise ErreurConflit("Cet email est déjà utilisé par un autre utilisateur")
        
        utilisateur.email = donnees['email']
    if 'mot_de_passe' in donnees:
        utilisateur.mot_de_passe = donnees['mot_de_passe']
    
    valider_changements()
    
    return utilisateur.vers_dict()

def mettre_a_jour_role(utilisateur_id, est_admin, admin_id):
    """Mettre à jour le rôle d'un utilisateur (admin seulement)"""
    # Vérifier si l'admin essaie de modifier son propre rôle
    if utilisateur_id == admin_id:
        raise ErreurRequeteInvalide("Vous ne pouvez pas modifier votre propre rôle")
    
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    
    # Mettre à jour le rôle
    utilisateur.est_admin = est_admin
    valider_changements()
    
    return utilisateur.vers_dict()

def mettre_a_jour_statut(utilisateur_id, est_actif, admin_id):
    """Activer/désactiver un compte utilisateur (admin seulement)"""
    # Vérifier si l'admin essaie de modifier son propre statut
    if utilisateur_id == admin_id:
        raise ErreurRequeteInvalide("Vous ne pouvez pas désactiver votre propre compte")
    
    utilisateur = obtenir_ou_404(Utilisateur, utilisateur_id, "Utilisateur non trouvé")
    
    # Mettre à jour le statut
    utilisateur.est_actif = est_actif
    valider_changements()
    
    return utilisateur.vers_dict()

def rechercher_utilisateurs(terme, page=1, par_page=10):
    """Rechercher des utilisateurs par nom, prénom ou email"""
    if not terme:
        raise ErreurRequeteInvalide("Le terme de recherche est requis")
    
    # Rechercher les utilisateurs
    requete = Utilisateur.query.filter(
        (Utilisateur.prenom.ilike(f'%{terme}%')) |
        (Utilisateur.nom.ilike(f'%{terme}%')) |
        (Utilisateur.email.ilike(f'%{terme}%'))
    )
    
    resultat = paginer_resultats(requete, page, par_page)
    
    return {
        'utilisateurs': [utilisateur.vers_dict() for utilisateur in resultat['elements']],
        'pagination': {
            'page': resultat['page'],
            'par_page': resultat['par_page'],
            'total': resultat['total'],
            'pages': resultat['pages'],
            'a_suivant': resultat['a_suivant'],
            'a_precedent': resultat['a_precedent']
        }
    }
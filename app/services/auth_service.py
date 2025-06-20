from datetime import datetime
from app.models.user import Utilisateur
from app.utils.database import ajouter_a_db, obtenir_par_champ_ou_404, verifier_unique_ou_409, valider_changements
from app.utils.security import generer_tokens, revoquer_token
from app.utils.error_handler import ErreurNonAutorise, ErreurValidation, ErreurRequeteInvalide
from app.utils.validation import valider_email_utilisateur
from flask_jwt_extended import get_jwt, get_jwt_identity, create_access_token

def inscrire_utilisateur(donnees):
    """Inscrire un nouvel utilisateur"""
    # Valider le format de l'email
    if not valider_email_utilisateur(donnees.get('email')):
        raise ErreurValidation("Format d'email invalide")

    # Vérifier si l'email existe déjà
    verifier_unique_ou_409(Utilisateur, 'email', donnees.get('email'), "Email déjà enregistré")

    # Créer un nouvel utilisateur
    nouvel_utilisateur = Utilisateur(
        prenom=donnees.get('prenom'),
        nom=donnees.get('nom'),
        email=donnees.get('email'),
        est_actif=True,
        est_admin=False,
        cree_le=datetime.utcnow()
    )

    # Définir le mot de passe
    nouvel_utilisateur.mot_de_passe = donnees.get('mot_de_passe')

    # Sauvegarder dans la base de données
    ajouter_a_db(nouvel_utilisateur)

    return nouvel_utilisateur.vers_dict()

def connecter_utilisateur(donnees):
    """Authentifier un utilisateur et générer des tokens"""
    # Obtenir l'utilisateur par email
    try:
        utilisateur = obtenir_par_champ_ou_404(Utilisateur, 'email', donnees.get('email'), "Email ou mot de passe invalide")
    except:
        # Utiliser le même message d'erreur pour la sécurité
        raise ErreurNonAutorise("Email ou mot de passe invalide")

    # Vérifier le mot de passe
    if not utilisateur.verifier_mot_de_passe(donnees.get('mot_de_passe')):
        raise ErreurNonAutorise("Email ou mot de passe invalide")

    # Vérifier si l'utilisateur est actif
    if not utilisateur.est_actif:
        raise ErreurNonAutorise("Compte désactivé")

    # Mettre à jour la dernière connexion
    utilisateur.derniere_connexion = datetime.utcnow()
    valider_changements()

    # Générer des tokens
    tokens = generer_tokens(utilisateur.id)

    return {
        'utilisateur': utilisateur.vers_dict(),
        'tokens': tokens
    }

def rafraichir_token():
    """Générer un nouveau token d'accès en utilisant un token de rafraîchissement"""
    # L'identité est déjà vérifiée par le décorateur @jwt_refresh_token_required
    utilisateur_id = get_jwt_identity()

    # Obtenir l'utilisateur
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur or not utilisateur.est_actif:
        raise ErreurNonAutorise("Utilisateur invalide ou inactif")

    # Générer un nouveau token d'accès
    token_acces = create_access_token(identity=utilisateur_id)

    return {
        'token_acces': token_acces
    }

def deconnecter_utilisateur():
    """Révoquer le token actuel"""
    jti = get_jwt()['jti']
    revoquer_token(jti)

    return {
        'message': 'Déconnexion réussie'
    }

def changer_mot_de_passe(utilisateur, donnees):
    """Changer le mot de passe de l'utilisateur"""
    # Vérifier le mot de passe actuel
    if not utilisateur.verifier_mot_de_passe(donnees.get('mot_de_passe_actuel')):
        raise ErreurNonAutorise("Le mot de passe actuel est incorrect")

    # Vérifier si le nouveau mot de passe répond aux exigences
    nouveau_mot_de_passe = donnees.get('nouveau_mot_de_passe')
    if len(nouveau_mot_de_passe) < 8:
        raise ErreurValidation("Le mot de passe doit comporter au moins 8 caractères")

    # Définir le nouveau mot de passe
    utilisateur.mot_de_passe = nouveau_mot_de_passe
    valider_changements()

    return {
        'message': 'Mot de passe changé avec succès'
    }

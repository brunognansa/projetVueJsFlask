from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, verify_jwt_in_request,
    get_jwt
)
from app.models.user import Utilisateur
from app.utils.error_handler import ErreurNonAutorise, ErreurInterdit

# Ensemble de liste noire de tokens révoqués
LISTE_NOIRE = set()


def generer_tokens(utilisateur_id):
    """Générer des tokens d'accès et de rafraîchissement pour un utilisateur"""
    # CORRECTION: Convertir l'ID en string
    identity_str = str(utilisateur_id)
    token_acces = create_access_token(identity=identity_str)
    token_rafraichissement = create_refresh_token(identity=identity_str)
    return {
        'token_acces': token_acces,
        'token_rafraichissement': token_rafraichissement
    }


def revoquer_token(jti):
    """Ajouter un JWT ID à la liste noire"""
    LISTE_NOIRE.add(jti)


def est_token_revoque(payload_jwt):
    """Vérifier si un token a été révoqué"""
    jti = payload_jwt['jti']
    return jti in LISTE_NOIRE


def token_requis(fn):
    """Décorateur pour protéger les routes avec JWT"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            donnees_jwt = get_jwt()

            # Vérifier si le token est dans la liste noire
            if est_token_revoque(donnees_jwt):
                raise ErreurNonAutorise("Le token a été révoqué")

            # Obtenir l'utilisateur actuel
            utilisateur_actuel_id = get_jwt_identity()

            # CORRECTION: Convertir l'identité string en int
            try:
                utilisateur_actuel_id_int = int(utilisateur_actuel_id)
            except (ValueError, TypeError):
                raise ErreurNonAutorise("Format d'identité invalide")

            utilisateur_actuel = Utilisateur.query.get(utilisateur_actuel_id_int)

            if not utilisateur_actuel:
                raise ErreurNonAutorise("Utilisateur invalide")

            if not utilisateur_actuel.est_actif:
                raise ErreurNonAutorise("Le compte utilisateur est désactivé")

            return fn(utilisateur_actuel, *args, **kwargs)
        except Exception as e:
            # Ajouter un log d'erreur pour le débogage
            current_app.logger.error(f"Erreur token_requis: {str(e)}")
            raise ErreurNonAutorise(str(e))

    return wrapper


def admin_requis(fn):
    """Décorateur pour protéger les routes réservées aux administrateurs"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            donnees_jwt = get_jwt()

            # Vérifier si le token est dans la liste noire
            if est_token_revoque(donnees_jwt):
                raise ErreurNonAutorise("Le token a été révoqué")

            # Obtenir l'utilisateur actuel
            utilisateur_actuel_id = get_jwt_identity()

            # CORRECTION: Convertir l'identité string en int
            try:
                utilisateur_actuel_id_int = int(utilisateur_actuel_id)
            except (ValueError, TypeError):
                raise ErreurNonAutorise("Format d'identité invalide")

            utilisateur_actuel = Utilisateur.query.get(utilisateur_actuel_id_int)

            if not utilisateur_actuel:
                raise ErreurNonAutorise("Utilisateur invalide")

            if not utilisateur_actuel.est_actif:
                raise ErreurNonAutorise("Le compte utilisateur est désactivé")

            if not utilisateur_actuel.est_admin:
                raise ErreurInterdit("Privilèges d'administrateur requis")

            return fn(utilisateur_actuel, *args, **kwargs)
        except Exception as e:
            # Ajouter un log d'erreur pour le débogage
            current_app.logger.error(f"Erreur admin_requis: {str(e)}")
            if isinstance(e, ErreurInterdit):
                raise e
            raise ErreurNonAutorise(str(e))

    return wrapper
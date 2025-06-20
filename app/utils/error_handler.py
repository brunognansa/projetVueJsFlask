from flask import jsonify

class ErreurAPI(Exception):
    """Classe de base pour les erreurs API"""
    def __init__(self, message, code_statut=400, payload=None):
        super().__init__()
        self.message = message
        self.code_statut = code_statut
        self.payload = payload

    def vers_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['statut'] = 'erreur'
        return rv

class ErreurRequeteInvalide(ErreurAPI):
    """Exception levée pour les erreurs de requête invalide"""
    def __init__(self, message, payload=None):
        super().__init__(message, 400, payload)

class ErreurNonAutorise(ErreurAPI):
    """Exception levée pour un accès non autorisé"""
    def __init__(self, message="Accès non autorisé", payload=None):
        super().__init__(message, 401, payload)

class ErreurInterdit(ErreurAPI):
    """Exception levée pour un accès interdit"""
    def __init__(self, message="Accès interdit", payload=None):
        super().__init__(message, 403, payload)

class ErreurNonTrouve(ErreurAPI):
    """Exception levée pour une ressource non trouvée"""
    def __init__(self, message="Ressource non trouvée", payload=None):
        super().__init__(message, 404, payload)

class ErreurConflit(ErreurAPI):
    """Exception levée pour les conflits de ressources"""
    def __init__(self, message="Conflit de ressource", payload=None):
        super().__init__(message, 409, payload)

class ErreurValidation(ErreurAPI):
    """Exception levée pour les erreurs de validation"""
    def __init__(self, message="Erreur de validation", payload=None):
        super().__init__(message, 422, payload)

class ErreurServeur(ErreurAPI):
    """Exception levée pour les erreurs de serveur"""
    def __init__(self, message="Erreur interne du serveur", payload=None):
        super().__init__(message, 500, payload)

def enregistrer_gestionnaires_erreurs(app):
    """Enregistrer les gestionnaires d'erreurs pour l'application Flask"""

    @app.errorhandler(ErreurAPI)
    def gerer_erreur_api(erreur):
        reponse = jsonify(erreur.vers_dict())
        reponse.status_code = erreur.code_statut
        return reponse

    @app.errorhandler(400)
    def gerer_requete_invalide(erreur):
        return jsonify({
            'statut': 'erreur',
            'message': 'Requête invalide'
        }), 400

    @app.errorhandler(401)
    def gerer_non_autorise(erreur):
        return jsonify({
            'statut': 'erreur',
            'message': 'Accès non autorisé'
        }), 401

    @app.errorhandler(403)
    def gerer_interdit(erreur):
        return jsonify({
            'statut': 'erreur',
            'message': 'Accès interdit'
        }), 403

    @app.errorhandler(404)
    def gerer_non_trouve(erreur):
        return jsonify({
            'statut': 'erreur',
            'message': 'Ressource non trouvée'
        }), 404

    @app.errorhandler(405)
    def gerer_methode_non_autorisee(erreur):
        return jsonify({
            'statut': 'erreur',
            'message': 'Méthode non autorisée'
        }), 405

    @app.errorhandler(500)
    def gerer_erreur_serveur(erreur):
        return jsonify({
            'statut': 'erreur',
            'message': 'Erreur interne du serveur'
        }), 500

from marshmallow import Schema, fields, validate, ValidationError
from email_validator import validate_email, EmailNotValidError

# Schémas Utilisateur
class SchemaInscriptionUtilisateur(Schema):
    prenom = fields.String(required=True, validate=validate.Length(min=2, max=50))
    nom = fields.String(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=True)
    mot_de_passe = fields.String(required=True, validate=validate.Length(min=8))

class SchemaConnexionUtilisateur(Schema):
    email = fields.Email(required=True)
    mot_de_passe = fields.String(required=True)

class SchemaMiseAJourUtilisateur(Schema):
    prenom = fields.String(validate=validate.Length(min=2, max=50))
    nom = fields.String(validate=validate.Length(min=2, max=50))
    email = fields.Email()
    mot_de_passe = fields.String(validate=validate.Length(min=8))

class SchemaMiseAJourRoleUtilisateur(Schema):
    est_admin = fields.Boolean(required=True)

class SchemaMiseAJourStatutUtilisateur(Schema):
    est_actif = fields.Boolean(required=True)

# Schémas Livre
class SchemaLivre(Schema):
    titre = fields.String(required=True, validate=validate.Length(min=1, max=200))
    auteur = fields.String(required=True, validate=validate.Length(min=1, max=100))
    isbn = fields.String(required=True, validate=validate.Length(min=10, max=20))
    date_publication = fields.Date()
    quantite = fields.Integer(validate=validate.Range(min=1))

class SchemaMiseAJourLivre(Schema):
    titre = fields.String(validate=validate.Length(min=1, max=200))
    auteur = fields.String(validate=validate.Length(min=1, max=100))
    isbn = fields.String(validate=validate.Length(min=10, max=20))
    date_publication = fields.Date()
    quantite = fields.Integer(validate=validate.Range(min=1))

# Schémas Emprunt
class SchemaCreationEmprunt(Schema):
    livre_id = fields.Integer(required=True)
    duree_emprunt = fields.Integer(validate=validate.Range(min=1, max=30))

class SchemaRetourEmprunt(Schema):
    emprunt_id = fields.Integer(required=True)

# Fonctions utilitaires pour la validation
def valider_email_utilisateur(email):
    """Valider le format de l'email"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def valider_donnees_requete(schema, donnees):
    """Valider les données de la requête par rapport au schéma"""
    try:
        return schema().load(donnees)
    except ValidationError as err:
        return {'erreurs': err.messages}

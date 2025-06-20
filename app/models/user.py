from datetime import datetime
from app import db, bcrypt

class Utilisateur(db.Model):
    """Modèle Utilisateur pour stocker les détails liés à l'utilisateur"""
    __tablename__ = 'utilisateurs'

    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(128), nullable=False)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)
    est_actif = db.Column(db.Boolean, default=True)
    est_admin = db.Column(db.Boolean, default=False)
    derniere_connexion = db.Column(db.DateTime, nullable=True)

    # Relation avec les emprunts
    emprunts = db.relationship('Emprunt', backref='utilisateur', lazy=True, cascade='all, delete-orphan')

    @property
    def mot_de_passe(self):
        """Empêcher l'accès au mot de passe"""
        raise AttributeError('mot_de_passe n\'est pas un attribut lisible')

    @mot_de_passe.setter
    def mot_de_passe(self, mot_de_passe):
        """Définir le mot de passe haché"""
        self.mot_de_passe_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    def verifier_mot_de_passe(self, mot_de_passe):
        """Vérifier si le mot de passe correspond au mot de passe haché"""
        return bcrypt.check_password_hash(self.mot_de_passe_hash, mot_de_passe)

    def __repr__(self):
        return f'<Utilisateur {self.email}>'

    def vers_dict(self):
        """Convertir l'objet utilisateur en dictionnaire"""
        return {
            'id': self.id,
            'prenom': self.prenom,
            'nom': self.nom,
            'email': self.email,
            'cree_le': self.cree_le.isoformat() if self.cree_le else None,
            'est_actif': self.est_actif,
            'est_admin': self.est_admin,
            'derniere_connexion': self.derniere_connexion.isoformat() if self.derniere_connexion else None
        }

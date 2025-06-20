from datetime import datetime
from app import db

class Livre(db.Model):
    """Modèle Livre pour stocker les détails liés au livre"""
    __tablename__ = 'livres'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    auteur = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    date_publication = db.Column(db.Date, nullable=True)
    quantite = db.Column(db.Integer, default=1)
    disponible = db.Column(db.Integer, default=1)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec les emprunts
    emprunts = db.relationship('Emprunt', backref='livre', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Livre {self.titre} par {self.auteur}>'

    def est_disponible(self):
        """Vérifier si le livre est disponible pour l'emprunt"""
        return self.disponible > 0

    def vers_dict(self):
        """Convertir l'objet livre en dictionnaire"""
        return {
            'id': self.id,
            'titre': self.titre,
            'auteur': self.auteur,
            'isbn': self.isbn,
            'date_publication': self.date_publication.isoformat() if self.date_publication else None,
            'quantite': self.quantite,
            'disponible': self.disponible,
            'cree_le': self.cree_le.isoformat() if self.cree_le else None
        }

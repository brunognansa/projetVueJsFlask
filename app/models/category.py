from datetime import datetime
from app import db

class Categorie(db.Model):
    """Modèle Categorie pour stocker les détails liés aux catégories de livres"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec les livres
    livres = db.relationship('Livre', backref='categorie', lazy=True)

    def __repr__(self):
        return f'<Categorie {self.nom}>'

    def vers_dict(self):
        """Convertir l'objet catégorie en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'cree_le': self.cree_le.isoformat() if self.cree_le else None,
            'nombre_livres': len(self.livres)
        }
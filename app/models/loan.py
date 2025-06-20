from datetime import datetime, timedelta
from app import db

class Emprunt(db.Model):
    """Modèle Emprunt pour stocker les détails liés à l'emprunt"""
    __tablename__ = 'emprunts'

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    livre_id = db.Column(db.Integer, db.ForeignKey('livres.id'), nullable=False)
    date_emprunt = db.Column(db.DateTime, default=datetime.utcnow)
    date_retour_prevue = db.Column(db.DateTime, nullable=False)
    date_retour_effective = db.Column(db.DateTime, nullable=True)

    def __init__(self, utilisateur_id, livre_id, duree_emprunt=14):
        """Initialiser un nouvel emprunt avec une durée d'emprunt par défaut de 14 jours"""
        self.utilisateur_id = utilisateur_id
        self.livre_id = livre_id
        self.date_emprunt = datetime.utcnow()
        self.date_retour_prevue = self.date_emprunt + timedelta(days=duree_emprunt)

    def __repr__(self):
        return f'<Emprunt {self.id} - Utilisateur: {self.utilisateur_id}, Livre: {self.livre_id}>'

    def est_retourne(self):
        """Vérifier si le livre a été retourné"""
        return self.date_retour_effective is not None

    def est_en_retard(self):
        """Vérifier si l'emprunt est en retard"""
        if self.est_retourne():
            return False
        return datetime.utcnow() > self.date_retour_prevue

    def jours_de_retard(self):
        """Calculer le nombre de jours de retard de l'emprunt"""
        if not self.est_en_retard():
            return 0
        delta = datetime.utcnow() - self.date_retour_prevue
        return delta.days

    def retourner_livre(self):
        """Marquer le livre comme retourné"""
        self.date_retour_effective = datetime.utcnow()

    def vers_dict(self):
        """Convertir l'objet emprunt en dictionnaire"""
        return {
            'id': self.id,
            'utilisateur_id': self.utilisateur_id,
            'livre_id': self.livre_id,
            'date_emprunt': self.date_emprunt.isoformat() if self.date_emprunt else None,
            'date_retour_prevue': self.date_retour_prevue.isoformat() if self.date_retour_prevue else None,
            'date_retour_effective': self.date_retour_effective.isoformat() if self.date_retour_effective else None,
            'est_retourne': self.est_retourne(),
            'est_en_retard': self.est_en_retard(),
            'jours_de_retard': self.jours_de_retard() if self.est_en_retard() else 0
        }

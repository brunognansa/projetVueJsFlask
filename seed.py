from app import  db
from app.models import Utilisateur
from datetime import datetime

def seed_admin():
    # Vérifier si l'admin existe déjà
    if Utilisateur.query.filter_by(email="admin@bibliotheque.com").first():
        print("L'admin existe déjà")
        return

    admin = Utilisateur(
        prenom="Admin",
        nom="System",
        email="admin@bibliotheque.com",
        mot_de_passe="SecurePassword123!",
        est_admin=True,
        derniere_connexion=datetime.utcnow()
    )

    db.session.add(admin)
    db.session.commit()
    print("Admin mock créé avec succès")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_admin()
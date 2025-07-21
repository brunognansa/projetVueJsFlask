from app import create_app

# script personnaliser de crétion d'admin pour l'application
import app
import click

from app import db
from app.models import Utilisateur


app = create_app()

@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
def create_admin(email, password):
    """Crée un utilisateur admin"""
    if Utilisateur.query.filter_by(email=email).first():
        print("Un utilisateur avec cet email existe déjà")
        return

    admin = Utilisateur(
        prenom="Admin",
        nom="System",
        email=email,
        mot_de_passe=password,
        est_admin=True
    )

    db.session.add(admin)
    db.session.commit()
    print(f"Admin {email} créé avec succès")





if __name__ == '__main__':
    app.run(debug=True)



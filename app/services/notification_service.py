from flask import current_app, render_template
from flask_mail import Message
from app import mail
from app.models.user import Utilisateur
from app.models.loan import Emprunt
from app.models.book import Livre
from app.utils.database import obtenir_ou_404
from app.utils.error_handler import ErreurServeur
from datetime import datetime, timedelta

def envoyer_email(destinataire, sujet, corps_html, corps_texte=None):
    """Envoyer un email"""
    try:
        msg = Message(
            subject=sujet,
            recipients=[destinataire],
            html=corps_html,
            body=corps_texte or corps_html
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

def notifier_emprunt(emprunt_id):
    """Envoyer une notification d'emprunt"""
    # Obtenir l'emprunt
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    
    # Obtenir l'utilisateur et le livre
    utilisateur = obtenir_ou_404(Utilisateur, emprunt.utilisateur_id, "Utilisateur non trouvé")
    livre = obtenir_ou_404(Livre, emprunt.livre_id, "Livre non trouvé")
    
    # Préparer les données pour le template
    donnees = {
        'utilisateur': utilisateur,
        'livre': livre,
        'emprunt': emprunt
    }
    
    # Rendre le template
    corps_html = render_template('emails/emprunt_confirmation.html', **donnees)
    corps_texte = render_template('emails/emprunt_confirmation.txt', **donnees)
    
    # Envoyer l'email
    sujet = f"Confirmation d'emprunt - {livre.titre}"
    return envoyer_email(utilisateur.email, sujet, corps_html, corps_texte)

def notifier_rappel_retour(emprunt_id):
    """Envoyer un rappel de retour (3 jours avant échéance)"""
    # Obtenir l'emprunt
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    
    # Vérifier si l'emprunt est déjà retourné
    if emprunt.est_retourne():
        return False
    
    # Obtenir l'utilisateur et le livre
    utilisateur = obtenir_ou_404(Utilisateur, emprunt.utilisateur_id, "Utilisateur non trouvé")
    livre = obtenir_ou_404(Livre, emprunt.livre_id, "Livre non trouvé")
    
    # Préparer les données pour le template
    donnees = {
        'utilisateur': utilisateur,
        'livre': livre,
        'emprunt': emprunt,
        'jours_restants': 3
    }
    
    # Rendre le template
    corps_html = render_template('emails/rappel_retour.html', **donnees)
    corps_texte = render_template('emails/rappel_retour.txt', **donnees)
    
    # Envoyer l'email
    sujet = f"Rappel de retour - {livre.titre}"
    return envoyer_email(utilisateur.email, sujet, corps_html, corps_texte)

def notifier_retard(emprunt_id):
    """Envoyer une notification de retard"""
    # Obtenir l'emprunt
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    
    # Vérifier si l'emprunt est déjà retourné
    if emprunt.est_retourne():
        return False
    
    # Vérifier si l'emprunt est en retard
    if not emprunt.est_en_retard():
        return False
    
    # Obtenir l'utilisateur et le livre
    utilisateur = obtenir_ou_404(Utilisateur, emprunt.utilisateur_id, "Utilisateur non trouvé")
    livre = obtenir_ou_404(Livre, emprunt.livre_id, "Livre non trouvé")
    
    # Préparer les données pour le template
    donnees = {
        'utilisateur': utilisateur,
        'livre': livre,
        'emprunt': emprunt,
        'jours_retard': emprunt.jours_de_retard()
    }
    
    # Rendre le template
    corps_html = render_template('emails/notification_retard.html', **donnees)
    corps_texte = render_template('emails/notification_retard.txt', **donnees)
    
    # Envoyer l'email
    sujet = f"Retard de retour - {livre.titre}"
    return envoyer_email(utilisateur.email, sujet, corps_html, corps_texte)

def notifier_retour(emprunt_id):
    """Envoyer une notification de retour"""
    # Obtenir l'emprunt
    emprunt = obtenir_ou_404(Emprunt, emprunt_id, "Emprunt non trouvé")
    
    # Vérifier si l'emprunt est retourné
    if not emprunt.est_retourne():
        return False
    
    # Obtenir l'utilisateur et le livre
    utilisateur = obtenir_ou_404(Utilisateur, emprunt.utilisateur_id, "Utilisateur non trouvé")
    livre = obtenir_ou_404(Livre, emprunt.livre_id, "Livre non trouvé")
    
    # Préparer les données pour le template
    donnees = {
        'utilisateur': utilisateur,
        'livre': livre,
        'emprunt': emprunt
    }
    
    # Rendre le template
    corps_html = render_template('emails/confirmation_retour.html', **donnees)
    corps_texte = render_template('emails/confirmation_retour.txt', **donnees)
    
    # Envoyer l'email
    sujet = f"Confirmation de retour - {livre.titre}"
    return envoyer_email(utilisateur.email, sujet, corps_html, corps_texte)

def verifier_emprunts_a_rappeler():
    """Vérifier les emprunts qui nécessitent un rappel (3 jours avant échéance)"""
    # Calculer la date pour les rappels (emprunts qui expirent dans 3 jours)
    date_rappel = datetime.utcnow() + timedelta(days=3)
    
    # Trouver les emprunts qui expirent dans 3 jours et qui ne sont pas encore retournés
    emprunts = Emprunt.query.filter(
        Emprunt.date_retour_prevue >= date_rappel.replace(hour=0, minute=0, second=0),
        Emprunt.date_retour_prevue <= date_rappel.replace(hour=23, minute=59, second=59),
        Emprunt.date_retour_effective == None
    ).all()
    
    # Envoyer des rappels
    resultats = []
    for emprunt in emprunts:
        succes = notifier_rappel_retour(emprunt.id)
        resultats.append({
            'emprunt_id': emprunt.id,
            'succes': succes
        })
    
    return resultats

def verifier_emprunts_en_retard():
    """Vérifier les emprunts en retard"""
    # Obtenir la date actuelle
    maintenant = datetime.utcnow()
    
    # Trouver les emprunts en retard qui ne sont pas encore retournés
    emprunts = Emprunt.query.filter(
        Emprunt.date_retour_prevue < maintenant,
        Emprunt.date_retour_effective == None
    ).all()
    
    # Envoyer des notifications de retard
    resultats = []
    for emprunt in emprunts:
        succes = notifier_retard(emprunt.id)
        resultats.append({
            'emprunt_id': emprunt.id,
            'succes': succes
        })
    
    return resultats
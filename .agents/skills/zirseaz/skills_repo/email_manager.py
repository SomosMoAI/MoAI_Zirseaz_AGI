"""
Zirseaz Email Manager v2 — Envío de correos vía Gmail SMTP.
Usa env_loader centralizado.
"""
import os
import sys
import smtplib
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Asegurar imports desde utils/
_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

try:
    import env_loader
except ImportError:
    env_loader = None


def _get_email_credentials():
    """Obtiene credenciales de email usando env_loader centralizado."""
    if env_loader:
        email, password = env_loader.get_email_credentials()
        if email and password:
            return email, password
    
    # Fallback directo a os.environ si env_loader falla o no tiene las keys
    return os.environ.get("ZIRSEAZ_EMAIL"), os.environ.get("ZIRSEAZ_PASSWORD")


def send_email_to(recipient_email, subject, body):
    """
    Envía un correo electrónico.
    Requiere ZIRSEAZ_EMAIL y ZIRSEAZ_PASSWORD en .env o variables de entorno.
    """
    sender_email, sender_password = _get_email_credentials()
    
    if not sender_email or not sender_password:
        return "Error: Faltan credenciales ZIRSEAZ_EMAIL o ZIRSEAZ_PASSWORD en el entorno."
        
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        return f"Exito: Correo enviado a {recipient_email}."
    except Exception as e:
        # Error limpio para no inducir a error al LLM
        return f"Error SMTP: {str(e)}"


def get_unread_emails():
    """
    Lee correos no leídos de la bandeja de entrada.
    Retorna una lista de diccionarios con keys: num, from, subject, body.
    """
    sender_email, sender_password = _get_email_credentials()
    if not sender_email or not sender_password:
        return []
        
    emails = []
    try:
        # Conectar a IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(sender_email, sender_password)
        mail.select("inbox")
        
        # Buscar correos no leídos
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            return []
            
        for num in messages[0].split():
            # fetch marks as read by default
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue
                
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
                
            from_ = msg.get("From")
            
            # Obtener el cuerpo del correo
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode("utf-8")
                            break
                        except: pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode("utf-8")
                except: pass
                
            emails.append({
                "num": num.decode("utf-8"),
                "from": from_,
                "subject": subject,
                "body": body
            })
            
        mail.close()
        mail.logout()
        return emails
    except Exception as e:
        print(f"Error leyendo correos: {e}")
        return []

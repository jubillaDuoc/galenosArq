import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "botvachir00@gmail.com"
        self.smtp_password = "foevdrqxdykppiwv"

    def send_email(self, to_email, subject, body):
        try:
            # Crear el objeto MIMEText para el cuerpo del correo
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Iniciar una conexión SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)

            # Enviar el correo
            server.sendmail(self.smtp_username, to_email, msg.as_string())

            # Cerrar la conexión SMTP
            server.quit()
            return True
        except Exception as e:
            print(f"Error al enviar el correo: {str(e)}")
            return False

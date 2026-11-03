import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class NotificationService:
    """Envia e-mails via SMTP configurado por ambiente; sem SMTP_HOST apenas registra em log."""

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @classmethod
    def from_config(cls, config):
        return cls(config["SMTP_HOST"], config["SMTP_PORT"], config["SMTP_USER"], config["SMTP_PASSWORD"])

    def send_email(self, to, subject, body):
        if not self.host:
            logger.info("SMTP não configurado; e-mail para %s não enviado (%s)", to, subject)
            return False
        message = EmailMessage()
        message["Subject"], message["From"], message["To"] = subject, self.user, to
        message.set_content(body)
        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(message)
            logger.info("E-mail enviado para %s", to)
            return True
        except (OSError, smtplib.SMTPException) as err:
            logger.error("Erro ao enviar e-mail: %s", err)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        return self.send_email(user.email, subject, body)

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        return self.send_email(user.email, subject, body)

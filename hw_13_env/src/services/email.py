from src.services.auth import auth_service
from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
    USE_CREDENTIALS=config.USE_CREDENTIALS,
    VALIDATE_CERTS=config.VALIDATE_CERTS,
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
    
    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Include the username in the email message
    :param host: str: Pass the hostname of the website where your service is located
    :return: None
    :doc-author: Trelent
    """
    try:
        # Створення токену для підтвердження електронної пошти
        token_verification = auth_service.create_email_token({"sub": email})
        
        # Створення повідомлення з шаблоном для підтвердження адреси електронної пошти
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        # Відправлення повідомлення за допомогою FastMail
        fm = FastMail(conf)
        await fm.send_message(message, template_name="mail.html")
    except ConnectionErrors as err:
        # Обробка помилки під час відправлення повідомлення
        print(f"Error sending email: {err}")
        # Можна додати додаткові дії або відправити повідомлення адміністратору про помилку
        raise HTTPException(status_code=500, detail="Failed to send email. Please try again later.")
import logging

import environ
from django.core.management import BaseCommand

from config.settings import BASE_DIR
from users.models import User

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Создает суперпользователя с email и паролем из переменных окружения"

    def handle(self, *args, **options):
        email = env("SU_EMAIL", default=None)
        password = env("SU_PASS", default=None)

        if not email or not password:
            logger.error("SU_EMAIL и SU_PASS должны быть заданы в .env")
            return

        if not User.objects.filter(email=email).exists():
            user = User.objects.create(
                email=email,
                first_name="admin",
                last_name="adminych",
                is_staff=True,
                is_superuser=True,
            )

            user.set_password(password)
            user.save()
            logger.info(f"Суперпользователь {email} успешно создан")
        else:
            logger.warning(f"Суперпользователь с email {email} уже существует")

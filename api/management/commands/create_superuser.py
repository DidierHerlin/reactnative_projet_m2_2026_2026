from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crée un superuser automatiquement'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        email = "didierherlin18@gmail.com"  # changez ici
        password = "123456789"      # changez ici
        
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} créé avec succès'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {email} existe déjà'))
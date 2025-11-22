from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user if it does not exist'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        student_id = os.environ.get('ADMIN_STUDENT_ID', 'ADMIN001')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123')

        self.stdout.write(f'Attempting to create admin user with username: {username}, email: {email}')

        try:
            # Check if user exists by username or email
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User with username {username} already exists'))
                return
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'User with email {email} already exists'))
                return

            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                student_id=student_id,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {username} with email: {email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from core.models import SiteSettings

@receiver(post_migrate)
def create_initial_site_settings(sender, **kwargs):
    if sender.name == 'core' and not SiteSettings.objects.exists():
        SiteSettings.objects.create()
        print("Создана начальная запись SiteSettings.")
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from store.models import Customer


@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_customer_based_on_customuser(sender,**kwargs):
    created = kwargs['created']
    if created:
        Customer.objects.create(user=kwargs['instance'])


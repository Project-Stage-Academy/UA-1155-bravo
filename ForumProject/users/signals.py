# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import CustomUser, UserRoleCompany

# @receiver(post_save, sender=CustomUser)
# def create_user_role_company(sender, instance, created, **kwargs):
#     if created:
#         UserRoleCompany.objects.create(user=instance, role=UserRoleCompany.Role.UNDEFINED)

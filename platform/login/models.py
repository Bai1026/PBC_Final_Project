# login/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# whenever change the models.py, we should make the migration and migrate
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nation = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    exchange_school = models.CharField(max_length=100, blank=True, null=True)
    # date = models.DateField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True, null=True)

    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    other_social_media = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class HiddenProfile(models.Model):
    user = models.ForeignKey(User, related_name='hiding_user', on_delete=models.CASCADE)
    hidden_user = models.ForeignKey(UserProfile, related_name='hidden_profile', on_delete=models.CASCADE)
    hide_count = models.IntegerField(default=1)  # Tracks how often a profile has been hidden

    # Max part
    is_deleted = models.BooleanField(default=False)  # 確保這個欄位存在

    class Meta:
        unique_together = ('user', 'hidden_user')  # Ensures uniqueness
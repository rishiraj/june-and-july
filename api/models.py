# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Q

class User(AbstractUser):
    # Add any additional user fields if needed, e.g., date_of_birth
    date_of_birth = models.DateField(null=True, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    # Location, preferences etc. would go here

    def __str__(self):
        return self.user.username

    @property
    def swipe_ratio(self):
        """Calculates Right Swipes / Total Swipes Sent."""
        swipes_sent = self.user.sent_swipes.all()
        total_sent = swipes_sent.count()
        if total_sent == 0:
            return None # Or 0.0, depending on how you want to display it

        right_swipes_sent = swipes_sent.filter(direction='right').count()
        return round((right_swipes_sent / total_sent) * 100)

    @property
    def acceptance_ratio(self):
        """Calculates (Matches / Right Swipes Received) * 100."""
        right_swipes_received = self.user.received_swipes.filter(direction='right')
        total_received = right_swipes_received.count()
        if total_received == 0:
            return None # Or 0.0

        # A match is formed when the other user also swiped right.
        # We find how many of the people who swiped right on us, we also swiped right on.
        accepted_swipes = 0
        for swipe in right_swipes_received:
            # Check if WE swiped right on the person who swiped right on US
            if Swipe.objects.filter(swiper=self.user, swiped=swipe.swiper, direction='right').exists():
                accepted_swipes += 1

        return round((accepted_swipes / total_received) * 100)


class Photo(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='profile_photos/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Swipe(models.Model):
    DIRECTIONS = (('left', 'Left'), ('right', 'Right'))
    swiper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_swipes')
    swiped = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_swipes')
    direction = models.CharField(max_length=5, choices=DIRECTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper', 'swiped') # A user can only swipe on another user once

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches2')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

# After defining models, run migrations
# python manage.py makemigrations
# python manage.py migrate

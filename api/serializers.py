# api/serializers.py

from rest_framework import serializers
from .models import User, Profile, Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['image', 'order']

class ProfileSerializer(serializers.ModelSerializer):
    # Make the @property fields from the model available in the API
    swipe_ratio = serializers.IntegerField(read_only=True)
    acceptance_ratio = serializers.IntegerField(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    
    # Get user's first name and age
    first_name = serializers.CharField(source='user.first_name')
    # age = serializers.SerializerMethodField() # You would calculate age from date_of_birth

    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'bio', 'job_title', 'company', 
            'photos', 'swipe_ratio', 'acceptance_ratio'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']

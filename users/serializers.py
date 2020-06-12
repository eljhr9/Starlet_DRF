from rest_framework import serializers
from django.conf import settings
from .models import User



class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        # model = settings.AUTH_USER_MODEL
        model = User
        fields = ('username',)

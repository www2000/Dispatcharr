from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import User


# 🔹 Fix for Permission serialization
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


# 🔹 Fix for Group serialization
class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all()
    )  # ✅ Fixes ManyToManyField `_meta` error

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


# 🔹 Fix for User serialization
class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, queryset=Group.objects.all(), slug_field="name"
    )  # ✅ Fix ManyToMany `_meta` error

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']

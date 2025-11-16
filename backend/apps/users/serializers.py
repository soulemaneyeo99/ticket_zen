"""
Serializers pour l'authentification et gestion des utilisateurs
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.companies.models import Company


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un utilisateur"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'role'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validation des données"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        
        # Validation du rôle (seul voyageur et compagnie peuvent s'inscrire)
        if attrs.get('role') not in [User.VOYAGEUR, User.COMPAGNIE]:
            raise serializers.ValidationError({
                'role': 'Rôle invalide pour l\'inscription.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Valider les credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError('Email ou mot de passe incorrect.')
        
        if not user.is_active:
            raise serializers.ValidationError('Ce compte est désactivé.')
        
        attrs['user'] = user
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un utilisateur"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'role_display', 'is_active',
            'is_verified', 'company', 'company_name', 'avatar',
            'created_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'created_at', 'last_login', 'full_name',
            'role_display', 'company_name'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'avatar'
        ]
    
    def validate_phone_number(self, value):
        """Vérifier l'unicité du téléphone"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(phone_number=value).exists():
            raise serializers.ValidationError('Ce numéro de téléphone est déjà utilisé.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Vérifier l'ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mot de passe actuel incorrect.')
        return value
    
    def validate(self, attrs):
        """Valider la confirmation du nouveau mot de passe"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return attrs
    
    def save(self):
        """Changer le mot de passe"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    """Serializer pour les tokens JWT"""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserDetailSerializer()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste d'utilisateurs"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'role', 'role_display', 'is_active', 'created_at'
        ]
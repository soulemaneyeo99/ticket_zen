"""
Views pour l'authentification et gestion des utilisateurs
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.users.models import User
from apps.users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    TokenSerializer,
    UserListSerializer
)
from apps.users.permissions import IsAdminGlobal, IsOwnerOrAdmin
from apps.logs.models import ActivityLog
from utils.pagination import StandardResultsSetPagination

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet pour l'authentification"""
    
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """Inscription d'un nouvel utilisateur"""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            
            # Logger l'inscription (skip for SQLite due to JSONField issues)
            try:
                ActivityLog.objects.create(
                    user=user,
                    action=ActivityLog.USER_REGISTER,
                    description=f"Inscription réussie : {user.email}",
                    details={
                        'user_id': str(user.id),
                        'role': user.role,
                        'email': user.email
                    },
                    content_type='User',
                    object_id=str(user.id),
                    severity=ActivityLog.SEVERITY_INFO,
                    ip_address=self.get_client_ip(request)
                )
            except Exception as e:
                # Ignore logging errors for SQLite compatibility
                pass
            
            return Response({
                'message': 'Inscription réussie',
                'user': UserDetailSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """Connexion d'un utilisateur"""
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Mettre à jour last_login et IP
            user.last_login = timezone.now()
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login', 'last_login_ip'])
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            
            # Logger la connexion (skip for SQLite due to JSONField issues)
            try:
                ActivityLog.objects.create(
                    user=user,
                    action=ActivityLog.USER_LOGIN,
                    description=f"Connexion réussie : {user.email}",
                    details={
                        'user_id': str(user.id),
                        'role': user.role,
                        'email': user.email
                    },
                    content_type='User',
                    object_id=str(user.id),
                    severity=ActivityLog.SEVERITY_INFO,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception:
                # Ignore logging errors for SQLite compatibility
                pass
            
            return Response({
                'message': 'Connexion réussie',
                'user': UserDetailSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        """Rafraîchir le token d'accès"""
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Token invalide ou expiré'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Déconnexion d'un utilisateur"""
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Logger la déconnexion
            ActivityLog.objects.create(
                user=request.user,
                action=ActivityLog.USER_LOGOUT,
                description=f"Déconnexion : {request.user.email}",
                details={'user_id': str(request.user.id)},
                content_type='User',
                object_id=str(request.user.id),
                severity=ActivityLog.SEVERITY_INFO,
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'message': 'Déconnexion réussie'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def get_client_ip(request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Retourner le serializer approprié selon l'action"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        """Filtrer les utilisateurs selon le rôle"""
        queryset = super().get_queryset()
        
        # Les admins voient tous les utilisateurs
        if self.request.user.role == 'admin':
            return queryset
        
        # Les compagnies voient leurs embarqueurs
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(
                company=self.request.user.company,
                role='embarqueur'
            )
        
        # Les autres ne voient que leur propre profil
        return queryset.filter(id=self.request.user.id)
    
    def get_permissions(self):
        """Permissions dynamiques selon l'action"""
        if self.action in ['create', 'destroy']:
            return [IsAdminGlobal()]
        elif self.action in ['update', 'partial_update']:
            return [IsOwnerOrAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Récupérer le profil de l'utilisateur connecté"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], url_path='update-profile')
    def update_profile(self, request):
        """Mettre à jour le profil de l'utilisateur connecté"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Logger la modification
            ActivityLog.objects.create(
                user=request.user,
                action=ActivityLog.USER_UPDATE,
                description=f"Mise à jour du profil : {request.user.email}",
                details={
                    'user_id': str(request.user.id),
                    'updated_fields': list(serializer.validated_data.keys())
                },
                content_type='User',
                object_id=str(request.user.id),
                severity=ActivityLog.SEVERITY_INFO,
                ip_address=AuthViewSet.get_client_ip(request)
            )
            
            return Response({
                'message': 'Profil mis à jour avec succès',
                'user': UserDetailSerializer(request.user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """Changer le mot de passe"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Logger le changement de mot de passe
            ActivityLog.objects.create(
                user=request.user,
                action=ActivityLog.USER_UPDATE,
                description=f"Changement de mot de passe : {request.user.email}",
                details={'user_id': str(request.user.id)},
                content_type='User',
                object_id=str(request.user.id),
                severity=ActivityLog.SEVERITY_INFO,
                ip_address=AuthViewSet.get_client_ip(request)
            )
            
            return Response({
                'message': 'Mot de passe changé avec succès'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='toggle-status', permission_classes=[IsAdminGlobal])
    def toggle_status(self, request, pk=None):
        """Activer/Désactiver un utilisateur (admin seulement)"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        # Logger l'action
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.ADMIN_ACTION,
            description=f"{'Activation' if user.is_active else 'Désactivation'} utilisateur : {user.email}",
            details={
                'target_user_id': str(user.id),
                'is_active': user.is_active
            },
            content_type='User',
            object_id=str(user.id),
            severity=ActivityLog.SEVERITY_WARNING,
            ip_address=AuthViewSet.get_client_ip(request)
        )
        
        return Response({
            'message': f"Utilisateur {'activé' if user.is_active else 'désactivé'} avec succès",
            'user': UserDetailSerializer(user).data
        })
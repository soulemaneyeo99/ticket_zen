"""
Serializers pour les réclamations
"""
from rest_framework import serializers
from apps.claims.models import Claim, ClaimMessage


class ClaimCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une réclamation"""
    
    class Meta:
        model = Claim
        fields = [
            'category', 'subject', 'description', 'ticket',
            'trip', 'attachment_1', 'attachment_2', 'attachment_3',
            'priority'
        ]
    
    def create(self, validated_data):
        """Créer une réclamation"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        
        claim = Claim.objects.create(**validated_data)
        return claim


class ClaimDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une réclamation"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    response_time = serializers.DurationField(read_only=True)
    
    class Meta:
        model = Claim
        fields = [
            'id', 'user', 'user_full_name', 'user_email', 'ticket',
            'trip', 'assigned_to', 'assigned_to_name', 'category',
            'category_display', 'subject', 'description',
            'attachment_1', 'attachment_2', 'attachment_3',
            'status', 'status_display', 'priority', 'priority_display',
            'admin_response', 'resolution_notes', 'is_open',
            'response_time', 'created_at', 'updated_at',
            'resolved_at', 'closed_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_full_name', 'user_email',
            'category_display', 'status_display', 'priority_display',
            'assigned_to_name', 'is_open', 'response_time',
            'created_at', 'updated_at', 'resolved_at', 'closed_at'
        ]


class ClaimUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une réclamation (admin)"""
    
    class Meta:
        model = Claim
        fields = [
            'status', 'priority', 'assigned_to', 'admin_response',
            'resolution_notes'
        ]


class ClaimListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de réclamations"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Claim
        fields = [
            'id', 'user_email', 'category', 'category_display',
            'subject', 'status', 'status_display', 'priority',
            'priority_display', 'created_at'
        ]


class ClaimMessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages d'une réclamation"""
    
    sender_full_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.get_role_display', read_only=True)
    
    class Meta:
        model = ClaimMessage
        fields = [
            'id', 'claim', 'sender', 'sender_full_name', 'sender_role',
            'message', 'is_internal', 'attachment', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'sender_full_name', 'sender_role', 'created_at']
    
    def create(self, validated_data):
        """Créer un message"""
        request = self.context.get('request')
        validated_data['sender'] = request.user
        
        message = ClaimMessage.objects.create(**validated_data)
        return message
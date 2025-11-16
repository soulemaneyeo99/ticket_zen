"""
Serializers pour les notifications
"""
from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une notification"""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'notification_type', 'category', 'title',
            'message', 'html_content', 'metadata', 'action_url',
            'recipient_email', 'recipient_phone', 'scheduled_at'
        ]
    
    def validate(self, attrs):
        """Validations"""
        notification_type = attrs.get('notification_type')
        
        # Vérifier email pour notifications email
        if notification_type == Notification.EMAIL:
            if not attrs.get('recipient_email') and not attrs.get('user'):
                raise serializers.ValidationError({
                    'recipient_email': 'Email requis pour les notifications email.'
                })
        
        # Vérifier téléphone pour notifications SMS
        if notification_type == Notification.SMS:
            if not attrs.get('recipient_phone') and not attrs.get('user'):
                raise serializers.ValidationError({
                    'recipient_phone': 'Téléphone requis pour les notifications SMS.'
                })
        
        return attrs


class NotificationDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une notification"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_read = serializers.BooleanField(read_only=True)
    can_retry = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'notification_type_display',
            'category', 'category_display', 'title', 'message',
            'html_content', 'metadata', 'action_url', 'status',
            'status_display', 'is_read', 'can_retry', 'recipient_email',
            'recipient_phone', 'sent_at', 'read_at', 'attempts',
            'max_attempts', 'error_message', 'scheduled_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'notification_type_display', 'category_display',
            'status_display', 'is_read', 'can_retry', 'sent_at',
            'read_at', 'attempts', 'created_at', 'updated_at'
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de notifications"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_read = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'category', 'category_display', 'title', 'message',
            'action_url', 'is_read', 'created_at'
        ]


class NotificationMarkAsReadSerializer(serializers.Serializer):
    """Serializer pour marquer une notification comme lue"""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False
    )
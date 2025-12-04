"""
Serializers pour les logs d'activité
"""
from rest_framework import serializers
from apps.logs.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer pour les logs d'activité (lecture seule)"""
    
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'action',
            'action_display', 'description', 'details', 'ip_address',
            'user_agent', 'content_type', 'object_id', 'severity',
            'severity_display', 'tags', 'created_at'
        ]
        read_only_fields = '__all__'  # Tous les champs en lecture seule


class ActivityLogCreateSerializer(serializers.Serializer):
    """Serializer pour créer un log (utilisé en interne)"""
    
    action = serializers.ChoiceField(choices=ActivityLog.ACTION_CHOICES, required=True)
    description = serializers.CharField(required=True)
    details = serializers.JSONField(required=False, default=dict)
    content_type = serializers.CharField(required=False, allow_blank=True)
    object_id = serializers.CharField(required=False, allow_blank=True)
    severity = serializers.ChoiceField(
        choices=ActivityLog.SEVERITY_CHOICES,
        default=ActivityLog.SEVERITY_INFO
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
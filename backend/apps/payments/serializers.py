"""
Serializers pour les paiements
"""
from rest_framework import serializers
from apps.payments.models import Payment


class PaymentInitSerializer(serializers.Serializer):
    """Serializer pour initialiser un paiement"""
    
    ticket_id = serializers.UUIDField(required=True)
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        required=True
    )
    phone_number = serializers.CharField(
        required=False,
        max_length=17,
        help_text='Obligatoire pour mobile money'
    )
    
    def validate(self, attrs):
        """Validations"""
        # Vérifier que le numéro de téléphone est fourni pour mobile money# Vérifier que le numéro de téléphone est fourni pour mobile money
        payment_method = attrs.get('payment_method')
        mobile_money_methods = [
            Payment.ORANGE_MONEY,
            Payment.MTN_MONEY,
            Payment.MOOV_MONEY,
            Payment.WAVE
        ]
        
        if payment_method in mobile_money_methods and not attrs.get('phone_number'):
            raise serializers.ValidationError({
                'phone_number': 'Le numéro de téléphone est obligatoire pour mobile money.'
            })
        
        return attrs


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un paiement"""
    
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'user', 'user_email', 'trip',
            'company', 'company_name', 'amount', 'platform_commission',
            'company_amount', 'payment_method', 'payment_method_display',
            'phone_number', 'status', 'status_display', 'is_successful',
            'is_pending', 'can_be_refunded', 'provider_transaction_id',
            'payment_url', 'refund_transaction_id', 'refund_amount',
            'refund_reason', 'refunded_at', 'created_at', 'updated_at',
            'completed_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'user_email', 'company_name',
            'platform_commission', 'company_amount', 'status_display',
            'is_successful', 'is_pending', 'can_be_refunded',
            'provider_transaction_id', 'payment_url', 'created_at',
            'updated_at', 'completed_at'
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de paiements"""
    
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'user_email', 'amount',
            'payment_method', 'payment_method_display', 'status',
            'status_display', 'created_at'
        ]


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer pour le webhook CinetPay"""
    
    cpm_trans_id = serializers.CharField(required=True)
    cpm_site_id = serializers.CharField(required=True)
    cpm_trans_status = serializers.CharField(required=True)
    cpm_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    cpm_currency = serializers.CharField(required=False)
    cpm_payid = serializers.CharField(required=False)
    cpm_payment_date = serializers.CharField(required=False)
    cpm_payment_time = serializers.CharField(required=False)
    cpm_error_message = serializers.CharField(required=False, allow_blank=True)
    signature = serializers.CharField(required=False)
    payment_method = serializers.CharField(required=False)
    cel_phone_num = serializers.CharField(required=False)
    cpm_phone_prefixe = serializers.CharField(required=False)
    cpm_language = serializers.CharField(required=False)
    cpm_version = serializers.CharField(required=False)
    cpm_payment_config = serializers.CharField(required=False)
    cpm_page_action = serializers.CharField(required=False)
    cpm_custom = serializers.CharField(required=False)
    cpm_designation = serializers.CharField(required=False)
    buyer_name = serializers.CharField(required=False)


class PaymentRefundSerializer(serializers.Serializer):
    """Serializer pour rembourser un paiement"""
    
    refund_reason = serializers.CharField(required=True, max_length=500)
    refund_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    
    def validate(self, attrs):
        """Validations"""
        payment = self.context.get('payment')
        
        # Vérifier que le paiement peut être remboursé
        if not payment.can_be_refunded:
            raise serializers.ValidationError('Ce paiement ne peut pas être remboursé.')
        
        # Si montant non spécifié, remboursement total
        if not attrs.get('refund_amount'):
            attrs['refund_amount'] = payment.amount
        
        # Vérifier que le montant ne dépasse pas le montant initial
        if attrs['refund_amount'] > payment.amount:
            raise serializers.ValidationError({
                'refund_amount': 'Le montant du remboursement ne peut pas dépasser le montant initial.'
            })
        
        return attrs
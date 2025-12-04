import { apiPost, apiGet } from '@/lib/api';
import { PaymentInitiatePayload, PaymentResponse } from '@/types/api';

export const paymentsService = {
  initiate: (payload: PaymentInitiatePayload) =>
    apiPost<PaymentResponse>('/payments/initiate/', payload),

  checkStatus: (transactionId: string) =>
    apiGet<PaymentResponse>(`/payments/check_status/?transaction_id=${transactionId}`),
};
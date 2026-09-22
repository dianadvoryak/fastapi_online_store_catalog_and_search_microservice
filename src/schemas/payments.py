import enum
from decimal import Decimal

from pydantic import BaseModel


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class WebhookWebhookPayload(BaseModel):
    transaction_id: str  # Тот самый external_id
    order_id: str
    amount: Decimal
    status: PaymentStatus


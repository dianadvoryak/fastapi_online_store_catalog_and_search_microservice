from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.payments import WebhookWebhookPayload
from src.services.payment_service import PaymentService
from src.core.db import get_async_session

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post("/webhook")
async def payment(payload: WebhookWebhookPayload, db: AsyncSession = Depends(get_async_session)):
    # Контроллер просто делегирует задачу сервису
    service = PaymentService(db)
    return await service.handle_payment_webhook(payload)

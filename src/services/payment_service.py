from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.payment import Payment, PaymentStatus
from src.schemas.payments import WebhookWebhookPayload


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_payment_webhook(self, payload: WebhookWebhookPayload):
        """
        Эндпоинт для приема уведомлений об оплате от стороннего сервиса.
        Защищен от дубликатов, смены порядка и гонок данных.
        """
        # 1. Блокируем строку с этим external_id в базе данных для текущей транзакции.
        # Если прилетит второй такой же запрос параллельно, он будет ждать на этой строке.
        query = (
            select(Payment)
            .where(Payment.external_id == payload.transaction_id)
            .with_for_update()  # <--- Пессимистичная блокировка строки (FOR UPDATE)
        )
        result = await self.db.execute(query)
        existing_payment = result.scalar_one_or_none()

        # 2. Если платеж уже существует в базе
        if existing_payment:
            # Сценарий А: Дубликат. Платеж уже успешно обработан.
            if existing_payment.status == PaymentStatus.SUCCESS:
                # Возвращаем 200 OK, чтобы сторонний сервис отстал от нас. Ничего не меняем.
                return {"status": "already_processed", "detail": "Payment was already successful"}

            # Сценарий Б: Запросы пришли не по порядку.
            # Если статус в базе PENDING (ожидание), а прилетел SUCCESS или FAILED — обновляем.
            if existing_payment.status == PaymentStatus.PENDING and payload.status != PaymentStatus.PENDING:
                existing_payment.status = payload.status
                await self.db.commit()
                # ИСПРАВЛЕНИЕ: Если статус изменился на SUCCESS, активируем заказ!
                if existing_payment.status == PaymentStatus.SUCCESS:
                    await self._activate_order(existing_payment.order_id)

                return {"status": "updated", "new_status": payload.status}

            # Если прилетел статус PENDING, а в базе уже лежит финальный статус — просто игнорируем
            return {"status": "ignored", "detail": "Older status update ignored"}

        # 3. Сценарий В: Платежа еще нет в базе (первый раз пришел запрос)
        new_payment = Payment(
            external_id=payload.transaction_id,
            order_id=payload.order_id,
            amount=payload.amount,
            status=payload.status
        )
        self.db.add(new_payment)

        try:
            await self.db.commit()
        except Exception:
            # Исправление: если произошла гонка при создании, откатываемся
            await self.db.rollback()
            # Для платежной системы мы возвращаем статус, как будто всё ок,
            # так как параллельный запрос прямо сейчас успешно создал эту запись.
            return {"status": "already_processed", "detail": "Payment processed by concurrent request"}

        # Если платеж сразу пришел со статусом SUCCESS — активируем заказ
        if new_payment.status == PaymentStatus.SUCCESS:
            await self._activate_order(new_payment.order_id)

        return {"status": "created", "payment_id": str(new_payment.id)}

    async def _activate_order(self, order_id: str):
        """Внутренний асинхронный метод для выполнения бизнес-логики после оплаты."""
        print(f"Заказ {order_id} успешно оплачен! Активируем подписку/отгружаем товар...")
        # Сюда вставляйте вызовы других сервисов, отправку ивентов в RabbitMQ/Kafka и т.д.
        # await self.order_service.mark_as_paid(order_id)
        pass


from decimal import Decimal
from payment_engine import PaymentEngine
from payment_schema import Money, PaymentStatus, WebhookEvent, OrderStatus, WebhookProcessingStatus


def test_create_order():
    engine = PaymentEngine()
    order = engine.create_order("u1", "product_99", Money("THB", Decimal("99")))
    assert order.user_id == "u1"
    assert order.status == OrderStatus.PENDING


def test_successful_payment_marks_order_paid():
    engine = PaymentEngine()
    order = engine.create_order("u1", "product_99", Money("THB", Decimal("99")))
    payment = engine.attach_payment(order.order_id, "test", "provider-pay-1", PaymentStatus.PENDING)
    assert payment.status == PaymentStatus.PENDING
    event = WebhookEvent("evt-1", "test", "payment.succeeded", "provider-pay-1", {})
    result = engine.process_webhook(event)
    assert result.status == WebhookProcessingStatus.PROCESSED
    assert engine.store.orders[order.order_id].status == OrderStatus.PAID


def test_duplicate_webhook_is_idempotent():
    engine = PaymentEngine()
    order = engine.create_order("u1", "product_99", Money("THB", Decimal("99")))
    engine.attach_payment(order.order_id, "test", "provider-pay-1", PaymentStatus.PENDING)
    event = WebhookEvent("evt-dup", "test", "payment.succeeded", "provider-pay-1", {})
    first = engine.process_webhook(event)
    second = engine.process_webhook(event)
    assert first is second
    assert engine.store.orders[order.order_id].status == OrderStatus.PAID


def test_unknown_payment_does_not_create_entitlement_side_effects():
    engine = PaymentEngine()
    event = WebhookEvent("evt-unknown", "test", "payment.succeeded", "missing", {})
    result = engine.process_webhook(event)
    assert result.status == WebhookProcessingStatus.IGNORED
    assert result.error_code == "payment_not_found"


def test_failed_payment_marks_order_failed():
    engine = PaymentEngine()
    order = engine.create_order("u1", "product_599", Money("THB", Decimal("599")))
    engine.attach_payment(order.order_id, "test", "provider-pay-2", PaymentStatus.PENDING)
    event = WebhookEvent("evt-fail", "test", "payment.failed", "provider-pay-2", {})
    engine.process_webhook(event)
    assert engine.store.orders[order.order_id].status == OrderStatus.FAILED

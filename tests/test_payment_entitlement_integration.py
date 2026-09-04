from decimal import Decimal
from uuid import uuid4

from membership_schema import MembershipState
from payment_entitlement_integration import (
    grant_after_successful_payment,
    revoke_after_refund,
)
from payment_schema import Money, OrderStatus, PaymentStatus, Order, Payment


def make_paid_pair(product_id="personal_insight_99"):
    user_id = uuid4()
    order = Order(
        order_id="ord_test_1",
        user_id=str(user_id),
        product_id=product_id,
        amount=Money("THB", Decimal("99")),
        status=OrderStatus.PAID,
    )
    payment = Payment(
        payment_id="pay_test_1",
        order_id=order.order_id,
        user_id=order.user_id,
        provider="test",
        provider_payment_id="prov_1",
        amount=order.amount,
        status=PaymentStatus.SUCCEEDED,
    )
    return user_id, order, payment


def test_successful_payment_grants_membership_once():
    user_id, order, payment = make_paid_pair()
    state = MembershipState(user_id=user_id)

    first = grant_after_successful_payment(state, order, payment)
    second = grant_after_successful_payment(state, order, payment)

    assert first.action == "granted"
    assert second.action == "already_granted"
    assert len(state.grants) == 1
    assert state.has_product("personal_insight_99") is True


def test_refund_revokes_only_linked_grant():
    user_id, order, payment = make_paid_pair()
    state = MembershipState(user_id=user_id)
    grant_after_successful_payment(state, order, payment)

    payment.status = PaymentStatus.REFUNDED
    order.status = OrderStatus.REFUNDED
    result = revoke_after_refund(state, order, payment)

    assert result.action == "revoked"
    assert state.has_product("personal_insight_99") is False
    assert state.grants[0].external_reference == "order:ord_test_1"


def test_refund_does_not_revoke_another_purchase_of_same_product():
    user_id = uuid4()
    state = MembershipState(user_id=user_id)

    order1 = Order("ord_1", str(user_id), "personal_insight_99", Money("THB", Decimal("99")), OrderStatus.PAID)
    pay1 = Payment("pay_1", "ord_1", str(user_id), "test", "prov_1", order1.amount, PaymentStatus.SUCCEEDED)
    order2 = Order("ord_2", str(user_id), "personal_insight_99", Money("THB", Decimal("99")), OrderStatus.PAID)
    pay2 = Payment("pay_2", "ord_2", str(user_id), "test", "prov_2", order2.amount, PaymentStatus.SUCCEEDED)

    grant_after_successful_payment(state, order1, pay1)
    grant_after_successful_payment(state, order2, pay2)

    pay1.status = PaymentStatus.REFUNDED
    order1.status = OrderStatus.REFUNDED
    revoke_after_refund(state, order1, pay1)

    assert state.has_product("personal_insight_99") is True
    assert len([g for g in state.grants if g.status == "active"]) == 1


def test_mismatched_user_is_rejected():
    user_id, order, payment = make_paid_pair()
    state = MembershipState(user_id=uuid4())
    try:
        grant_after_successful_payment(state, order, payment)
        assert False
    except ValueError as exc:
        assert "user" in str(exc)

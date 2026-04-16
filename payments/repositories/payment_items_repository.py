from decimal import Decimal

from payments.models import PaymentItem, PaymentSession

class PaymentItemRepository:
    def bulk_create(self, session: PaymentSession, items: list[dict]):
        items_to_create = []
        total = Decimal("0.00")

        for item in items:
            price_str = str(item['product_price']).strip()
            price = Decimal(price_str)
            quantity = int(item['quantity'])
            line_total = price * quantity
            total += line_total
            items_to_create.append(
                PaymentItem(
                    session=session,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    unit_price=price,
                    quantity=quantity,
                )
            )

        PaymentItem.objects.bulk_create(items_to_create)
        return total
        
    def delete_by_session(self, session):
        session.items.all().delete()
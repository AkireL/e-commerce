class PaidOrderService:

    def __init__(self, order_repository):
        self.order_repository = order_repository

    def mark_as_paid(self, order_id):
        order = self.order_repository.get_order_by_id(order_id)
        
        if order is None or order.is_active:
            return False
        return self.order_repository.mark_as_paid(order_id)
class PaidOrderService:

    def __init__(self, order_repository):
        self.order_repository = order_repository

    def mark_as_paid(self, order_id):
        return self.order_repository.mark_as_paid(order_id)
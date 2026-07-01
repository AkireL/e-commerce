class OrderDomainError(Exception):
    pass


class ItemNotAvailableError(OrderDomainError):
    pass


class InsufficientStockError(OrderDomainError):
    pass


class ItemNotFoundError(OrderDomainError):
    pass

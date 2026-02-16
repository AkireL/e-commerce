class PaymentError(Exception):
    """Errores relacionados con el flujo de pagos simulados."""


class EmptyOrderError(PaymentError):
    """La orden no tiene artículos y no puede procesarse."""


class ActiveSessionExistsError(PaymentError):
    """Ya existe una sesión de pago pendiente para esta orden."""

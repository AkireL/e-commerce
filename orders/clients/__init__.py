from typing import Protocol


class ProductsClientProtocol(Protocol):
    def get_products_available(self) -> list: ...
    
    def get_products_info(self, product_ids: list[int]) -> dict: ...
    
    def get_products_stock(self, product_ids: list[int]) -> dict: ...


class PaymentsClientProtocol(Protocol):
    def invalidate_payment_sessions(self, order_id: int) -> dict: ...
    
    def get_payment_completed_session(self, token: str, user_id: int) -> dict | None: ...


class ProductsClient:
    def get_products_available(self) -> list:
        from orders.http_client import get_products_available
        return get_products_available()
    
    def get_products_info(self, product_ids: list[int]) -> dict:
        from orders.http_client import get_products_info
        return get_products_info(product_ids)
    
    def get_products_stock(self, product_ids: list[int]) -> dict:
        from orders.http_client import get_products_stock
        return get_products_stock(product_ids)


class PaymentsClient:
    def invalidate_payment_sessions(self, order_id: int) -> dict:
        from orders.http_client import invalidate_payment_sessions
        return invalidate_payment_sessions(order_id)
    
    def get_payment_completed_session(self, token: str, user_id: int) -> dict | None:
        from orders.http_client import get_payment_completed_session
        return get_payment_completed_session(token, user_id)


class MockProductsClient:
    def __init__(self):
        self._products_available = []
        self._products_info = {}
        self._products_stock = {}
    
    def set_products_available(self, products: list):
        self._products_available = products
    
    def set_products_info(self, products_info: dict):
        self._products_info = products_info
    
    def set_products_stock(self, products_stock: dict):
        self._products_stock = products_stock
    
    def get_products_available(self) -> list:
        return self._products_available
    
    def get_products_info(self, product_ids: list[int]) -> dict:
        return {str(k): v for k, v in self._products_info.items() if k in product_ids}
    
    def get_products_stock(self, product_ids: list[int]) -> dict:
        return {str(k): v for k, v in self._products_stock.items() if k in product_ids}


class MockPaymentsClient:
    def __init__(self):
        self._invalidate_calls = []
        self._sessions = {}
    
    def set_payment_session(self, token: str, session: dict):
        self._sessions[token] = session
    
    def invalidate_payment_sessions(self, order_id: int) -> dict:
        self._invalidate_calls.append(order_id)
        return {"success": True}
    
    def get_payment_completed_session(self, token: str, user_id: int) -> dict | None:
        return self._sessions.get(token)
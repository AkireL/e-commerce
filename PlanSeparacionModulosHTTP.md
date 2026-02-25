# Plan de Separación de Módulos vía HTTP

## Objetivo

Eliminar cualquier importación cruzada entre módulos mediante comunicación HTTP interna:
- `orders/` no importa de `payments/` ni `products/`
- `payments/` no importa de `orders/` ni `products/`
- `products/` no importa de ningún otro módulo

---

## Decisiones Tomadas

| Aspecto | Decisión | Razón |
|---------|----------|-------|
| Framework | JsonResponse (vistas Django) | Simple, sin dependencias extra, ya se usa en el proyecto |
| Flujo de datos | Orders tiene snapshots, solo consulta HTTP para stock y foto | Los snapshots ya tienen product_id, product_name, product_price |
| Autenticación | Sin autenticación | Simple para empezar, pendiente mejora futura |
| URLs | `/orders/api/...`, `/payments/api/...`, `/products/api/...` | Dentro del módulo, fácil de identificar |
| Cliente HTTP | urllib de Django (interno) | Sin dependencias externas, rápido, interno al servidor |
| Transacciones | No crítico | Aceptable inconsistencia temporal, pendiente mejora |
| Paso de datos | Vista envía datos necesarios en la llamada HTTP | Evita consultas adicionales |

---

## Endpoints a Crear por Módulo

### products/ - Endpoints que expone

| Endpoint | Método | Descripción | Parámetros | Retorno |
|----------|--------|-------------|------------|---------|
| `/products/api/products-info/` | POST | Obtener info de múltiples productos | `{"product_ids": [1, 2, 3]}` | `{"products": {1: {...}, 2: {...}}}` |
| `/products/api/product-stock/` | POST | Obtener stock actual de productos | `{"product_ids": [1, 2, 3]}` | `{"stocks": {1: 10, 2: 5}}` |

### orders/ - Endpoints que expone

| Endpoint | Método | Descripción | Parámetros | Retorno |
|----------|--------|-------------|------------|---------|
| `/orders/api/order/<int:order_id>/` | GET | Obtener info de una orden | - | `{"order": {...}}` |
| `/orders/api/order/<int:order_id>/mark-paid/` | POST | Marcar orden como pagada | - | `{"success": true}` |

### payments/ - Endpoints que expone

| Endpoint | Método | Descripción | Parámetros | Retorno |
|----------|--------|-------------|------------|---------|
| `/payments/api/invalidate-sessions/` | POST | Invalidar sesiones pendientes | `{"order_id": 1}` | `{"deleted": 2}` |

---

## Módulos que Consumen Endpoints

| Módulo | Endpoint que consume | Motivo |
|--------|---------------------|--------|
| `orders/views.py` | `/products/api/products-info/` | Obtener stock y foto para mostrar en carrito |
| `orders/views.py` | `/products/api/product-stock/` | Validar stock al actualizar cantidad |
| `orders/views.py` | `/payments/api/invalidate-sessions/` | Invalidar sesiones cuando cambia el carrito |
| `payments/views.py` | `/orders/api/order/<id>/mark-paid/` | Marcar orden pagada al completar pago |

---

## Estructura de Archivos por Módulo

```
products/
├── api.py                    # NUEVO: Endpoints internos
├── urls.py                   # MODIFICAR: Agregar rutas /api/
└── ...

orders/
├── api.py                    # NUEVO: Endpoints internos
├── urls.py                   # MODIFICAR: Agregar rutas /api/
├── http_client.py            # NUEVO: Cliente HTTP para llamar a otros módulos
└── views.py                  # MODIFICAR: Usar http_client en lugar de imports

payments/
├── api.py                    # NUEVO: Endpoints internos
├── urls.py                   # MODIFICAR: Agregar rutas /api/
├── http_client.py            # NUEVO: Cliente HTTP para llamar a otros módulos
├── views.py                  # MODIFICAR: Usar http_client en lugar de imports
└── services/payment_service.py  # MODIFICAR: Recibir datos en lugar de OrderDTO

core/                         # NUEVO: Utilidades compartidas
├── __init__.py
└── internal_http.py          # Cliente HTTP base usando urllib
```

---

## Flujo de Comunicación

### Caso 1: Mostrar carrito con productos

```
orders/views.py (MyOrdersView)
    │
    ├── Obtiene Order y OrderProducts (models propios)
    │   └── Tiene: product_id, product_name, product_price, quantity
    │
    ├── Necesita: stock, photo de cada producto
    │
    └── Llama HTTP POST /products/api/products-info/
            │
            └── products/api.py
                    │
                    └── Retorna: {product_id: {stock, photo_url, ...}}
```

### Caso 2: Actualizar cantidad de producto en carrito

```
orders/views.py (update_order_item)
    │
    ├── Recibe: order_item_id, nueva_cantidad
    │
    ├── Necesita: stock actual del producto
    │
    └── Llama HTTP POST /products/api/product-stock/
            │
            └── products/api.py
                    │
                    └── Retorna: {product_id: stock}
    │
    ├── Valida cantidad <= stock
    │
    ├── Actualiza OrderProduct
    │
    └── Llama HTTP POST /payments/api/invalidate-sessions/
            │
            └── payments/api.py
                    │
                    └── Invalida sesiones pendientes
```

### Caso 3: Completar pago

```
payments/views.py (PaymentCheckoutView.form_valid)
    │
    ├── Recibe: token de sesión
    │   └── Tiene: order_id, user_id, items, amount_total
    │
    ├── Marca sesión como completada
    │
    └── Llama HTTP POST /orders/api/order/<order_id>/mark-paid/
            │
            └── orders/api.py
                    │
                    └── Marca Order.is_active = False
```

---

## Detalle de Archivos a Crear

### 1. `core/__init__.py`

Vacío, solo para que sea un paquete Python.

---

### 2. `core/internal_http.py`

Cliente HTTP base usando `urllib` de Python estándar.

**Funciones:**
- `internal_post(url_path, data)` - Hace POST interno con JSON
- `internal_get(url_path)` - Hace GET interno

**Características:**
- Usa `urllib.request` de Python estándar
- No requiere dependencias externas
- Se comunica internamente sin salir del servidor
- Maneja errores de conexión

---

### 3. `products/api.py`

**Funciones:**
- `products_info_view(request)` - Recibe product_ids, retorna info completa (stock, photo, name, price, available)
- `products_stock_view(request)` - Recibe product_ids, retorna solo stocks

**Retorno de `products_info_view`:**
```json
{
    "products": {
        "1": {
            "id": 1,
            "name": "Producto 1",
            "price": "100.00",
            "stock": 10,
            "available": true,
            "photo_url": "/media/upload/producto1.jpg"
        }
    }
}
```

---

### 4. `orders/api.py`

**Funciones:**
- `order_detail_view(request, order_id)` - Retorna info de orden completa
- `order_mark_paid_view(request, order_id)` - Marca orden como pagada

**Retorno de `order_detail_view`:**
```json
{
    "order": {
        "id": 1,
        "user_id": 5,
        "user_username": "juan",
        "user_email": "juan@email.com",
        "is_active": true,
        "items": [
            {
                "id": 1,
                "product_id": 10,
                "product_name": "Producto 10",
                "product_price": "100.00",
                "quantity": 2
            }
        ]
    }
}
```

---

### 5. `orders/http_client.py`

**Funciones:**
- `get_products_info(product_ids)` - Llama a `/products/api/products-info/`
- `get_products_stock(product_ids)` - Llama a `/products/api/product-stock/`
- `invalidate_payment_sessions(order_id)` - Llama a `/payments/api/invalidate-sessions/`

---

### 6. `payments/api.py`

**Funciones:**
- `invalidate_sessions_view(request)` - Invalida sesiones por order_id

**Retorno:**
```json
{
    "deleted": 2
}
```

---

### 7. `payments/http_client.py`

**Funciones:**
- `mark_order_as_paid(order_id)` - Llama a `/orders/api/order/<id>/mark-paid/`

---

## Detalle de Archivos a Modificar

### 1. `products/urls.py`

Agregar rutas API:
```python
path('api/products-info/', products_info_view, name='api-products-info'),
path('api/product-stock/', products_stock_view, name='api-product-stock'),
```

---

### 2. `orders/urls.py`

Agregar rutas API:
```python
path('api/order/<int:order_id>/', order_detail_view, name='api-order-detail'),
path('api/order/<int:order_id>/mark-paid/', order_mark_paid_view, name='api-order-mark-paid'),
```

---

### 3. `orders/views.py`

**Cambios en `MyOrdersView`:**
- Usar `get_products_info()` de `orders/http_client.py` en lugar de `get_products_by_ids()` de `products.services`
- Eliminar import: `from products.services import ...`

**Cambios en `update_order_item`:**
- Usar `get_products_stock()` para validar stock
- Usar `invalidate_payment_sessions()` para invalidar pagos pendientes
- Eliminar imports: `from products.services import ...`, `from payments.services import ...`

**Cambios en `remove_order_item`:**
- Usar `invalidate_payment_sessions()` para invalidar pagos pendientes
- Eliminar import: `from payments.services import ...`

**Cambios en `OrderProcessedView`:**
- Usar cliente HTTP para obtener sesión completada
- Eliminar import: `from payments.services import ...`

---

### 4. `payments/urls.py`

Agregar rutas API:
```python
path('api/invalidate-sessions/', invalidate_sessions_view, name='api-invalidate-sessions'),
```

---

### 5. `payments/views.py`

**Cambios en `create_session_view`:**
- Recibir datos de orden en el POST (order_id, items, user info)
- Eliminar imports: `from orders.services import ...`, `from orders.models import ...`

**Cambios en `PaymentCheckoutView.form_valid`:**
- Usar `mark_order_as_paid()` de `payments/http_client.py`
- Eliminar import: `from orders.services import ...`

---

### 6. `payments/services/payment_service.py`

**Cambios en `create_payment_session()`:**
- Recibir datos como diccionario en lugar de `OrderDTO`
- Parámetros: `order_data: dict` con claves: `id`, `items` (lista de dicts)
- Eliminar import: `from orders.services.interfaces import ...`

---

## Detalle de Archivos a Eliminar

| Archivo | Razón |
|---------|-------|
| `orders/services/interfaces.py` | Ya no se usa, datos pasan vía HTTP |
| `payments/services/interfaces.py` | Ya no se usa, datos pasan vía HTTP |
| `products/services/interfaces.py` | Ya no se usa, datos pasan vía HTTP |
| `integrations/` (carpeta completa) | Se eliminó el enfoque de integrations |
| `contracts/` (carpeta completa) | Se eliminó el enfoque de contracts |

---

## Orden de Implementación

1. ✅ Crear `core/__init__.py`
2. ✅ Crear `core/internal_http.py` (cliente HTTP base)
3. ✅ Crear `products/api.py` (endpoints de products)
4. ✅ Modificar `products/urls.py` (agregar rutas API)
5. ✅ Crear `orders/api.py` (endpoints de orders)
6. ✅ Modificar `orders/urls.py` (agregar rutas API)
7. ✅ Crear `orders/http_client.py` (cliente HTTP)
8. ✅ Modificar `orders/views.py` (usar http_client)
9. ✅ Crear `payments/api.py` (endpoints de payments)
10. ✅ Modificar `payments/urls.py` (agregar rutas API)
11. ✅ Crear `payments/http_client.py` (cliente HTTP)
12. ✅ Modificar `payments/views.py` (usar http_client)
13. ✅ Modificar `payments/services/payment_service.py` (recibir datos como dict)
14. ✅ Eliminar `orders/services/interfaces.py`
15. ✅ Eliminar `payments/services/interfaces.py`
16. ✅ Eliminar `products/services/interfaces.py`
17. ✅ Eliminar carpeta `integrations/` (si existe)
18. ✅ Eliminar carpeta `contracts/` (si existe)
19. ✅ Ejecutar `docker compose run --rm web python manage.py check`
20. ✅ Mover `OrderProductForm` a `orders/forms.py` (sin importar Product)
21. ✅ Probar flujos manualmente:
    - Ver carrito
    - Actualizar cantidad
    - Eliminar producto
    - Completar pago

---

## Mejoras Pendientes para Futuro

### 1. Autenticación Interna

**Problema actual:** Las APIs internas no tienen autenticación, cualquiera podría llamarlas.

**Solución propuesta:**
- Agregar token estático en settings: `INTERNAL_API_TOKEN`
- Crear decorador `@internal_api` que valide el header `X-Internal-Token`
- O verificar que la petición viene de localhost/127.0.0.1

**Archivos a modificar:**
- `core/internal_http.py` - Agregar header de autenticación
- `core/decorators.py` - Nuevo archivo con decorador `@internal_api`
- Cada vista en `*/api.py` - Agregar decorador

---

### 2. Manejo de Transacciones

**Problema actual:** Si `payments` completa el pago pero falla la llamada HTTP a `orders` para marcar como pagada, queda inconsistente.

**Solución propuesta:**
- Implementar patrón Saga con compensación
- Agregar campo `payment_completed_at` en `Order`
- Crear comando de reconciliación: `python manage.py reconcile_orders`

**Archivos a crear/modificar:**
- `payments/services/compensation.py` - Lógica de compensación
- `orders/management/commands/reconcile_orders.py` - Comando de reconciliación
- `orders/models.py` - Agregar campo `payment_completed_at`

---

### 3. Retry Logic

**Problema actual:** Si una llamada HTTP falla por timeout o error transitorio, no se reintenta.

**Solución propuesta:**
- Agregar decorador de retry en `core/internal_http.py`
- Configurar número de reintentos y delay
- Usar librería `tenacity` o implementación propia simple

**Archivos a modificar:**
- `core/internal_http.py` - Agregar lógica de retry
- `settings.py` - Agregar configuración de reintentos

---

### 4. Logging

**Problema actual:** No hay registro de las llamadas HTTP entre módulos.

**Solución propuesta:**
- Agregar logging en `core/internal_http.py`
- Registrar: URL, método, parámetros, respuesta, tiempo
- Crear archivo de log separado: `logs/internal_api.log`

**Archivos a crear/modificar:**
- `core/internal_http.py` - Agregar logging
- `settings.py` - Configurar logger para API interna

---

### 5. Timeouts

**Problema actual:** Las llamadas HTTP no tienen timeout configurado.

**Solución propuesta:**
- Configurar timeout en `core/internal_http.py`
- Tiempo razonable: 5 segundos para APIs internas
- Agregar configuración en settings

**Archivos a modificar:**
- `core/internal_http.py` - Agregar timeout
- `settings.py` - Agregar `INTERNAL_API_TIMEOUT = 5`

---

### 6. Circuit Breaker

**Problema actual:** Si un módulo falla repetidamente, las llamadas continúan intentando.

**Solución propuesta:**
- Implementar patrón Circuit Breaker
- Después de N fallos consecutivos, dejar de intentar por un tiempo
- Usar librería `pybreaker` o implementación propia

**Archivos a crear/modificar:**
- `core/circuit_breaker.py` - Nuevo archivo
- `core/internal_http.py` - Integrar circuit breaker
- `settings.py` - Configurar umbrales

---

## Resultado Final

```
orders/           payments/         products/
├── views.py      ├── views.py      ├── views.py
├── api.py        ├── api.py        ├── api.py
├── http_client   ├── http_client   └── ...
└── models        └── models        
     │                 │
     │    HTTP         │    HTTP
     └──────► ◄────────┘
           (core/internal_http.py)
```

**Sin acoplamiento:**
- `orders/` no importa de `payments/` ni `products/`
- `payments/` no importa de `orders/` ni `products/`
- `products/` no importa de ningún otro módulo

**Comunicación:**
- Todos los módulos se comunican vía HTTP interno
- Los endpoints API exponen funcionalidad
- Los http_client encapsulan las llamadas
- `core/internal_http.py` es la infraestructura compartida

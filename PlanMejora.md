# Plan de Mejoras y Correcciones - Proyecto Django

---

## 🔴 VULNERABILIDADES CRÍTICAS

| # | Vulnerabilidad | Ubicación |
|---|----------------|-----------|
| 3 | **IDOR en order_detail_view** - Cualquier usuario puede ver cualquier orden | `orders/api.py:10-35` |
| 4 | **IDOR en mark_order_as_paid** - Sin verificación de propiedad | `orders/api.py:38-49` |
| 5 | **CSRF desactivado** en APIs POST | `products/api.py:28,56` |
| 6 | **ALLOWED_HOSTS demasiado permisivo** (0.0.0.0) | `settings.py:32` |
| 7 | **No hay autenticación** en endpoints API | `products/api.py`, `orders/api.py`, `payments/api.py` |
| 8 | **Sin rate limiting** en APIs públicas | - |
| 9 | **Token de pago en URL** sin verificación de propiedad | `payments/views.py:74-76` |

---

## 🟡 MEJORAS RECOMENDADAS

### Seguridad
- Configurar HTTPS en producción
- Añadir CORS y security headers
- Implementar rate limiting
- Usar Django REST Framework con autenticación JWT

### Arquitectura
- Mantener `internal_http.py` para comunicación entre servicios (diseño intencional para microservicios)
- Separar lógica de negocio en servicios
- Implementar DRF con JWT

### Código
- Añadir tests (pytest/django test)
- Añadir logging
- Manejo de errores consistente
- Type hints consistentes
- Paginación en listados

### Base de Datos
- Migrar de SQLite a PostgreSQL
- Añadir índices en campos frecuentemente consultados
- Validaciones en modelos

### Deployment
- Configurar proper docker-compose
- Usar environment variables
- Configurar CI/CD

---

## 📋 PLAN ÓPTIMO DE MEJORA

### PRIORIDAD ALTA (Seguridad Crítica) - DRF con JWT

1. [ ] Añadir `djangorestframework` y `djangorestframework-simplejwt` a requirements.txt
2. [ ] Configurar DRF en settings.py (DEFAULT_AUTHENTICATION_CLASSES, DEFAULT_PERMISSION_CLASSES)
3. [ ] Configurar JWT en settings.py (SIMPLE_JWT)
4. [ ] Añadir URLs de autenticación JWT (token obtain/refresh)

#### Service Accounts
5. [ ] Crear usuario `service_orders` en Django
6. [ ] Crear usuario `service_payments` en Django
7. [ ] Configurar credenciales en variables de entorno:
   - `SERVICE_ORDERS_USERNAME`
   - `SERVICE_ORDERS_PASSWORD`
   - `SERVICE_PAYMENTS_USERNAME`
   - `SERVICE_PAYMENTS_PASSWORD`

#### PRODUCTS (app)
8. [ ] Crear serializers para Product
9. [ ] Refactorizar vistas a DRF APIView
10. [ ] Configurar URLs con prefijo `/api/`
11. [ ] Añadir autenticación JWT

#### ORDERS (app)
12. [ ] Crear serializers para Order y OrderProduct
13. [ ] Refactorizar vistas a DRF APIView
14. [ ] Configurar URLs con prefijo `/api/`
15. [ ] Añadir autenticación JWT
16. [ ] Implementar permiso IsOwner (corregir IDOR)

#### PAYMENTS (app)
17. [ ] Crear serializers para PaymentSession y PaymentItem
18. [ ] Refactorizar vistas a DRF APIView
19. [ ] Configurar URLs con prefijo `/api/`
20. [ ] Añadir autenticación JWT
21. [ ] Verificar propiedad del token (corregir IDOR)

#### HTTP Clients
22. [ ] Actualizar `core/internal_http.py` para aceptar token JWT en headers
23. [ ] Actualizar `orders/http_client.py` para obtener token del service account y enviar en requests
24. [ ] Actualizar `payments/http_client.py` para obtener token del service account y enviar en requests

---

### PRIORIDAD MEDIA

25. [ ] Crear permiso personalizado IsOwner
26. [ ] Crear management command para crear service accounts automáticamente
27. [ ] Añadir logging centralizado
28. [ ] Crear tests unitarios y de integración

---

### PRIORIDAD BAJA (Optimización)

29. [ ] Migrar SQLite → PostgreSQL
30. [ ] Implementar caché (Redis)
31. [ ] Añadir paginación en listados
32. [ ] Configurar CI/CD
33. [ ] Documentar APIs con Swagger/OpenAPI

---

## ✅ Arquitectura Validada

- **internal_http.py**: Diseño intencional para futura separación como microservicios. ✅ Correcto.
- **Service Accounts**: Cada servicio (orders, payments) usará credenciales propias para autenticarse via JWT.

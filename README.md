# E-commerce Django Project

## Descripción General

Proyecto de comercio electrónico desarrollado con Django y Django REST Framework. Implementa un flujo completo de compra: catálogo de productos, carrito de compras, gestión de órdenes y simulación de pagos.

## Arquitectura

El proyecto sigue una arquitectura de módulos independientes que se comunican via HTTP:

- **products/**: Catálogo de productos con imágenes y control de stock
- **orders/**: Carrito de compras y gestión de órdenes por usuario
- **payments/**: Simulación de pasarela de pagos con sesiones
- **core/**: Utilidades compartidas (cliente HTTP interno)

### Comunicación Entre Módulos

Cada módulo se comunica con los demás mediante HTTP + JWT, no acceso directo a bases de datos:

```
Orders ──HTTP/JWT──► Products
   │                    ▲
   │                    │
   └─────HTTP/JWT───────┘
         Payments
```

- `core/internal_http.py`: Cliente HTTP interno para peticiones
- `http_client.py` en cada módulo: Abstrae la comunicación con otros módulos

## Tecnologías

| Tecnología | Propósito |
|------------|-----------|
| Django 5.2 | Framework web |
| Django REST Framework | API REST |
| djangorestframework-simplejwt | Autenticación JWT |
| TailwindCSS | Estilos frontend |

## Flujo de Compra

```
1. Usuario inicia sesión
2. Explora productos (/product/)
3. Agrega productos al carrito (AJAX)
4. Gestiona su carrito (/orders/my-orders/)
5. Inicia proceso de pago
6. Completa checkout (/payments/checkout/<token>/)
7. Confirma pago → orden procesada
```

## Configuración

### Variables de Entorno

Copiar `.env.example` a `.env` y configurar los valores necesarios.

**Credenciales de servicio**: El proyecto usa credenciales de servicio para la comunicación HTTP entre módulos (orders → products, payments → orders). Estas credenciales permiten que cada módulo se autentique ante los demás para realizar peticiones.

### ALLOWED_HOSTS (para Docker)

Agregar `host.docker.internal` a `ALLOWED_HOSTS` en `settings.py` cuando se ejecute en Docker.

## Comandos

```bash
python manage.py runserver 0.0.0.0:8000
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

## Mejores Prácticas seguidas

- Separación de módulos independientes
- Comunicación HTTP entre aplicaciones
- Servicios de negocio aislados
- API REST bien definida
- Autenticación JWT para seguridad inter-servicios

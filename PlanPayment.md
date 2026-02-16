## Plan App Payments

- **App payments**
  - Crear app `payments` y registrarla en `INSTALLED_APPS`.
  - Modelos: `PaymentSession` con orden, usuario, token UUID, estado (`pending`, `completed`, `failed`), totales y timestamps; `PaymentItem` para snapshot de cada producto (nombre, precio, cantidad).
  - Admin opcional si se usa.

- **Lógica del microservicio**
  - `payments/services.py`: función `create_payment_session(order, user)` que valide orden activa con ítems, genere token, clone productos en `PaymentItem`, calcule total y retorne URL `/payments/checkout/<token>/`.
  - Vistas:
    - `create_session_view` (POST clásico) protegido con login: obtiene orden activa, llama servicio y redirige a checkout; en errores (orden vacía o inexistente) vuelve al carrito con mensajes.
    - `PaymentCheckoutView` (GET muestra resumen + formulario simulado de tarjeta; POST valida campos dummy); si pago “exitoso”, marca sesión completada, orden `is_active=False`, registra fecha de pago.
  - Formularios: `PaymentForm` con `card_number` y `cvv` validación simple.

- **URLs**
  - `payments/urls.py`: ruta `create-session/` para POST, ruta `checkout/<uuid:token>/`.
  - Incluir `path('payments/', include('payments.urls'))` en `my_first_project/urls.py`.

- **Integración en orders**
  - Reusar `MyOrdersView` como carrito. Si la orden tiene ítems, mostrar botón `Proceder al pago` con formulario que haga POST a `payments:create-session`.
  - Nueva vista `OrderProcessedView` (LoginRequired) que reciba `session_token` en query o URL, obtenga sesión completada y muestre productos comprados; si token inválido redirige al carrito.
  - `orders/urls.py`: añadir `path('processed/<uuid:token>/', OrderProcessedView.as_view(), name='order-processed')`.
  - Plantillas:
    - Actualizar `orders/templates/my_orders.html` con botón y manejo de mensajes.
    - Crear `payments/templates/payments/checkout.html` con resumen + formulario.
    - Crear `orders/templates/order_processed.html` con lista de artículos pagados y mensaje de éxito.

- **Flujo final**
  1. Usuario en carrito (`my_orders`) envía POST → `payments:create-session`.
  2. Servicio crea sesión y redirige a `/payments/checkout/<token>/`.
  3. Usuario ingresa datos simulados; al guardar, micro marca pago completado y redirige a `orders:order-processed` mostrando resumen final.

- **Validaciones y extras**
  - Mensajes informativos (Django messages) para errores como orden sin productos o sesión expirada.
  - Manejo de reintentos: si sesión completada no permitir re-procesar (redirigir a pantalla de confirmación).
  - Mantener consistencia con estilos existentes (Tailwind utilities vistas actuales).

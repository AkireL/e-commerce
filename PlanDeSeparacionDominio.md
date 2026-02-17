# Plan de Separación de Dominios

## Objetivo
Eliminar dependencias directas entre dominios (FKs cruzados) conservando los nombres de tablas existentes y copiando la información relevante mediante campos snapshot.

## Alcance
- Desacoplar órdenes, productos y sesiones de pago: `orders_order`, `orders_orderproduct`, `payments_paymentsession` (y sus items).
- Mantener integridad histórica almacenando datos necesarios (usuario, producto, totales) en el propio registro.
- No se requieren respaldos formales (datos falsos) ni nuevos campos de moneda en esta fase.

## Cambios de Modelo
1. **orders.Order**
   - Reemplazar `user` (`ForeignKey`) por `IntegerField` (`user_id`).
   - Agregar snapshots: `user_username`, `user_email` (y adicionales si negocio lo requiere).

2. **orders.OrderProduct**
   - Reemplazar `product` por `IntegerField` (`product_id`).
   - Añadir snapshots: `product_name`, `product_price` (otros campos opcionales como `description`).

3. **payments.PaymentSession**
   - Sustituir FKs por enteros `order_id` y `user_id`.
   - Guardar snapshots: `order_number` (id de orden), `user_username`, y mantener `amount_total` existente.

4. **payments.PaymentItem**
   - Mantener snapshot actual (`product_id`, `product_name`, `unit_price`, `quantity`). Ajustar solo si se requieren campos extra.

## Actualizaciones de Código
- Crear helpers para poblar snapshots al generar órdenes, productos agregados al carrito y sesiones de pago.
- Sustituir accesos a relaciones (`order.user`, `orderproduct.product`) por los campos snapshot.
- Ajustar vistas, servicios y plantillas para usar los nuevos atributos.

## Plan de Migraciones
1. **Migración de esquema inicial**
   - Añadir nuevos campos snapshot (`null=True, blank=True`).
   - Deshabilitar constraints (`db_constraint=False`) en FKs a eliminar.

2. **Migración de datos (RunPython)**
   - Poblar snapshots iterando en lotes sobre órdenes y productos existentes.
   - Copiar valores de ids actuales a las nuevas columnas (`user_id`, `product_id`, etc.).

3. **Migración final**
   - Convertir FKs en `IntegerField` definitivo y eliminar constraints.
   - Establecer `null=False` cuando los datos estén completos.
   - Añadir índices (`db_index=True`) para búsquedas por `user_id`, `order_id`, `product_id`.

## Comandos (ejecutar manualmente tras modificar modelos)
1. `python3 manage.py makemigrations orders payments`
2. `python3 manage.py migrate`

## Verificación
- Crear orden y agregar productos para asegurar que snapshots se registran.
- Simular pago y confirmar que `PaymentSession` contiene la información esperada.
- Revisar que las vistas y reportes funcionen sin depender de joins cruzados.

## Pendientes por confirmar
- Lista exacta de campos snapshot requeridos por negocio (nombre completo, dirección, etc.).
- Modulos adicionales que dependan de los campos eliminados.

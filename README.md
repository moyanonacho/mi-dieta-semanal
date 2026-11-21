# Mi Dieta Semanal

Web para seguir la dieta del nutricionista por raciones: menú semanal, lista de la compra con fotos y precios de Mercadona, plan de deporte y balance de calorías.

Cada persona crea su cuenta con email y contraseña y solo ve sus propios datos (Supabase con reglas por usuario).

- `index.html` se genera desde la app de Claude con `herramientas/construir_web_dieta.py` (en el PC de Nacho).
- `supabase/esquema.sql`: tablas y reglas de seguridad.
- Se publica sola en GitHub Pages al subir cambios a `main`.

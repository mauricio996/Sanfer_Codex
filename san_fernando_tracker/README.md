# San Fernando Weekly Digital Performance Tracker

Proyecto de reporting semanal automatizado para meta mensual de sesiones, conversiones, nuevos usuarios e ingresos (PEN).

## Estructura
Incluye conectores de GA4, Meta Ads, Google Ads, persistencia en BigQuery, lógica de alertas y generación de reporte HTML.

## Ejecutar en Google Colab (sin instalación local)
1. Abrir `san_fernando_tracker.ipynb` en Colab.
2. Subir `service_account.json` con el widget de archivos.
3. Completar variables sensibles en `config.py` (tokens OAuth de Meta y Google Ads).
4. Ejecutar todas las celdas.

## Scheduling semanal (lunes 8:00 Lima)
Recomendado: **Cloud Run + Cloud Scheduler**.

1. Empaquetar el proyecto en una imagen Docker y desplegar a Cloud Run.
2. Configurar job HTTP en Cloud Scheduler con zona horaria `America/Lima`.
3. Cron: `0 8 * * 1`.
4. Adjuntar cuenta de servicio con permisos de BigQuery, GA4 y envío de email.

Este enfoque es serverless y económico para usuarios en Lima sin servidor local.

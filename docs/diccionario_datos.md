# Diccionario de datos del artefacto

Este documento resume las variables más importantes que alimentarán el dashboard del proyecto de seguro agrícola indexado para café en Colombia.

## 1. Cubos de datos

### weekly.csv
Frecuencia semanal por departamento. Se usa para monitoreo operativo, sensibilidad y seguimiento reciente.

### monthly.csv
Frecuencia mensual por departamento. Es la base principal del artefacto para análisis comparativo y soporte técnico.

### annual.csv
Frecuencia anual por departamento. Se usa como contraste metodológico y apoyo a la lectura técnica.

---

## 2. Variables clave por frecuencia

## Weekly

| Variable | Tipo | Significado | Uso sugerido en la app |
|---|---|---|---|
| fecha_semana_inicio | fecha | Inicio de la semana | Filtros y series |
| fecha_semana_fin | fecha | Fin de la semana | Filtros y series |
| anio_referencia_y | entero | Año de referencia | Filtros |
| mes_referencia_y | entero | Mes de referencia | Filtros |
| semana_iso | entero | Semana ISO | Series semanales |
| departamento | texto | Departamento del panel | Comparación territorial |
| produccion_semanal_proxy_t | numérica | Proxy semanal de producción | Indicador operativo |
| PRECTOTCORR | numérica | Precipitación corregida | Clima semanal |
| T2M | numérica | Temperatura media a 2m | Clima semanal |
| T2M_MAX | numérica | Temperatura máxima | Estrés térmico |
| T2M_MIN | numérica | Temperatura mínima | Contexto térmico |
| RH2M | numérica | Humedad relativa | Clima semanal |
| GWETROOT | numérica | Humedad del suelo en raíz | Riesgo hídrico |
| ALLSKY_SFC_SW_DWN | numérica | Radiación superficial | Contexto climático |
| WS2M | numérica | Velocidad del viento | Contexto climático |
| lluvia_acum_4s | numérica | Lluvia acumulada 4 semanas | Riesgo climático derivado |
| lluvia_acum_8s | numérica | Lluvia acumulada 8 semanas | Riesgo climático derivado |
| anomalia_lluvia_semana_iso | numérica | Anomalía de lluvia semanal | Señal comparativa |
| t2m_max_ma_4s | numérica | Media móvil de temperatura máxima | Persistencia térmica |
| gwetroot_ma_4s | numérica | Media móvil de humedad raíz | Persistencia hídrica |
| precio_interno_cop_carga | numérica | Precio interno del café | Contexto económico |
| precio_externo_exdock_cent_usd_lb | numérica | Precio externo del café | Contexto económico |
| exportaciones_mensual_miles_sacos | numérica | Exportaciones de café | Contexto económico |
| trm_promedio_semana_cop_usd | numérica | TRM promedio semanal | Contexto cambiario |

## Monthly

| Variable | Tipo | Significado | Uso sugerido en la app |
|---|---|---|---|
| departamento | texto | Departamento | Filtros y comparaciones |
| anio_referencia_y | entero | Año | Filtros |
| mes_referencia_y | entero | Mes | Filtros |
| produccion_mensual_desde_semana_t | numérica | Producción mensual agregada desde semanas | Verificación de consistencia |
| produccion_mensual_proxy_t | numérica | Proxy mensual de producción | Indicador central |
| produccion_anual_departamental_t | numérica | Producción anual departamental | Contexto productivo |
| area_cosechada_departamental_ha | numérica | Área cosechada | Estructural |
| rendimiento_departamental_t_ha | numérica | Rendimiento por hectárea | Desempeño productivo |
| valor_cosecha_anual_millones | numérica | Valor anual de cosecha | Contexto económico |
| PRECTOTCORR | numérica | Precipitación agregada | Clima mensual |
| T2M_mean | numérica | Temperatura media mensual | Clima mensual |
| T2M_MAX_mean | numérica | Temperatura máxima media | Estrés térmico |
| RH2M_mean | numérica | Humedad relativa media | Clima mensual |
| GWETROOT_mean | numérica | Humedad del suelo media | Riesgo hídrico |
| ALLSKY_SFC_SW_DWN_mean | numérica | Radiación media | Clima mensual |
| WS2M_mean | numérica | Viento medio | Clima mensual |
| anomalia_lluvia_semana_iso_mean | numérica | Anomalía promedio | Señal climática |
| indice_climatico_base_x_mean | numérica | Índice climático base promedio | Indicador resumen |
| indice_climatico_ajustado_x_mean | numérica | Índice climático ajustado promedio | Indicador resumen |
| dummy_exceso_lluvia_p75_any | binaria | Hubo evento de exceso de lluvia | Alerta |
| dummy_estres_hidrico_p25_any | binaria | Hubo estrés hídrico | Alerta |
| dummy_temp_max_alta_p75_any | binaria | Hubo temperatura alta extrema | Alerta |
| precio_interno_cop_carga_mean | numérica | Precio interno promedio | Contexto económico |
| precio_externo_exdock_cent_usd_lb_mean | numérica | Precio externo promedio | Contexto económico |
| exportaciones_mensual_miles_sacos_mean | numérica | Exportaciones promedio/agregadas | Contexto económico |
| trm_promedio_semana_cop_usd_mean | numérica | TRM promedio mensual | Contexto cambiario |
| diff_target_mensual | numérica | Diferencia de consistencia del target | Control técnico |

## Annual

| Variable | Tipo | Significado | Uso sugerido en la app |
|---|---|---|---|
| departamento | texto | Departamento | Filtros |
| anio_referencia_y | entero | Año | Series/análisis |
| produccion_anual_desde_semana_t | numérica | Producción anual agregada desde semanas | Control técnico |
| produccion_anual_departamental_t | numérica | Producción anual departamental | Indicador annual |
| area_cosechada_departamental_ha | numérica | Área cosechada | Estructural |
| rendimiento_departamental_t_ha | numérica | Rendimiento anual | Contraste metodológico |
| valor_cosecha_anual_millones | numérica | Valor anual cosecha | Contexto económico |
| PRECTOTCORR | numérica | Clima agregado anual | Soporte metodológico |
| T2M_mean | numérica | Temperatura media anual | Soporte metodológico |
| RH2M_mean | numérica | Humedad media anual | Soporte metodológico |
| GWETROOT_mean | numérica | Humedad suelo anual | Soporte metodológico |
| precio_interno_cop_carga_mean | numérica | Precio interno promedio anual | Contexto económico |
| precio_externo_exdock_cent_usd_lb_mean | numérica | Precio externo promedio anual | Contexto económico |
| exportaciones_mensual_miles_sacos_mean | numérica | Exportaciones promedio anual | Contexto económico |
| trm_promedio_semana_cop_usd_mean | numérica | TRM promedio anual | Contexto cambiario |
| diff_target_anual | numérica | Diferencia de consistencia del target | Control técnico |

---

## 3. Nota de uso

- El dashboard debe usar como base principal los cubos **departamentales**.
- La “proxy nacional” puede calcularse posteriormente agregando departamentos.
- No todas las variables del cubo completo se usarán en la interfaz final; este diccionario prioriza las más útiles para el artefacto.

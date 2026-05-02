# Proyecto: Modelo Analítico Climático para Riesgo de Café en Colombia

**README metodológico actualizado**  
**Periodo del cubo:** 2021-2024  
**Unidad de análisis:** semana ISO  
**Nivel analítico:** proxy nacional y panel departamental construido desde cinco municipios cafeteros representativos  

---

## 1. Contexto del proyecto

El cultivo de café en Colombia es altamente vulnerable al riesgo climático. La variabilidad en precipitaciones, los excesos de lluvia, los periodos secos, la temperatura, la humedad del suelo y la radiación pueden afectar la floración, el desarrollo del fruto, la calidad del grano y el volumen producido.

El objetivo del proyecto es construir un cubo de datos semanal que permita estudiar la relación entre condiciones climáticas, producción cafetera y señales económicas, como insumo para un futuro modelo de **seguro agrícola indexado**.

La principal limitación metodológica es que la producción agrícola observada está disponible en frecuencia anual para los municipios seleccionados, mientras que las variables climáticas y económicas se encuentran en frecuencia semanal, mensual o diaria. Por esta razón, se construye una **Y semanal proxy**, documentando explícitamente sus supuestos, limitaciones y usos.

---

## 2. Objetivo del cubo de datos

Construir una base semanal 2021-2024 que permita:

- Integrar producción, clima y variables económicas en una frecuencia común.
- Construir una variable objetivo semanal proxy sin usar clima en su construcción.
- Reservar las variables climáticas como **X explicativas** para modelación.
- Evitar leakage o correlación artificial entre la Y semanal y las X climáticas.
- Preparar dos estructuras de modelamiento:
  - una **base proxy nacional semanal**;
  - una **base panel departamental semanal**.
- Documentar los supuestos de desagregación temporal para que el modelo sea defendible.

---

## 3. Estructuras de datos generadas

### 3.1 Base proxy nacional semanal

La primera base tiene una fila por semana. Su lógica es construir una aproximación nacional a partir de los cinco municipios seleccionados.

En esta base:

- la producción anual corresponde a la suma de los cinco municipios;
- las variables climáticas corresponden al promedio nacional proxy previamente consolidado desde los cinco departamentos;
- las variables económicas como precio interno, precio externo, exportaciones, valor de cosecha y TRM se integran como señales de contexto nacional.

Esta base se entrega como:

```text
base_proxy_nacional_semanal_cafe_2021_2024.csv
```

Y también dentro del Excel consolidado:

```text
cubo_cafe_semanal_proxy_y_panel_2021_2024.xlsx
```

---

### 3.2 Base panel departamental semanal

La segunda base se construye en modo panel, con una fila por departamento y semana.

El nivel territorial queda como:

```text
departamento - semana
```

Se decidió dejar únicamente el nombre del departamento porque cada departamento representa el municipio seleccionado en el proyecto. Esto evita agregar columnas redundantes, dado que el municipio está determinado por la selección metodológica inicial.

| Departamento | Municipio representativo usado en producción |
|---|---|
| Antioquia | Fredonia |
| Caldas | Chinchiná |
| Cauca | Suárez |
| Huila | San Agustín |
| Tolima | Ibagué |

En esta base:

- la Y semanal se calcula para cada municipio/departamento;
- las variables climáticas se toman a nivel departamental;
- las variables económicas nacionales se replican para cada departamento-semana;
- se conserva una estructura adecuada para modelos panel, modelos con efectos por departamento o validaciones por corte temporal.

Esta base se entrega como:

```text
base_panel_departamental_semanal_cafe_2021_2024.csv
```

---

## 4. Selección territorial y construcción de la proxy nacional

El proyecto no usa directamente la producción nacional oficial como target principal. En su lugar, se construye una **proxy nacional** a partir de cinco municipios cafeteros representativos.

La lógica es:

> Seleccionar municipios ubicados en departamentos cafeteros relevantes, sumar o promediar sus variables según corresponda y construir una aproximación operacional del comportamiento cafetero nacional.

Esta decisión permite mantener coherencia entre producción agrícola y variables climáticas, ya que el clima proviene de las zonas seleccionadas y no de un agregado nacional genérico.

Para futuras mejoras, una extensión natural del proyecto será pasar de una proxy nacional a modelos específicos por municipio o departamento.

---

## 5. Fuentes de datos utilizadas

### 5.1 Producción municipal anual

Contiene producción, área sembrada, área cosechada y rendimiento por municipio. Es la fuente base para construir la producción anual observada de los municipios seleccionados.

Variables principales:

- `produccion_anual_t`
- `area_sembrada_ha`
- `area_cosechada_ha`
- `rendimiento_t_ha`

---

### 5.2 Producción nacional mensual oficial

Se usa como **patrón temporal de estacionalidad mensual**.

No se usa como target final, ni reemplaza la proxy de los cinco municipios. Su función es distribuir la producción anual municipal entre meses de forma más realista.

Variable principal:

```text
produccion_nacional_mensual_oficial_miles_sacos
```

---

### 5.3 Variables climáticas NASA

Variables semanales disponibles:

| Variable | Descripción | Uso |
|---|---|---|
| `PRECTOTCORR` | Precipitación corregida | X climática central |
| `IMERG_PRECTOT` | Precipitación IMERG | X climática complementaria |
| `T2M` | Temperatura media a 2 metros | X climática central |
| `T2M_MAX` | Temperatura máxima | X de estrés térmico |
| `T2M_MIN` | Temperatura mínima | X climática |
| `RH2M` | Humedad relativa | X asociada a hongos/estrés |
| `QV2M` | Humedad específica | X climática |
| `GWETTOP` | Humedad superficial del suelo | X central |
| `GWETROOT` | Humedad en zona radicular | X central |
| `ALLSKY_SFC_SW_DWN` | Radiación solar | X asociada a fotosíntesis |
| `WS2M` | Velocidad del viento | X complementaria |

---

### 5.4 Variables económicas y de mercado

| Variable | Uso recomendado |
|---|---|
| Precio interno del café | Señal económica local; preferir rezagos y medias móviles |
| Precio externo Ex-Dock | Señal externa/internacional; preferir rezagos |
| Exportaciones | Contexto comercial; preferir rezagos |
| Valor cosecha | Exposición financiera y severidad económica |
| TRM / dólar | Contexto cambiario y costos de insumos importados |

---

## 6. Construcción de la variable objetivo semanal `Y`

### 6.1 Nombre de la Y semanal

La variable objetivo semanal principal es:

```text
produccion_semanal_proxy_t
```

Esta variable representa producción semanal proxy en toneladas.

---

### 6.2 Interpretación correcta

La Y semanal **no es producción semanal observada**.

Debe interpretarse como:

> Producción semanal proxy asociada a la producción anual de los cinco municipios seleccionados, distribuida temporalmente con una regla trazable de desagregación temporal.

No debe interpretarse como:

> Producción semanal real observada de Colombia.

---

### 6.3 Paso 1: producción anual proxy

Para la base proxy nacional, primero se suma la producción anual de los cinco municipios:

\[
P^{proxy}_{a} = \sum_{j=1}^{5} P_{j,a}
\]

Donde:

- \(P^{proxy}_{a}\) es la producción anual proxy del año \(a\);
- \(P_{j,a}\) es la producción anual observada del municipio \(j\) en el año \(a\).

Para la base panel, se conserva la producción anual de cada municipio/departamento:

\[
P_{d,a}
\]

---

### 6.4 Paso 2: mensualización usando estacionalidad mensual nacional

La producción anual se distribuye entre meses usando la participación mensual de la producción nacional oficial.

\[
w_{a,m} = \frac{PN_{a,m}}{\sum_{m=1}^{12} PN_{a,m}}
\]

Donde:

- \(w_{a,m}\) es el peso del mes \(m\) en el año \(a\);
- \(PN_{a,m}\) es la producción nacional mensual oficial.

Luego, para la base proxy nacional:

\[
P^{proxy}_{a,m} = P^{proxy}_{a} \times w_{a,m}
\]

Y para la base panel:

\[
P_{d,a,m} = P_{d,a} \times w_{a,m}
\]

Esta etapa permite que la producción anual de los municipios tome una forma mensual coherente con la estacionalidad real observada en el país.

---

### 6.5 Paso 3: semanalización por proporción de días calendario

Para construir la Y semanal, se reemplazó la semanalización climática por una regla de calendario.

La producción mensual proxy se distribuye a semanas ISO usando la proporción de días de cada semana que caen dentro del mes correspondiente.

Para una semana \(s\) y un mes \(m\):

\[
d_{s,m} = \text{número de días de la semana } s \text{ que pertenecen al mes } m
\]

\[
D_m = \text{número total de días del mes } m
\]

Entonces:

\[
P^{proxy}_{s} = \sum_{m \in s} P^{proxy}_{a,m} \times \frac{d_{s,m}}{D_m}
\]

Para panel:

\[
P_{d,s} = \sum_{m \in s} P_{d,a,m} \times \frac{d_{s,m}}{D_m}
\]

Esta regla preserva exactamente los totales mensuales y, por construcción, también los totales anuales.

---

### 6.6 Validación obligatoria

La base incluye una hoja de validación anual:

```text
validacion_anual
```

La validación comprueba que:

\[
\sum_{s \in a} P^{proxy}_{s} = P^{proxy}_{a}
\]

Y para panel:

\[
\sum_{s \in a} P_{d,s} = P_{d,a}
\]

Las diferencias son prácticamente cero y corresponden únicamente a precisión numérica.

---

## 7. Cambio metodológico frente a la versión anterior

Inicialmente se había considerado usar un índice climático para distribuir la producción mensual entre semanas. Esa idea era útil desde una perspectiva operacional, pero podía generar un problema para la modelación.

Si la Y semanal se construye usando clima, y luego el modelo usa esas mismas variables climáticas como X, el modelo podría encontrar una relación parcialmente inducida por construcción. Esto se conoce como leakage o correlación artificial.

Por esta razón, la versión actual adopta la siguiente decisión:

> El clima no participa en la construcción de la Y semanal. La Y se construye con producción anual, estacionalidad mensual observada y pesos de calendario. Las variables climáticas quedan reservadas como X explicativas.

Texto metodológico recomendado:

> Para construir la variable objetivo semanal, se mantuvo la mensualización basada en la estacionalidad mensual nacional observada y se reemplazó la semanalización climática por una regla de desagregación temporal no climática. En particular, la producción mensual proxy se distribuye a semanas ISO usando pesos de calendario definidos por la proporción de días de cada semana que caen dentro del mes correspondiente, preservando exactamente los totales mensuales. Esta decisión metodológica permite evitar leakage con las variables climáticas semanales, las cuales quedan reservadas como covariables explicativas del modelo. En consecuencia, la serie semanal resultante debe interpretarse como una proxy operativa para simulación, monitoreo y sensibilidad del artefacto, y no como producción semanal observada.

---

## 8. Fundamento metodológico de la desagregación temporal

La construcción de una serie semanal a partir de una serie mensual se apoya en la literatura de **desagregación temporal** y **benchmarking**, cuyo objetivo es generar series de mayor frecuencia consistentes con agregados observados de menor frecuencia.

Denton propuso un enfoque clásico para ajustar series mensuales o trimestrales a totales anuales mediante minimización cuadrática. Posteriormente, Dagum y Cholette sistematizaron métodos de benchmarking, distribución temporal y reconciliación de series.

Sax y Steiner explican que la desagregación temporal puede realizarse con o sin indicadores de alta frecuencia, preservando sumas, promedios o valores de referencia de la serie original. También señalan que los métodos clásicos funcionan de manera más directa cuando la frecuencia alta es un múltiplo entero de la baja; combinaciones como mes a semana son irregulares, lo cual justifica reglas operativas y trazables cuando se busca preservar coherencia temporal sin introducir señales espurias.

En este proyecto, la transición mes-semana se resuelve con una regla simple: asignar producción mensual a semanas según la proporción de días de cada semana dentro del mes. Esta decisión es transparente, reproducible y evita incorporar clima en la construcción del target.

Referencias:

- Denton, F. T. (1971). *Adjustment of Monthly or Quarterly Series to Annual Totals: An Approach Based on Quadratic Minimization*. Journal of the American Statistical Association.
- Dagum, E. B., & Cholette, P. (2006). *Benchmarking, Temporal Distribution, and Reconciliation Methods for Time Series*.
- Sax, C., & Steiner, P. (2013). *Temporal Disaggregation of Time Series*. The R Journal. https://journal.r-project.org/articles/RJ-2013-028/
- Eurostat / ESS (2018). *ESS Guidelines on Temporal Disaggregation, Benchmarking and Reconciliation*.

---

## 9. Índice climático como variable X

Aunque el índice climático ya no se usa para construir la Y semanal, sí se conserva como una variable explicativa derivada.

Esto permite que un modelo robusto pueda evaluar si existe relación entre condiciones climáticas compuestas y la producción semanal proxy, sin que esa relación haya sido inducida artificialmente en el target.

### 9.1 Componentes del índice climático base

El índice climático base combina cuatro dimensiones:

1. Humedad del suelo.
2. Precipitación.
3. Temperatura.
4. Radiación solar.

La fórmula es:

\[
IC_s = 0.35 \cdot score\_humedad_s
+ 0.25 \cdot score\_precipitacion_s
+ 0.25 \cdot score\_temperatura_s
+ 0.15 \cdot score\_radiacion_s
\]

Donde \(s\) representa la semana.

---

### 9.2 Score de humedad

Se usan las variables:

```text
GWETROOT
GWETTOP
```

Primero se normalizan con min-max:

\[
minmax(x_s) = \frac{x_s - min(x)}{max(x) - min(x)}
\]

Luego:

\[
score\_humedad_s =
\frac{minmax(GWETROOT_s) + minmax(GWETTOP_s)}{2}
\]

La lógica es capturar tanto humedad superficial como humedad en zona radicular.

---

### 9.3 Score de precipitación

Se usa:

```text
PRECTOTCORR
```

Para evitar que semanas extremadamente lluviosas dominen el índice, la precipitación se capa en el percentil 90:

\[
PRECTOTCORR^{cap}_s = min(PRECTOTCORR_s, P90(PRECTOTCORR))
\]

Después:

\[
score\_precipitacion_s = minmax(PRECTOTCORR^{cap}_s)
\]

---

### 9.4 Score de temperatura

Se usa:

```text
T2M
```

El score premia temperaturas cercanas a la mediana histórica del periodo:

\[
ref\_temp = mediana(T2M)
\]

\[
score\_temperatura_s =
1 - \frac{|T2M_s - ref\_temp|}{max(|T2M - ref\_temp|)}
\]

Esto evita asumir que mayor temperatura siempre es mejor.

---

### 9.5 Score de radiación

Se usa:

```text
ALLSKY_SFC_SW_DWN
```

Y se normaliza con min-max:

\[
score\_radiacion_s = minmax(ALLSKY\_SFC\_SW\_DWN_s)
\]

---

### 9.6 Índice climático ajustado

Además del índice base, se conserva una versión suavizada:

\[
IC^{ajustado}_s = 0.70 + 0.30 \cdot IC_s
\]

En la base aparece como:

```text
indice_climatico_ajustado_x
```

En la versión anterior, este índice ajustado iba a usarse para repartir producción entre semanas. En la versión actual, **solo queda como X**, no como componente de la Y.

---

## 10. Variables económicas y transformaciones

Las variables económicas se conservan porque pueden aportar señales de contexto financiero y de mercado.

### 10.1 Precio interno

Variable base:

```text
precio_interno_cop_carga
```

Transformaciones recomendadas:

```text
precio_interno_cop_carga_lag_1s
precio_interno_cop_carga_lag_4s
precio_interno_cop_carga_ma_4s
precio_interno_cop_carga_var_4s
dummy_precio_interno_alto_p75
```

Interpretación:

> El precio interno puede reflejar condiciones de oferta, demanda, tasa de cambio, expectativas y dinámica del mercado cafetero. Por esta razón, se recomienda usarlo con rezagos y no necesariamente como señal contemporánea directa.

---

### 10.2 Precio externo

Variable base:

```text
precio_externo_exdock_cent_usd_lb
```

Transformaciones:

```text
precio_externo_exdock_cent_usd_lb_lag_4s
precio_externo_exdock_cent_usd_lb_ma_4s
precio_externo_exdock_cent_usd_lb_var_4s
```

---

### 10.3 Exportaciones

Variable base:

```text
exportaciones_mensual_miles_sacos
```

Uso recomendado:

- contexto de mercado;
- análisis descriptivo;
- validación económica;
- rezagos para evitar simultaneidad.

---

### 10.4 TRM / dólar

La TRM se incorpora como variable económica de contexto porque cambios en la tasa de cambio pueden afectar costos de insumos importados como fertilizantes, agroquímicos, maquinaria o repuestos.

Variable principal:

```text
trm_viernes_cop_usd
```

Regla de armonización semanal:

> Se toma la TRM del viernes de cada semana o, en ausencia de dato por festivo/no hábil, el último dato disponible anterior.

Transformaciones recomendadas:

```text
trm_viernes_cop_usd_lag_1s
trm_viernes_cop_usd_lag_4s
trm_viernes_cop_usd_ma_4s
trm_viernes_cop_usd_var_4s
dummy_trm_alta_p75
dummy_devaluacion_4s_p75
```

Nota: si el script se ejecuta sin conexión a internet, las columnas TRM quedan vacías y se pueden poblar al ejecutar nuevamente el script con acceso a la API de Datos Abiertos Colombia.

---

## 11. Variables que sí pueden usarse como X

### 11.1 X climáticas centrales

```text
PRECTOTCORR
IMERG_PRECTOT
T2M
T2M_MAX
T2M_MIN
RH2M
QV2M
GWETTOP
GWETROOT
ALLSKY_SFC_SW_DWN
WS2M
```

### 11.2 X climáticas derivadas

```text
score_humedad
score_precipitacion
score_temperatura
score_radiacion
indice_climatico_base_x
indice_climatico_ajustado_x
lluvia_acum_4s
lluvia_acum_8s
anomalia_lluvia_semana_iso
dummy_exceso_lluvia_p75
dummy_estres_hidrico_p25
dummy_temp_max_alta_p75
dummy_indice_climatico_bajo_p25
dummy_indice_climatico_alto_p75
```

### 11.3 X económicas de contexto

```text
precio_interno_cop_carga_lag_1s
precio_interno_cop_carga_lag_4s
precio_interno_cop_carga_ma_4s
precio_interno_cop_carga_var_4s
precio_externo_exdock_cent_usd_lb_lag_4s
precio_externo_exdock_cent_usd_lb_ma_4s
precio_externo_exdock_cent_usd_lb_var_4s
exportaciones_mensual_miles_sacos_lag_4s
exportaciones_mensual_miles_sacos_ma_4s
exportaciones_mensual_miles_sacos_var_4s
trm_viernes_cop_usd_lag_4s
trm_viernes_cop_usd_ma_4s
trm_viernes_cop_usd_var_4s
```

---

## 12. Variables que NO deberían usarse como X contra la Y semanal

Aunque están en la base por trazabilidad, estas variables participan en la construcción de la Y o son controles directos. Por tanto, no deberían usarse como predictores de `produccion_semanal_proxy_t`:

```text
produccion_anual_proxy_5mun_t
produccion_anual_depto_mun_t
produccion_nacional_mensual_oficial_miles_sacos
peso_mensual_prod_nacional_principal
produccion_mensual_proxy_principal_t
dias_asignados_semana
detalle_meses_asignados
metodo_y
tipo_target
```

Estas variables se conservan para auditoría, validación y explicación metodológica, pero no como X del modelo semanal principal.

---

## 13. Recomendación de modelamiento

### 13.1 Modelo semanal operacional

Target:

```text
produccion_semanal_proxy_t
```

Uso:

- simulación;
- sensibilidad;
- monitoreo;
- identificación de señales climáticas y económicas;
- soporte para prototipo de seguro indexado.

Interpretación:

> El modelo semanal no predice producción semanal observada, sino variaciones de una proxy operativa construida con producción anual observada, estacionalidad mensual real y asignación calendario.

---

### 13.2 Modelo panel semanal

Target:

```text
produccion_semanal_proxy_t
```

Unidad:

```text
departamento - semana
```

Ventajas:

- más observaciones;
- heterogeneidad territorial;
- posibilidad de incluir efectos por departamento;
- permite validar si las señales climáticas se comportan distinto entre zonas.

---

### 13.3 Modelo anual complementario

Para una validación más estricta, se recomienda un modelo anual complementario.

Targets posibles:

```text
produccion_anual_proxy_5mun_t
rendimiento_proxy_t_ha
produccion_anual_depto_mun_t
rendimiento_depto_mun_t_ha
```

En ese caso, las variables semanales deben agregarse a ventanas anuales o fenológicas:

- lluvia acumulada anual;
- lluvia en semanas críticas;
- humedad promedio trimestral;
- temperatura máxima promedio;
- semanas con exceso de lluvia;
- semanas con estrés hídrico;
- precio interno promedio con rezagos;
- TRM promedio o variación anual.

---

## 14. Diccionario resumido de variables principales

| Variable | Tipo | Descripción | Uso recomendado |
|---|---|---|---|
| `produccion_semanal_proxy_t` | Y proxy | Producción semanal proxy en toneladas | Target semanal |
| `produccion_anual_proxy_5mun_t` | Control / Y anual | Suma anual de los cinco municipios | Target anual o validación |
| `produccion_anual_depto_mun_t` | Control / Y anual panel | Producción anual del municipio representativo del departamento | Target anual panel |
| `produccion_nacional_mensual_oficial_miles_sacos` | Benchmark temporal | Producción mensual nacional usada para estacionalidad | No usar como X semanal |
| `peso_mensual_prod_nacional_principal` | Benchmark temporal | Participación mensual en la producción anual nacional | No usar como X semanal |
| `PRECTOTCORR` | X climática | Precipitación corregida | X central |
| `T2M` | X climática | Temperatura media | X central |
| `T2M_MAX` | X climática | Temperatura máxima | X estrés térmico |
| `GWETTOP` | X climática | Humedad superficial del suelo | X central |
| `GWETROOT` | X climática | Humedad radicular | X central |
| `indice_climatico_base_x` | X derivada | Índice compuesto climático | X explicativa |
| `indice_climatico_ajustado_x` | X derivada | Índice climático suavizado | X explicativa opcional |
| `lluvia_acum_4s` | X derivada | Lluvia acumulada 4 semanas | X con rezago hidrológico |
| `lluvia_acum_8s` | X derivada | Lluvia acumulada 8 semanas | X con rezago hidrológico |
| `precio_interno_cop_carga` | X económica | Precio interno semanal | Usar rezagos/medias |
| `precio_externo_exdock_cent_usd_lb` | X económica | Precio externo mensual asignado a semana | Usar rezagos |
| `exportaciones_mensual_miles_sacos` | X económica | Exportaciones mensuales asignadas a semana | Usar rezagos |
| `trm_viernes_cop_usd` | X económica | TRM viernes o último hábil anterior | Usar rezagos/medias |
| `valor_cosecha_anual_millones_cop` | Financiera | Valor anual de cosecha | Exposición/severidad |

---

## 15. Conclusión metodológica

La versión actual del cubo mejora la defensa del proyecto porque separa claramente la construcción del target de las variables explicativas climáticas.

La Y semanal se construye con:

1. producción anual observada de los municipios seleccionados;
2. estacionalidad mensual nacional observada;
3. regla calendario de días por semana.

Las X climáticas, incluyendo el índice climático base y ajustado, quedan disponibles para modelación sin haber sido usadas para crear la Y.

Esta separación permite correr modelos más robustos y argumentar que cualquier relación encontrada entre clima y producción semanal proxy no fue inducida directamente por la construcción del target.

---

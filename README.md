# Proyecto: Modelo Analítico Climático para Riesgo de Café en Colombia

**README metodológico actualizado**  
**Periodo actual del cubo:** 2021-2024  
**Unidad de análisis:** semana calendario  
**Nivel analítico:** proxy nacional construida desde cinco municipios cafeteros representativos  

---

## 1. Contexto del proyecto

El cultivo de café en Colombia es altamente vulnerable al riesgo climático. La variabilidad en precipitaciones, los excesos de lluvia, los periodos secos, la temperatura y la humedad del suelo pueden afectar floración, desarrollo del fruto, calidad del grano y volumen producido.

Este proyecto busca construir una base analítica semanal que permita estudiar la relación entre condiciones climáticas, producción cafetera y señales económicas, como insumo para un futuro modelo de **seguro agrícola indexado**.

La dificultad principal es que la producción agrícola observada no está disponible semanalmente. Por eso, el proyecto construye una **proxy semanal operacional**, documentando claramente sus supuestos y limitaciones.

---

## 2. Objetivo del proyecto

Construir un cubo de datos semanal, climático, productivo y económico que permita:

- Analizar el comportamiento histórico del clima en zonas cafeteras representativas.
- Construir una proxy semanal de producción cafetera a partir de producción anual observada.
- Identificar señales de exceso de lluvia, estrés hídrico y estrés térmico.
- Incorporar variables económicas de contexto, como precio interno, precio externo, exportaciones, valor de cosecha y TRM.
- Generar insumos para modelos exploratorios de riesgo climático y simulación de un seguro indexado.
- Separar claramente lo que corresponde a **riesgo climático** de lo que corresponde a **impacto económico/financiero**.

---

## 3. Decisión metodológica central: proxy nacional desde cinco municipios

El proyecto no usa directamente la producción nacional oficial como variable objetivo del modelo semanal. En su lugar, se construye una **proxy nacional** a partir de cinco municipios ubicados en departamentos cafeteros relevantes.

| Departamento | Municipio | Latitud | Longitud |
|---|---|---:|---:|
| Antioquia | Fredonia | 5.96 | -75.13 |
| Huila | San Agustín | 1.87 | -76.26 |
| Tolima | Ibagué | 4.36 | -75.07 |
| Caldas | Chinchiná | 4.99 | -75.60 |
| Cauca | Suárez | 2.95 | -76.69 |

### 3.1 Justificación

Estos municipios representan zonas cafeteras con condiciones climáticas diferenciadas y alta relevancia productiva. La intención no es afirmar que estos cinco municipios equivalen perfectamente a Colombia, sino construir una aproximación operativa y trazable para el proyecto.

La lógica es:

> Si el seguro indexado requiere monitoreo climático semanal, se necesita una unidad de análisis compatible con las variables climáticas. Por eso se parte de municipios cafeteros representativos, se agregan sus datos productivos y se construye una proxy nacional consistente con el alcance del proyecto.

Para futuras versiones, una mejora natural será pasar de un modelo proxy nacional a modelos específicos por municipio o departamento.

---

## 4. Fuentes de datos utilizadas

### 4.1 Producción municipal anual

Fuente con producción, área sembrada, área cosechada y rendimiento por municipio. Se usa para construir la base productiva anual de los cinco municipios seleccionados.

### 4.2 Producción nacional mensual oficial

Se usa únicamente como **patrón temporal de estacionalidad mensual**. No se usa como target final ni como reemplazo de la proxy de cinco municipios.

### 4.3 Variables climáticas NASA

Variables semanales consolidadas para la proxy nacional:

| Variable | Descripción |
|---|---|
| `PRECTOTCORR` | Precipitación corregida. |
| `T2M` | Temperatura media a 2 metros. |
| `T2M_MAX` | Temperatura máxima. |
| `T2M_MIN` | Temperatura mínima. |
| `RH2M` | Humedad relativa. |
| `QV2M` | Humedad específica. |
| `GWETTOP` | Humedad superficial del suelo. |
| `GWETROOT` | Humedad en zona radicular. |
| `ALLSKY_SFC_SW_DWN` | Radiación solar de onda corta descendente. |
| `WS2M` | Velocidad del viento. |

### 4.4 Variables económicas y de mercado

| Fuente / variable | Uso principal |
|---|---|
| Precio interno del café | Señal económica local del mercado cafetero. |
| Precio externo Ex-Dock | Señal internacional / externa de precio. |
| Exportaciones | Contexto comercial y validación descriptiva. |
| Valor de cosecha | Exposición financiera y severidad económica. |
| TRM / dólar | Contexto de costos importados, insumos y presión cambiaria. |

---

## 5. Construcción de la variable objetivo semanal `Y`

### 5.1 Nombre recomendado de la Y

La variable objetivo semanal principal del cubo es:

```text
produccion_semanal_proxy_t
```

También puede documentarse como:

```text
Y = produccion_proxy_nacional_semanal_t
```

### 5.2 Interpretación correcta

Esta variable representa la **producción semanal estimada de la proxy nacional**, construida desde los cinco municipios seleccionados.

No representa producción semanal observada real de Colombia.

Interpretación correcta:

> Producción semanal proxy asociada a los cinco municipios cafeteros representativos agregados como aproximación nacional operacional.

Interpretación incorrecta:

> Producción semanal observada de café en Colombia.

---

## 6. Formulación matemática de la Y semanal

### 6.1 Agregación anual de los cinco municipios

Para cada año `a`, se suma la producción anual de los cinco municipios:

$$
P^{proxy}_a = \sum_{m=1}^5 P_{m,a}
$$

Donde:

- $P^{proxy}_a$ es la producción anual agregada de la proxy.
- $P_{m,a}$ es la producción anual observada del municipio $m$ en el año $a$.

---

### 6.2 Peso mensual usando producción nacional oficial

La producción nacional mensual oficial se usa solo para obtener la forma temporal dentro del año:

$$
w^M_{a,j} = \frac{PN_{a,j}}{\sum_{j=1}^{12} PN_{a,j}}
$$

Donde:

- $w^M_{a,j}$ es el peso del mes $j$ en el año $a$.
- $PN_{a,j}$ es la producción nacional oficial del mes $j$ en el año $a$.

La producción mensual proxy queda:

$$
P^{proxy}_{a,j} = P^{proxy}_a \times w^M_{a,j}
$$

---

### 6.3 Índice climático semanal

Para repartir la producción mensual proxy a nivel semanal, se construye un **índice climático semanal suave** a partir de variables NASA. Este índice no pretende estimar la producción real de cada semana, sino asignar mayor o menor participación relativa a las semanas de un mismo mes según condiciones climáticas observadas.

La motivación es la siguiente:

> Si dos semanas pertenecen al mismo mes, pero una presenta mejores condiciones hídricas, térmicas y de radiación, esa semana puede recibir una proporción ligeramente mayor de la producción mensual proxy. Sin embargo, este ajuste debe ser controlado para evitar que la producción semanal quede determinada casi por completo por las mismas variables climáticas que luego se analizarán en el modelo.

Por esta razón, el índice se construye en dos niveles:

1. **Índice climático base:** combina humedad, precipitación, temperatura y radiación.
2. **Índice climático ajustado:** suaviza el índice base para que el clima influya, pero no domine la desagregación semanal.

#### 6.3.1 Normalización min-max

Para las variables que se transforman a escala comparable se utiliza normalización min-max:

$$
minmax(x_s) = \frac{x_s - min(x)}{max(x) - min(x)}
$$

Donde $x_s$ es el valor de la variable en la semana $s$.

Esta transformación lleva las variables a una escala común entre 0 y 1, permitiendo combinarlas en un índice compuesto.

#### 6.3.2 Score de humedad del suelo

La humedad del suelo se construye combinando dos variables NASA:

- `GWETROOT`: humedad en zona radicular.
- `GWETTOP`: humedad superficial del suelo.

La fórmula es:

$$
score_{humedad,s} = \frac{minmax(GWETROOT_s) + minmax(GWETTOP_s)}{2}
$$

La lógica agronómica es que el cultivo de café no depende únicamente de la humedad superficial, sino también de la humedad disponible en la zona de raíces. Por eso se combinan ambas señales.

#### 6.3.3 Score de precipitación

Para la precipitación se utiliza `PRECTOTCORR`. Antes de normalizarla, se controla el efecto de semanas extremadamente lluviosas mediante un tope en el percentil 90:

$$
PRECTOTCORR^{cap}_s = min(PRECTOTCORR_s, P90(PRECTOTCORR))
$$

Luego se normaliza:

$$
score_{precipitacion,s} = minmax(PRECTOTCORR^{cap}_s)
$$

Este tratamiento evita que una semana con lluvia extrema concentre de manera desproporcionada la producción mensual proxy. La lluvia es relevante para el cultivo, pero el exceso de lluvia también puede ser un factor de riesgo; por eso no se asume que más precipitación siempre implica mejores condiciones productivas.

#### 6.3.4 Score de temperatura

Para la temperatura se utiliza `T2M`. A diferencia de otras variables, no se aplica un min-max directo, porque no es correcto asumir que una temperatura más alta siempre es mejor. En café, temperaturas demasiado bajas o demasiado altas pueden generar estrés.

Por eso se premian las semanas cuya temperatura media está más cerca de la mediana histórica del periodo:

$$
ref_{temp} = mediana(T2M)
$$

$$
score_{temperatura,s} = 1 - \frac{|T2M_s - ref_{temp}|}{max(|T2M - ref_{temp}|)}
$$

Interpretación:

- Si la temperatura semanal está cerca de la mediana histórica, el score se acerca a 1.
- Si la temperatura semanal se aleja mucho de la mediana, el score disminuye.
- Esto permite capturar condiciones térmicas relativamente normales sin asumir una relación lineal positiva entre temperatura y producción.

#### 6.3.5 Score de radiación

Para radiación se utiliza `ALLSKY_SFC_SW_DWN`, asociada con radiación solar de onda corta descendente:

$$
score_{radiacion,s} = minmax(ALLSKY\_SFC\_SW\_DWN_s)
$$

La radiación se incluye porque está relacionada con energía disponible para procesos de fotosíntesis y desarrollo del cultivo. Sin embargo, se le asigna un peso menor que a humedad, precipitación y temperatura.

#### 6.3.6 Índice climático base

Una vez calculados los cuatro scores, se combinan con ponderaciones definidas de manera metodológica:

$$
IC_s = 0.35 \cdot score_{humedad,s} + 0.25 \cdot score_{precipitacion,s} + 0.25 \cdot score_{temperatura,s} + 0.15 \cdot score_{radiacion,s}
$$

| Componente | Peso | Justificación |
|---|---:|---|
| Humedad del suelo | 0.35 | Captura disponibilidad hídrica en superficie y raíz. |
| Precipitación | 0.25 | Señal central de exceso o disponibilidad de agua. |
| Temperatura | 0.25 | Relacionada con estrés térmico y condiciones de desarrollo. |
| Radiación | 0.15 | Complementa condiciones de energía/fotosíntesis. |

La suma de pesos es igual a 1:

$$
0.35 + 0.25 + 0.25 + 0.15 = 1
$$

#### 6.3.7 Índice climático ajustado

Después de calcular el índice climático base, se aplica un suavizamiento:

$$
IC^{ajustado}_s = 0.70 + 0.30 \cdot IC_s
$$

Este ajuste tiene una función metodológica importante: evitar que la distribución semanal de la producción dependa excesivamente del clima.

En otras palabras:

- El componente `0.70` garantiza que todas las semanas conserven un peso base.
- El componente `0.30 \cdot IC_s` permite que las condiciones climáticas ajusten parcialmente la distribución.
- El clima influye en la semanalización, pero no la determina por completo.

Esto reduce el riesgo de construir una Y semanal demasiado correlacionada con las mismas variables climáticas que posteriormente serán analizadas como posibles predictores.

La interpretación recomendada es:

> El índice climático no busca estimar directamente la producción semanal observada, sino distribuir de forma controlada la producción mensual proxy entre semanas con base en condiciones climáticas relativas. Para evitar que la producción semanal quede excesivamente determinada por las mismas variables climáticas que luego serán analizadas, se aplica un factor de suavizamiento que conserva un peso base para todas las semanas y limita el ajuste climático al 30%.

---

### 6.4 Peso semanal climático dentro de cada mes

Una vez calculado el índice climático ajustado, se normaliza dentro de cada mes para obtener el peso semanal:

$$
w^S_{a,j,s} = \frac{IC^{ajustado}_{a,j,s}}{\sum_{s \in j} IC^{ajustado}_{a,j,s}}
$$

Donde:

- $w^S_{a,j,s}$ es el peso climático de la semana $s$ dentro del mes $j$.
- $IC^{ajustado}_{a,j,s}$ es el índice climático ajustado de esa semana.
- $\sum_{s \in j} IC^{ajustado}_{a,j,s}$ es la suma del índice ajustado de todas las semanas del mismo mes.

La condición de consistencia es:

$$
\sum_{s \in j} w^S_{a,j,s} = 1
$$

Esto garantiza que la producción mensual proxy se reparta completamente entre las semanas del mes, sin crear ni destruir producción.

---

### 6.5 Producción semanal proxy

La Y semanal queda:

$$
Y_s = P^{proxy}_a \times w^M_{a,j} \times w^S_{a,j,s}
$$

Equivalentemente:

$$
produccion\_semanal\_proxy\_t_s = produccion\_anual\_proxy\_5mun\_t_a \times peso\_mensual\_prod\_nacional_{a,j} \times peso\_semanal\_climatico\_mes_{a,j,s}
$$

---

### 6.6 Validación obligatoria

La suma semanal debe volver al total anual observado de la proxy:

$$
\sum_{s=1}^{52/53} Y_s = P^{proxy}_a
$$

Esta validación es clave para demostrar que la semanalización conserva la producción anual observada.

---

## 7. Advertencias metodológicas que defienden el modelo

La producción semanal proxy es útil para monitoreo y simulación, pero debe interpretarse con cuidado.

### 7.1 La Y semanal no es observada

> La producción observada de café se encuentra disponible a nivel anual para los municipios seleccionados. Para construir una base semanal compatible con las variables climáticas, se implementó una desagregación temporal en dos etapas. Primero, la producción anual municipal se distribuyó mensualmente usando la estructura relativa de la producción nacional mensual oficial. Segundo, la producción mensual estimada se distribuyó a nivel semanal mediante pesos derivados de condiciones climáticas semanales. La variable resultante no representa producción semanal observada, sino una proxy operacional para monitoreo, simulación y análisis exploratorio del seguro indexado.

### 7.2 Riesgo de correlación artificial

Como el clima participa en la construcción de la Y semanal, un modelo que use esas mismas variables climáticas para predecir `produccion_semanal_proxy_t` puede presentar correlaciones artificiales.

Por eso, los modelos semanales se deben presentar como:

> ejercicios exploratorios de simulación, sensibilidad y monitoreo operacional.

Y no como:

> validación causal estricta de producción semanal observada.

### 7.3 Separación recomendada de capas analíticas

| Capa | Variable objetivo | Uso recomendado |
|---|---|---|
| Semanal operacional | `produccion_semanal_proxy_t` | Monitoreo, simulación, alertas y sensibilidad. |
| Anual validable | `produccion_anual_proxy_5mun_t` o `rendimiento_proxy_t_ha` | Validación predictiva más defendible. |
| Financiera | `valor_cosecha_semanal_proxy_millones` | Severidad económica, exposición, estimación de impacto. |

### 7.4 Puente hacia el modelamiento

La construcción anterior define con claridad qué tipo de modelamiento es metodológicamente válido.

#### 7.4.1 Modelo semanal exploratorio

Cuando se modele `produccion_semanal_proxy_t`, el objetivo no debe presentarse como predicción de producción real semanal, sino como un ejercicio de:

- sensibilidad de la proxy frente a variables climáticas;
- monitoreo semanal de condiciones de riesgo;
- identificación de señales tempranas;
- simulación operacional para un posible seguro indexado.

La formulación correcta es:

> Se modela una variable proxy semanal construida para fines de monitoreo y simulación. Por tanto, los resultados indican patrones de sensibilidad y asociación dentro de la proxy, no efectos causales sobre producción semanal observada.

#### 7.4.2 Variables que pueden entrar al modelo semanal

Para el modelo semanal exploratorio, se recomienda priorizar variables climáticas derivadas que no sean exactamente los componentes directos del peso semanal, por ejemplo:

- acumulados de lluvia a 4 y 8 semanas;
- anomalías de lluvia por semana ISO;
- medias móviles de humedad del suelo;
- medias móviles de temperatura máxima;
- dummies de exceso de lluvia, estrés hídrico y temperatura alta;
- rezagos climáticos.

También pueden incluirse variables económicas rezagadas como contexto, por ejemplo precio interno, precio externo, exportaciones y TRM, siempre aclarando que estas variables explican entorno económico y no componen el índice climático principal.

#### 7.4.3 Variables que deben excluirse para evitar leakage

En un modelo semanal con `produccion_semanal_proxy_t` como Y, no deben usarse como predictores las variables que construyen directamente la Y:

```text
produccion_anual_proxy_5mun_t
produccion_nacional_mensual_oficial_miles_sacos
peso_mensual_prod_nacional
produccion_mensual_proxy_t
indice_climatico_base
indice_climatico_ajustado
peso_semanal_climatico_mes
valor_cosecha_semanal_proxy_millones
```

La razón es que el modelo estaría aprendiendo la fórmula de construcción de la variable objetivo y no una relación independiente entre clima y producción.

#### 7.4.4 Modelo anual complementario

Para una validación predictiva más defendible, se recomienda construir un modelo anual complementario usando como target:

```text
produccion_anual_proxy_5mun_t
```

o:

```text
rendimiento_proxy_t_ha
```

En este caso, las variables semanales pueden agregarse a nivel anual o por ventanas críticas:

- lluvia acumulada anual;
- lluvia acumulada en meses de floración;
- humedad promedio en ventanas críticas;
- número de semanas con exceso de lluvia;
- número de semanas con estrés hídrico;
- temperatura máxima promedio en ventanas de riesgo;
- precio interno promedio o rezagado;
- TRM promedio o rezagada.

Este modelo anual es más defendible porque el target sí proviene de información observada anual, no de una desagregación semanal construida.

---

## 8. Tratamiento de variables económicas

Las variables económicas se mantienen en el cubo porque pueden enriquecer el análisis financiero y contextual, pero no deben confundirse con las variables centrales del índice climático.

### 8.1 Precio interno

El precio interno puede reflejar oferta, demanda, tasa de cambio, expectativas, calidad y condiciones del mercado. Puede subir cuando hay restricciones de oferta, pero no debe afirmarse que siempre sube únicamente porque baja la producción.

Uso recomendado:

- `precio_interno_cop_carga_lag_1s`
- `precio_interno_cop_carga_lag_4s`
- `precio_interno_cop_carga_ma_4s`
- `precio_interno_cop_carga_var_4s`
- `dummy_precio_interno_alto_p75`

### 8.2 Precio externo

El precio externo se conserva como variable internacional de contexto. Al ser mensual, se asigna a las semanas del mes correspondiente.

Uso recomendado:

- `precio_externo_exdock_lag_4s`
- `precio_externo_exdock_ma_4s`
- `precio_externo_exdock_var_4s`
- `dummy_precio_externo_alto_p75`

### 8.3 Exportaciones

Las exportaciones se usan como variable contextual de mercado, no como causa directa de la producción semanal. Pueden estar afectadas por inventarios, logística, demanda externa y decisiones comerciales.

Uso recomendado:

- `exportaciones_mensual_miles_sacos_lag_4s`
- `exportaciones_mensual_miles_sacos_ma_4s`
- `exportaciones_mensual_miles_sacos_var_4s`
- `dummy_exportaciones_altas_p75`

### 8.4 Valor de cosecha

El valor de cosecha se usa para traducir producción proxy a exposición económica. Es especialmente útil para escenarios de pérdida, severidad y diseño financiero del seguro.

### 8.5 TRM / dólar

La TRM se propone como variable adicional por su relación con insumos importados como fertilizantes, agroquímicos, maquinaria o repuestos.

Tratamiento recomendado:

1. Descargar TRM diaria oficial.
2. Tomar el valor del viernes de cada semana.
3. Si no existe valor para el viernes, usar el último dato disponible anterior.
4. Construir rezagos, medias móviles, variaciones y dummies.

Variables sugeridas:

| Variable | Descripción | Uso |
|---|---|---|
| `trm_viernes_cop_usd` | TRM del viernes o último dato disponible anterior. | Contexto económico. |
| `trm_promedio_semana_cop_usd` | Promedio semanal de TRM. | Alternativa suavizada. |
| `trm_viernes_cop_usd_lag_1s` | TRM rezagada 1 semana. | Evita simultaneidad. |
| `trm_viernes_cop_usd_lag_4s` | TRM rezagada 4 semanas. | Hipótesis de costos de insumos. |
| `trm_viernes_cop_usd_ma_4s` | Media móvil 4 semanas. | Suavización. |
| `trm_viernes_cop_usd_var_4s` | Variación a 4 semanas. | Choque cambiario. |
| `dummy_trm_alta_p75` | TRM por encima del percentil 75. | Presión cambiaria alta. |
| `dummy_devaluacion_4s_p75` | Devaluación a 4 semanas por encima del percentil 75. | Choque de devaluación. |
| `dummy_trm_lag4_alta_p75` | TRM alta rezagada 4 semanas. | Hipótesis de encarecimiento de insumos. |

---

## 9. Fases lunares

Se incorporan variables lunares como variables exploratorias:

- `fase_lunar_fraccion_aprox`
- `fase_lunar_categoria`
- `dummy_luna_nueva`
- `dummy_luna_llena`
- `dummy_luna_creciente`
- `dummy_luna_menguante`

Estas variables no se usan para construir la Y. Se mantienen únicamente como hipótesis exploratoria porque existen prácticas agrícolas tradicionales asociadas al calendario lunar, pero no se recomienda que sean el fundamento central del modelo ni del seguro indexado.

---

## 10. Variables recomendadas para modelamiento

### 10.1 Variables de riesgo climático central

Estas son las más alineadas con el seguro indexado:

```text
PRECTOTCORR
T2M
T2M_MAX
T2M_MIN
RH2M
QV2M
GWETTOP
GWETROOT
ALLSKY_SFC_SW_DWN
WS2M
lluvia_acum_4s
lluvia_acum_8s
t2m_max_ma_4s
gwetroot_ma_4s
gwettop_ma_4s
anomalia_lluvia_semana_iso
dummy_exceso_lluvia_p75
dummy_estres_hidrico_p25
dummy_temp_max_alta_p75
```

### 10.2 Variables económicas de contexto

Estas explican entorno económico, exposición y mercado, pero no deberían ser el núcleo del índice climático:

```text
precio_interno_cop_carga_lag_1s
precio_interno_cop_carga_lag_4s
precio_interno_cop_carga_ma_4s
precio_interno_cop_carga_var_4s
precio_externo_exdock_lag_4s
precio_externo_exdock_ma_4s
precio_externo_exdock_var_4s
exportaciones_mensual_miles_sacos_lag_4s
exportaciones_mensual_miles_sacos_ma_4s
exportaciones_mensual_miles_sacos_var_4s
trm_viernes_cop_usd_lag_4s
trm_viernes_cop_usd_ma_4s
trm_viernes_cop_usd_var_4s
dummy_trm_lag4_alta_p75
dummy_devaluacion_4s_p75
```

### 10.3 Variables de trazabilidad o construcción que NO deben usarse como X en un modelo semanal

Estas variables construyen la Y o documentan la metodología. Usarlas como predictor directo puede generar leakage:

```text
produccion_anual_proxy_5mun_t
produccion_nacional_mensual_oficial_miles_sacos
peso_mensual_prod_nacional
produccion_mensual_proxy_t
indice_climatico_base
indice_climatico_ajustado
peso_semanal_climatico_mes
valor_cosecha_semanal_proxy_millones
fuente_produccion
tipo_target
```

---

## 11. Diccionario de variables del cubo semanal

| Variable | Grupo | Descripción | Uso sugerido |
|---|---|---|---|
| `fecha_semana` | Identificación temporal | Fecha de cierre o referencia de la semana. | Llave temporal; no usar como predictor directo salvo para crear tendencia/estacionalidad. |
| `anio` | Identificación temporal | Año calendario de la observación. | Útil para validación temporal y partición train/test. |
| `mes` | Identificación temporal | Mes calendario de la observación. | Útil para estacionalidad; puede codificarse como variable cíclica. |
| `semana_iso` | Identificación temporal | Número de semana ISO. | Útil para estacionalidad semanal; no representa causalidad. |
| `anio_iso` | Identificación temporal | Año ISO asociado a la semana. | Control temporal. |
| `produccion_anual_proxy_5mun_t` | Producción / proxy | Producción anual agregada de los cinco municipios seleccionados, en toneladas. | No usar como X si el target semanal deriva de esta variable; sirve para validación anual. |
| `area_sembrada_proxy_ha` | Producción / proxy | Área sembrada agregada de los cinco municipios, en hectáreas. | Variable estructural; posible control anual. |
| `area_cosechada_proxy_ha` | Producción / proxy | Área cosechada agregada de los cinco municipios, en hectáreas. | Variable estructural; posible control anual. |
| `rendimiento_proxy_t_ha` | Producción / proxy | Rendimiento anual proxy calculado como producción anual proxy / área cosechada proxy. | Target alternativo anual más defendible. |
| `produccion_nacional_mensual_oficial_miles_sacos` | Guía temporal oficial | Producción nacional mensual oficial, en miles de sacos, usada como patrón de estacionalidad. | No usar como target de la proxy; sirve solo para mensualizar. |
| `peso_mensual_prod_nacional` | Peso de desagregación | Participación de cada mes en la producción nacional anual oficial. | Insumo de construcción de la Y; no usar como X en el modelo semanal. |
| `produccion_mensual_proxy_t` | Producción / proxy | Producción mensual proxy resultante de repartir la producción anual de los 5 municipios según el peso mensual nacional. | Variable intermedia de construcción del target. |
| `indice_climatico_base` | Índice climático | Índice compuesto a partir de humedad, precipitación, temperatura y radiación normalizadas. | Insumo de construcción del peso semanal; no usar sin cuidado para predecir la Y semanal. |
| `indice_climatico_ajustado` | Índice climático | Índice climático suavizado: 0.70 + 0.30 * índice climático base. | Insumo de construcción del target; evitar como X principal del modelo semanal. |
| `peso_semanal_climatico_mes` | Peso de desagregación | Peso climático semanal normalizado dentro de cada mes. | Insumo directo de la Y; no usar como predictor del target semanal. |
| `produccion_semanal_proxy_t` | Target semanal | Producción semanal proxy nacional construida desde los cinco municipios, en toneladas. | Y semanal principal para simulación/monitoreo; no es producción observada. |
| `valor_cosecha_anual_millones` | Económica / valorización | Valor anual de la cosecha, en millones de pesos. | Variable de valoración financiera; posible exposición económica anual. |
| `valor_cosecha_semanal_proxy_millones` | Económica / valorización | Valor semanal proxy distribuido según la producción semanal proxy. | No usar como X para explicar producción; útil para severidad económica. |
| `precio_interno_cop_carga` | Económica / mercado | Precio interno del café en COP por carga. | Variable económica de contexto; preferir rezagos y medias móviles. |
| `precio_externo_exdock` | Económica / mercado | Precio externo Ex-Dock asignado al mes correspondiente. | Variable económica de contexto; preferir rezagos. |
| `exportaciones_mensual_miles_sacos` | Económica / mercado | Exportaciones mensuales de café, en miles de sacos, asignadas a las semanas del mes. | Contextual; evitar interpretación causal contemporánea. |
| `fuente_produccion` | Trazabilidad | Etiqueta de fuente o metodología de construcción de producción. | No usar como predictor; documentación. |
| `tipo_target` | Trazabilidad | Etiqueta que identifica si el target es proxy/observado/estimado. | No usar como predictor; documentación. |
| `PRECTOTCORR` | Climática / riesgo | Precipitación semanal corregida NASA/MERRA-2. | Predictor climático central. |
| `T2M` | Climática / riesgo | Temperatura media semanal a 2 metros. | Predictor climático central. |
| `T2M_MAX` | Climática / riesgo | Temperatura máxima semanal a 2 metros. | Predictor de estrés térmico. |
| `T2M_MIN` | Climática / riesgo | Temperatura mínima semanal a 2 metros. | Predictor de condiciones frías/variabilidad térmica. |
| `RH2M` | Climática / riesgo | Humedad relativa semanal a 2 metros. | Predictor de ambiente húmedo y posibles enfermedades. |
| `QV2M` | Climática / riesgo | Humedad específica semanal a 2 metros. | Predictor complementario de humedad atmosférica. |
| `GWETTOP` | Climática / riesgo | Humedad superficial del suelo. | Predictor de saturación/encharcamiento superficial. |
| `GWETROOT` | Climática / riesgo | Humedad en zona radicular. | Predictor central de estrés hídrico o exceso de humedad. |
| `ALLSKY_SFC_SW_DWN` | Climática / riesgo | Radiación solar de onda corta descendente. | Predictor de energía disponible/fotosíntesis. |
| `WS2M` | Climática / riesgo | Velocidad del viento a 2 metros. | Predictor complementario; menor prioridad. |
| `score_humedad` | Score climático | Score normalizado de humedad del suelo superficial y radicular. | Usado para construir índice; evitar como X si ya se usa la Y semanal proxy. |
| `score_precipitacion` | Score climático | Score normalizado de precipitación con control de extremos. | Usado para construir índice; evitar como X si ya se usa la Y semanal proxy. |
| `score_temperatura` | Score climático | Score de cercanía de temperatura a un valor de referencia. | Usado para construir índice; evitar como X si ya se usa la Y semanal proxy. |
| `score_radiacion` | Score climático | Score normalizado de radiación solar. | Usado para construir índice; evitar como X si ya se usa la Y semanal proxy. |
| `fase_lunar_fraccion_aprox` | Exploratoria | Fracción aproximada del ciclo lunar. | Hipótesis exploratoria; no usada para construir la Y. |
| `fase_lunar_categoria` | Exploratoria | Categoría aproximada de fase lunar. | Exploratoria; usar solo si se quiere probar hipótesis no central. |
| `dummy_luna_nueva` | Exploratoria | Indicador de luna nueva aproximada. | Variable experimental; baja prioridad. |
| `dummy_luna_llena` | Exploratoria | Indicador de luna llena aproximada. | Variable experimental; baja prioridad. |
| `dummy_luna_creciente` | Exploratoria | Indicador de fase creciente aproximada. | Variable experimental; baja prioridad. |
| `dummy_luna_menguante` | Exploratoria | Indicador de fase menguante aproximada. | Variable experimental; baja prioridad. |
| `precio_interno_cop_carga_lag_1s` | Económica transformada | Precio interno rezagado 1 semana. | Mejor que el contemporáneo para evitar simultaneidad. |
| `precio_interno_cop_carga_lag_4s` | Económica transformada | Precio interno rezagado 4 semanas. | Buen predictor económico de contexto. |
| `precio_interno_cop_carga_ma_4s` | Económica transformada | Media móvil de 4 semanas del precio interno. | Suaviza ruido semanal. |
| `precio_interno_cop_carga_var_4s` | Económica transformada | Variación porcentual del precio interno frente a 4 semanas atrás. | Captura presión/choques de mercado. |
| `precio_externo_exdock_lag_1s` | Económica transformada | Precio externo rezagado 1 semana. | Contexto de mercado internacional. |
| `precio_externo_exdock_lag_4s` | Económica transformada | Precio externo rezagado 4 semanas. | Contexto internacional con rezago. |
| `precio_externo_exdock_ma_4s` | Económica transformada | Media móvil 4 semanas del precio externo. | Contexto internacional suavizado. |
| `precio_externo_exdock_var_4s` | Económica transformada | Variación del precio externo frente a 4 semanas atrás. | Choque internacional de precio. |
| `exportaciones_mensual_miles_sacos_lag_1s` | Económica transformada | Exportaciones rezagadas 1 semana. | Contexto comercial; cuidado con causalidad. |
| `exportaciones_mensual_miles_sacos_lag_4s` | Económica transformada | Exportaciones rezagadas 4 semanas. | Contexto comercial mensual. |
| `exportaciones_mensual_miles_sacos_ma_4s` | Económica transformada | Media móvil 4 semanas de exportaciones. | Contexto comercial suavizado. |
| `exportaciones_mensual_miles_sacos_var_4s` | Económica transformada | Variación de exportaciones frente a 4 semanas atrás. | Cambio comercial reciente. |
| `lluvia_acum_4s` | Climática derivada | Precipitación acumulada en las últimas 4 semanas. | Predictor climático recomendado. |
| `lluvia_acum_8s` | Climática derivada | Precipitación acumulada en las últimas 8 semanas. | Predictor climático recomendado. |
| `t2m_max_ma_4s` | Climática derivada | Media móvil 4 semanas de temperatura máxima. | Predictor de estrés térmico persistente. |
| `gwetroot_ma_4s` | Climática derivada | Media móvil 4 semanas de humedad radicular. | Predictor recomendado de condición hídrica. |
| `gwettop_ma_4s` | Climática derivada | Media móvil 4 semanas de humedad superficial. | Predictor recomendado de saturación superficial. |
| `anomalia_lluvia_semana_iso` | Climática derivada | Diferencia entre lluvia semanal y promedio histórico de esa semana ISO. | Predictor recomendado de anomalía climática. |
| `dummy_exceso_lluvia_p75` | Dummy climática | 1 si la lluvia semanal supera el percentil 75 del periodo. | Variable recomendada para riesgo de exceso de lluvia. |
| `dummy_estres_hidrico_p25` | Dummy climática | 1 si la humedad radicular está por debajo del percentil 25. | Variable recomendada para riesgo de sequía/estrés hídrico. |
| `dummy_temp_max_alta_p75` | Dummy climática | 1 si la temperatura máxima supera el percentil 75. | Variable recomendada para estrés térmico. |
| `dummy_precio_interno_alto_p75` | Dummy económica | 1 si el precio interno supera el percentil 75. | Contexto económico; no causal por sí sola. |
| `dummy_precio_externo_alto_p75` | Dummy económica | 1 si el precio externo supera el percentil 75. | Contexto internacional. |
| `dummy_exportaciones_altas_p75` | Dummy económica | 1 si exportaciones superan el percentil 75. | Contexto comercial. |

---

## 12. Recomendaciones de modelamiento

### 12.1 Modelo semanal exploratorio

Target:

```text
produccion_semanal_proxy_t
```

Uso:

- simulación;
- sensibilidad;
- alertas;
- monitoreo operacional;
- explicación exploratoria del comportamiento de la proxy.

Advertencia:

> No debe presentarse como predicción causal de producción semanal observada.

### 12.2 Modelo anual más defendible

Targets alternativos:

```text
produccion_anual_proxy_5mun_t
rendimiento_proxy_t_ha
```

Uso:

- validación predictiva más fuerte;
- comparación de años;
- relación entre clima acumulado/rezagado y desempeño productivo.

### 12.3 Clasificación de riesgo

También puede construirse un target de clasificación, por ejemplo:

```text
riesgo_alto_produccion = 1 si produccion_semanal_proxy_t está por debajo del percentil 25
riesgo_alto_produccion = 0 en caso contrario
```

O un target climático puro:

```text
riesgo_climatico = 1 si hay exceso de lluvia, estrés hídrico o temperatura alta
riesgo_climatico = 0 en caso contrario
```

Este segundo enfoque puede ser más coherente con un seguro indexado, porque el pago depende de un índice climático observable y no de una producción semanal no observada.

---

## 13. Prompt recomendado para pedir modelamiento a otro motor

```text
Estoy trabajando en un proyecto de seguro agrícola indexado para café en Colombia. Tengo una base semanal de 2021 a 2024 construida como una proxy nacional a partir de cinco municipios cafeteros representativos: Fredonia (Antioquia), San Agustín (Huila), Ibagué (Tolima), Chinchiná (Caldas) y Suárez (Cauca).

La variable objetivo semanal principal es `produccion_semanal_proxy_t`. Esta Y no es producción semanal observada, sino una proxy operacional. Se construyó así: primero se sumó la producción anual observada de los cinco municipios; luego se mensualizó usando la estacionalidad de la producción nacional mensual oficial; finalmente se semanalizó usando un índice climático suave construido con variables NASA. Por esta razón, cualquier modelo semanal debe interpretarse como simulación, sensibilidad o monitoreo operacional, no como validación causal estricta.

Quiero que me ayudes a proponer modelos y variables, separando tres grupos:

1. Variables de riesgo climático central, que sí deberían ser el corazón del seguro indexado: `PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `QV2M`, `GWETTOP`, `GWETROOT`, `ALLSKY_SFC_SW_DWN`, `WS2M`, `lluvia_acum_4s`, `lluvia_acum_8s`, `t2m_max_ma_4s`, `gwetroot_ma_4s`, `gwettop_ma_4s`, `anomalia_lluvia_semana_iso`, `dummy_exceso_lluvia_p75`, `dummy_estres_hidrico_p25`, `dummy_temp_max_alta_p75`.

2. Variables económicas de contexto, útiles para explicar exposición financiera o entorno de mercado, pero no como núcleo del índice climático: `precio_interno_cop_carga_lag_1s`, `precio_interno_cop_carga_lag_4s`, `precio_interno_cop_carga_ma_4s`, `precio_interno_cop_carga_var_4s`, `precio_externo_exdock_lag_4s`, `precio_externo_exdock_ma_4s`, `precio_externo_exdock_var_4s`, `exportaciones_mensual_miles_sacos_lag_4s`, `exportaciones_mensual_miles_sacos_ma_4s`, `exportaciones_mensual_miles_sacos_var_4s`, y si está disponible, TRM con `trm_viernes_cop_usd_lag_4s`, `trm_viernes_cop_usd_ma_4s`, `trm_viernes_cop_usd_var_4s`, `dummy_trm_lag4_alta_p75`, `dummy_devaluacion_4s_p75`.

3. Variables que NO deben usarse como X para predecir la Y semanal porque participan en su construcción o pueden causar leakage: `produccion_anual_proxy_5mun_t`, `produccion_nacional_mensual_oficial_miles_sacos`, `peso_mensual_prod_nacional`, `produccion_mensual_proxy_t`, `indice_climatico_base`, `indice_climatico_ajustado`, `peso_semanal_climatico_mes`, `valor_cosecha_semanal_proxy_millones`, `fuente_produccion`, `tipo_target`.

Necesito que propongas: modelos candidatos, estrategia de validación temporal, métricas, tratamiento de leakage, selección de variables, y cómo presentar resultados sin afirmar que la Y semanal es observada. También quiero una alternativa de modelo anual usando `produccion_anual_proxy_5mun_t` o `rendimiento_proxy_t_ha` como target para una validación más defendible.
```

---

## 14. Estructura sugerida del repositorio

```text
proyecto-cafe-seguro-indexado/
│
├── data/
│   ├── raw/
│   │   └── Variables_cafe_seguro_agricola.xlsx
│   ├── processed/
│   │   ├── base_semanal_proxy_cafe_2021_2024.csv
│   │   └── base_semanal_proxy_cafe_2021_2024_con_trm.csv
│   └── outputs/
│
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_construccion_proxy_semanal.ipynb
│   ├── 03_modelo_exploratorio_semanal.ipynb
│   └── 04_modelo_anual_validable.ipynb
│
├── scripts/
│   ├── construccion_base_proxy_cafe.py
│   └── agregar_trm_base_proxy_cafe.py
│
├── README.md
└── requirements.txt
```

---

## 15. Próximos pasos

1. Integrar TRM semanal y sus transformaciones.
2. Revisar valores faltantes y cobertura de variables por año.
3. Realizar análisis exploratorio de correlaciones con advertencia de leakage.
4. Entrenar un modelo semanal exploratorio con validación temporal.
5. Construir un modelo anual complementario más defendible.
6. Diseñar un índice climático de pago para seguro indexado.
7. Separar resultados en tres capas: riesgo climático, producción proxy y exposición financiera.

---

## 16. Conclusión

Este repositorio documenta la construcción de un cubo semanal para analizar riesgo climático en café. La principal contribución metodológica es la construcción de una **proxy nacional semanal** a partir de cinco municipios cafeteros representativos, combinando producción anual observada, estacionalidad mensual nacional oficial y ajuste climático semanal.

El cubo permite avanzar hacia modelos exploratorios de monitoreo y simulación, pero conserva una advertencia metodológica central: la producción semanal es una proxy construida, no una variable observada. Por esa razón, la validación predictiva más robusta debe complementarse con modelos anuales y con un índice climático independiente para el diseño del seguro indexado.

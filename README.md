# Proyecto: Modelo Analítico Climático para Riesgo de Café en Colombia

## 1. Enfoque general del proyecto

Este repositorio documenta el desarrollo de un artefacto analítico para apoyar el diseño, monitoreo y simulación de un seguro agrícola indexado para café en Colombia.

El proyecto integra información productiva, climática y económica con el fin de construir una base analítica trazable que permita:

- analizar el comportamiento climático en zonas cafeteras representativas;
- aproximar una variable productiva semanal útil para monitoreo operativo;
- construir variables explicativas climáticas, económicas y estructurales;
- comparar modelos en diferentes frecuencias de análisis;
- apoyar decisiones relacionadas con riesgo, primas, exposición, sensibilidad y posibles triggers de un seguro indexado.

El punto de partida metodológico es que, en contextos agroclimáticos con información productiva observada a baja frecuencia, la solución no debe depender de un único modelo perfecto. En su lugar, se propone una arquitectura analítica por capas que combine consistencia estadística, utilidad operativa, trazabilidad metodológica y lectura de negocio.

---

## 2. Objetivo del repositorio

Construir y documentar un cubo de datos climático-productivo-económico para café, con foco en el periodo 2021-2024, que permita desarrollar modelos exploratorios y operativos para un seguro agrícola indexado.

El repositorio busca responder preguntas como:

- ¿Cómo se puede armonizar producción anual con variables climáticas semanales?
- ¿Qué variables climáticas explican mejor el riesgo productivo del café?
- ¿Qué papel tienen variables económicas como precio interno, precio externo, exportaciones y TRM?
- ¿Qué frecuencia de modelamiento es más útil: semanal, mensual o anual?
- ¿Cómo evitar leakage al construir una variable objetivo semanal no observada directamente?
- ¿Cómo convertir el modelo en un artefacto útil para monitoreo, simulación y apoyo a decisiones de aseguramiento?

---

## 3. Diseño territorial del proyecto

El proyecto utiliza cinco municipios cafeteros representativos ubicados en cinco departamentos relevantes para la producción de café en Colombia.

| Departamento | Municipio representativo | Rol dentro del proyecto |
|-------------|--------------------------|--------------------------|
| Antioquia   | Fredonia                 | Zona cafetera representativa |
| Huila       | San Agustín              | Zona cafetera representativa |
| Tolima      | Ibagué                   | Zona cafetera representativa |
| Caldas      | Chinchiná                | Zona cafetera representativa |
| Cauca       | Suárez                   | Zona cafetera representativa |

La lógica no es afirmar que estos cinco municipios representan perfectamente toda la producción nacional, sino construir una proxy nacional operativa a partir de zonas cafeteras estratégicas, con condiciones climáticas heterogéneas y relevancia productiva.

En futuras versiones, el artefacto puede escalar hacia modelos específicos por municipio, finca, zona agroclimática o región cafetera. Para esta versión, la prioridad es construir una base consistente, explicable y defendible para modelamiento inicial.

---

## 4. Arquitectura general de datos

El proyecto organiza la información en dos estructuras principales y tres frecuencias de trabajo.

### 4.1 Cubos principales

1. **Base proxy nacional semanal**

   Una fila por semana. Se construye agregando la producción de los cinco municipios/departamentos seleccionados y usando el consolidado climático proxy nacional.

2. **Base panel departamental semanal**

   Una fila por departamento-semana. Se conserva el departamento como identificador territorial, dado que cada departamento está asociado al municipio representativo definido en el diseño del proyecto.

### 4.2 Frecuencias de análisis

Para la fase de experimentación se trabaja con tres frecuencias:

- **Semanal:** capa operativa para monitoreo, sensibilidad y simulación.
- **Mensual:** capa intermedia para balancear consistencia productiva y utilidad operativa.
- **Anual:** capa de contraste metodológico y validación más agregada.

La frecuencia semanal permite mayor detalle operativo, pero la Y no es observada directamente. La frecuencia mensual ofrece un equilibrio entre detalle temporal y estabilidad. La frecuencia anual permite contrastar resultados con el nivel de observación productiva original, aunque con menos registros.

---

## 5. Fuentes y tipos de variables

### 5.1 Variables productivas

Provienen de fuentes de producción agrícola disponibles a nivel anual para los municipios seleccionados. Se utilizan para construir la variable objetivo proxy.

Variables principales:

- `produccion_anual_departamental_t`
- `produccion_anual_proxy_5mun_t`
- `produccion_mensual_proxy_t`
- `produccion_semanal_proxy_t`
- `area_cosechada_departamental_ha`
- `rendimiento_departamental_t_ha`
- `valor_cosecha_anual_millones`

### 5.2 Variables climáticas NASA

Variables climáticas semanales extraídas y consolidadas desde NASA POWER.

| Variable | Descripción general | Tipo de agregación sugerida |
|----------|---------------------|-----------------------------|
| `PRECTOTCORR` | Precipitación corregida | Flujo / acumulación |
| `IMERG_PRECTOT` | Precipitación IMERG | Flujo / acumulación |
| `T2M` | Temperatura media a 2 metros | Estado / promedio |
| `T2M_MAX` | Temperatura máxima | Estado / promedio o máximo |
| `T2M_MIN` | Temperatura mínima | Estado / promedio o mínimo |
| `RH2M` | Humedad relativa | Estado / promedio |
| `QV2M` | Humedad específica | Estado / promedio |
| `GWETTOP` | Humedad superficial del suelo | Estado / promedio |
| `GWETROOT` | Humedad en zona radicular | Estado / promedio |
| `ALLSKY_SFC_SW_DWN` | Radiación solar de onda corta | Estado / promedio |
| `WS2M` | Velocidad del viento | Estado / promedio |

### 5.3 Variables económicas y de mercado

Estas variables se incorporan como contexto económico y financiero. No son el núcleo climático del seguro, pero pueden ayudar a explicar exposición, condiciones de mercado y sensibilidad económica.

Variables principales:

- `precio_interno_cop_carga`
- `precio_externo_exdock_cent_usd_lb`
- `exportaciones_mensual_miles_sacos`
- `trm_viernes_cop_usd`
- `trm_ultimo_dia_semana_cop_usd`

La TRM se incorpora como variable económica de contexto. En la base se conserva el nombre `trm_viernes_cop_usd` por compatibilidad con versiones previas, pero metodológicamente representa la TRM vigente al cierre de la semana o último día disponible de la semana.

---

## 6. Construcción de la variable objetivo semanal

### 6.1 Target principal

La variable objetivo principal de la base semanal es:

```text
produccion_semanal_proxy_t
```

Esta variable **no representa producción semanal observada**. Es una proxy operativa construida a partir de:

1. producción anual observada de los municipios seleccionados;
2. estacionalidad mensual nacional observada;
3. una regla de asignación semanal por calendario.

Su uso principal es operativo: monitoreo, simulación, sensibilidad y modelamiento exploratorio del artefacto de seguro indexado.

---

### 6.2 Mensualización de la producción anual

Para cada año `a`, la producción anual observada de los cinco municipios se agrega como:

$$
P^{proxy}_{a} = \sum_{d=1}^{5} P_{d,a}
$$

Donde:

- $P^{proxy}_{a}$ es la producción anual de la proxy nacional.
- $P_{d,a}$ es la producción anual del departamento o municipio representativo `d` en el año `a`.

Luego se calcula el peso mensual nacional observado:

$$
w_{a,m} = \frac{PN_{a,m}}{\sum_{m=1}^{12} PN_{a,m}}
$$

Donde:

- $PN_{a,m}$ es la producción nacional mensual oficial en el año `a` y mes `m`.
- $w_{a,m}$ representa la participación del mes dentro de la producción anual nacional.

La producción mensual proxy nacional se define como:

$$
P^{proxy}_{a,m} = P^{proxy}_{a} \times w_{a,m}
$$

Para el panel departamental, la producción mensual se calcula como:

$$
P_{d,a,m} = P_{d,a} \times w_{a,m}
$$

Esta decisión permite que cada departamento conserve su producción anual observada, pero tome la forma mensual de la estacionalidad nacional observada.

---

### 6.3 Semanalización por calendario

Para construir la Y semanal, se distribuye cada producción mensual entre los días del mes y luego se asigna a semanas ISO según la cantidad de días de cada semana que caen dentro del mes correspondiente.

$$
P^{proxy}_{s} = \sum_{k \in s} \frac{P^{proxy}_{a(k),m(k)}}{D_{a(k),m(k)}}
$$

Donde:

- `s` es la semana ISO.
- `k` es cada día dentro de la semana.
- `a(k)` es el año del día `k`.
- `m(k)` es el mes del día `k`.
- `D_{a,m}` es el número de días del mes correspondiente.

Esta regla preserva exactamente los totales mensuales y anuales, sin utilizar información climática para construir la Y.

En palabras simples:

> La producción mensual proxy se reparte por días calendario y cada semana recibe la suma de los días que le corresponden.

---

## 7. Por qué no se usa el clima para construir la Y

Inicialmente se evaluó usar un índice climático semanal para distribuir la producción mensual entre semanas. Sin embargo, esa alternativa fue descartada para evitar **leakage metodológico**.

Si el clima se usa para construir la Y semanal y luego esas mismas variables climáticas se usan como X, el modelo podría encontrar una correlación artificial inducida por el propio proceso de construcción del target.

Por esta razón, la semanalización final se hace por calendario. El clima queda reservado como conjunto de variables explicativas limpias del modelo.

La decisión metodológica puede resumirse así:

> Para construir la variable objetivo semanal, se mantuvo la mensualización basada en la estacionalidad mensual nacional observada y se reemplazó la semanalización climática por una regla de desagregación temporal no climática. En particular, la producción mensual proxy se distribuye a semanas ISO usando pesos de calendario definidos por la proporción de días de cada semana que caen dentro del mes correspondiente, preservando exactamente los totales mensuales. Esta decisión metodológica permite evitar leakage con las variables climáticas semanales, las cuales quedan reservadas como covariables explicativas del modelo. En consecuencia, la serie semanal resultante debe interpretarse como una proxy operativa para simulación, monitoreo y sensibilidad del artefacto, y no como producción semanal observada.

---

## 8. Índice climático como variable explicativa

Aunque el índice climático no se utiliza para construir la Y, se conserva como una variable explicativa derivada. Su objetivo es sintetizar información de humedad, precipitación, temperatura y radiación en una señal climática agregada.

En la base aparecen dos variables principales:

```text
indice_climatico_base_x
indice_climatico_ajustado_x
```

Ambas se interpretan como X o variables explicativas, no como parte del target.

---

### 8.1 Normalización min-max

Para algunas variables se usa normalización min-max:

$$
minmax(x_s) = \frac{x_s - min(x)}{max(x) - min(x)}
$$

Esto transforma las variables a una escala comparable entre 0 y 1.

---

### 8.2 Score de humedad

Se usan dos variables de humedad del suelo:

- `GWETROOT`: humedad en zona radicular.
- `GWETTOP`: humedad superficial del suelo.

$$
score\_humedad_s = \frac{minmax(GWETROOT_s) + minmax(GWETTOP_s)}{2}
$$

La lógica es capturar tanto la humedad superficial como la humedad disponible en la zona de raíces, relevante para el cultivo de café.

---

### 8.3 Score de precipitación

La precipitación se calcula con `PRECTOTCORR`. Antes de normalizar, se aplica un cap al percentil 90 para evitar que semanas extremadamente lluviosas dominen el índice.

$$
PRECTOTCORR^{cap}_s = min(PRECTOTCORR_s, P90(PRECTOTCORR))
$$

$$
score\_precipitacion_s = minmax(PRECTOTCORR^{cap}_s)
$$

Esto reconoce que la lluvia puede ser favorable hasta cierto punto, pero que valores extremos no deben incrementar indefinidamente el score climático.

---

### 8.4 Score de temperatura

La temperatura se evalúa respecto a la mediana histórica de `T2M`.

$$
score\_temperatura_s = 1 - \frac{|T2M_s - mediana(T2M)|}{max(|T2M - mediana(T2M)|)}
$$

Esta formulación evita asumir que una mayor temperatura siempre es mejor. Las semanas con temperatura cercana a la mediana reciben mayor score; las semanas con temperaturas muy alejadas reciben menor score.

---

### 8.5 Score de radiación

La radiación se calcula a partir de `ALLSKY_SFC_SW_DWN`:

$$
score\_radiacion_s = minmax(ALLSKY\_SFC\_SW\_DWN_s)
$$

La radiación se incluye por su relación con fotosíntesis y desarrollo del cultivo, aunque con menor peso que humedad, precipitación y temperatura.

---

### 8.6 Índice climático base

El índice climático base combina los cuatro scores:

$$
IC_s = 0.35 \cdot score\_humedad_s + 0.25 \cdot score\_precipitacion_s + 0.25 \cdot score\_temperatura_s + 0.15 \cdot score\_radiacion_s
$$

Pesos utilizados:

| Componente | Peso |
|-----------|-----:|
| Humedad del suelo | 0.35 |
| Precipitación | 0.25 |
| Temperatura | 0.25 |
| Radiación | 0.15 |

En la base se llama:

```text
indice_climatico_base_x
```

---

### 8.7 Índice climático ajustado

El índice ajustado suaviza el índice base:

$$
IC^{ajustado}_s = 0.70 + 0.30 \cdot IC_s
$$

En la base se llama:

```text
indice_climatico_ajustado_x
```

En esta versión, el índice ajustado no se usa para repartir producción. Se conserva como variable explicativa agregada o variable de control climático.

---

## 9. Fundamento metodológico de la desagregación temporal

La construcción de una serie semanal a partir de una serie mensual se apoya en la literatura de desagregación temporal y benchmarking, cuyo objetivo es obtener series de mayor frecuencia consistentes con agregados observados de menor frecuencia.

Denton propuso un enfoque clásico de ajuste de series subanuales a totales observados, ampliamente usado en estadística aplicada. Dagum y Cholette desarrollaron métodos de benchmarking, distribución temporal y reconciliación de series. Sax y Steiner sintetizan estos métodos y explican que la desagregación temporal puede realizarse con o sin indicadores de alta frecuencia, preservando sumas, promedios o valores de referencia de la serie original.

Una consideración importante es que los métodos clásicos funcionan de manera más natural cuando la frecuencia alta es múltiplo entero de la frecuencia baja. La transición mes a semana es irregular, porque los meses no tienen un número entero y constante de semanas. Por eso, en este proyecto se adopta una regla operativa, trazable y no climática basada en días calendario.

Esta decisión permite conservar coherencia temporal sin introducir señales espurias en la relación entre clima y producción.

---

## 10. Reglas de agregación semanal, mensual y anual

Para la fase de experimentación se generan bases mensual y anual a partir de la base semanal.

### 10.1 Target mensual

La producción mensual del panel se recupera como suma de semanas dentro del mismo departamento-año-mes:

$$
Y^{(m)}_{d,a,m} = \sum_{s \in (d,a,m)} Y^{(w)}_{d,a,m,s}
$$

### 10.2 Target anual

La producción anual se recupera como suma de meses dentro del mismo departamento-año:

$$
Y^{(a)}_{d,a} = \sum_{m=1}^{12} Y^{(m)}_{d,a,m}
$$

### 10.3 Variables estructurales repetidas

Las variables anuales o mensuales repetidas a nivel semanal no se suman múltiples veces. Se conservan usando el primer valor del grupo, luego de validar que sean constantes dentro del periodo.

Ejemplos:

- `produccion_mensual_proxy_t`
- `produccion_anual_departamental_t`
- `area_cosechada_departamental_ha`
- `rendimiento_departamental_t_ha`
- `valor_cosecha_anual_millones`

### 10.4 Variables climáticas

Las variables climáticas se agregan según su naturaleza:

| Tipo de variable | Regla sugerida | Ejemplos |
|------------------|----------------|----------|
| Flujo / acumulación | Suma | precipitación, lluvia acumulada |
| Estado / intensidad | Promedio | temperatura, humedad, radiación, viento |
| Eventos binarios | Máximo o promedio | dummies de exceso de lluvia, estrés hídrico, temperatura alta |

Para dummies, el máximo indica si el evento ocurrió al menos una vez en el periodo, mientras que el promedio indica proporción de semanas afectadas.

---

## 11. Uso de variables en modelamiento

### 11.1 Target principal semanal

```text
produccion_semanal_proxy_t
```

Interpretación:

> Producción semanal estimada como proxy operativa, no observada directamente.

### 11.2 Variables climáticas centrales

Estas variables pueden ser usadas como X principales para riesgo climático:

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

### 11.3 Variables climáticas derivadas

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
```

### 11.4 Variables económicas de contexto

```text
precio_interno_cop_carga
precio_externo_exdock_cent_usd_lb
exportaciones_mensual_miles_sacos
trm_viernes_cop_usd
trm_ultimo_dia_semana_cop_usd
```

Variables transformadas útiles:

```text
precio_interno_cop_carga_lag_1s
precio_interno_cop_carga_lag_4s
precio_interno_cop_carga_ma_4s
precio_interno_cop_carga_var_4s
precio_externo_exdock_cent_usd_lb_lag_4s
precio_externo_exdock_cent_usd_lb_ma_4s
exportaciones_mensual_miles_sacos_lag_4s
exportaciones_mensual_miles_sacos_ma_4s
trm_viernes_cop_usd_lag_1s
trm_viernes_cop_usd_lag_4s
trm_viernes_cop_usd_ma_4s
trm_viernes_cop_usd_var_4s
```

Estas variables no definen el índice climático, pero pueden aportar señales de mercado, costos, presión cambiaria, comercialización y exposición económica.

### 11.5 Variables que deben evitarse como X para predecir la Y semanal

Estas variables participan en la construcción, valorización o explicación directa del target y pueden inducir leakage si se usan como X en el modelo semanal:

```text
produccion_anual_proxy_5mun_t
produccion_anual_departamental_t
produccion_mensual_proxy_t
peso_mensual_prod_nacional
produccion_nacional_mensual_oficial_miles_sacos
valor_cosecha_semanal_proxy_millones
```

---

## 12. Estrategia de modelamiento y criterios técnicos

La fase de modelamiento del Módulo 2 se organizó en tres frecuencias complementarias: weekly, monthly y annual. La lógica no fue encontrar un único modelo dominante para todo el proyecto, sino identificar qué combinación de variables, frecuencia y técnica ofrecía mayor valor según el rol esperado dentro del artefacto.

- **Weekly:** capa operativa para monitoreo, sensibilidad y simulación.
- **Monthly:** capa intermedia para equilibrar utilidad operativa y consistencia productiva.
- **Annual:** capa de contraste metodológico y validación más conservadora.

La selección de familias de modelos respondió a cuatro criterios principales: (i) tamaño muestral disponible, (ii) interpretabilidad, (iii) capacidad para capturar relaciones no lineales y (iv) riesgo de sobreajuste.

### 12.1 Modelos candidatos por frecuencia

| Frecuencia | Modelos candidatos | Motivo técnico de inclusión |
|---|---|---|
| Weekly | Dummy, Ridge, Random Forest, XGBoost | Mayor número de observaciones; permite comparar modelos lineales y no lineales para capturar dinámica operativa. |
| Monthly | Dummy, Ridge, Random Forest, XGBoost | Frecuencia intermedia con tamaño muestral suficiente para comparar interpretabilidad vs. flexibilidad. |
| Annual | Dummy, Ridge | Muestra reducida (20 observaciones); se privilegió parsimonia y estabilidad sobre complejidad. |

### 12.2 Supuestos y criterios metodológicos

Los modelos lineales regularizados se usaron como baselines interpretables y parsimoniosos. En particular, RidgeCV fue útil cuando existía posible multicolinealidad entre covariables y se buscaba estabilidad fuera de muestra. De forma esquemática, Ridge minimiza:

$$
\min_{\beta} \sum_i (y_i - x_i'\beta)^2 + \lambda \sum_j \beta_j^2
$$

donde $\lambda$ controla el grado de regularización.

Los modelos basados en árboles se incluyeron para capturar relaciones no lineales, interacciones y posibles umbrales entre clima, economía y estructura productiva. Random Forest se usó como alternativa robusta de bagging, mientras XGBoost se probó como versión boosting en weekly y monthly, donde el número de observaciones justificaba esa comparación. En annual no se emplearon modelos más complejos debido al alto riesgo de sobreajuste con una muestra tan pequeña.

Además, la selección de variables se hizo bajo control explícito de leakage: no se incluyeron como covariables aquellas variables que participaban directamente en la construcción del target proxy o que incorporaban información futura incompatible con el esquema de validación temporal.

### 12.3 Esquema experimental y métricas

Todas las corridas siguieron un split temporal consistente:

- **Entrenamiento:** 2021–2022
- **Validación:** 2023
- **Prueba:** 2024

Esta decisión buscó emular un escenario real de generalización hacia adelante, evitando fuga de información futura y preservando coherencia cronológica.

Las métricas reportadas fueron:

- **RMSE**: penaliza con mayor fuerza errores grandes.
- **MAE**: resume el error absoluto promedio.
- **MAPE**: facilita interpretar el error relativo.
- **R²**: resume la capacidad explicativa del modelo.
- **Corr**: se utilizó como métrica complementaria para evaluar si el modelo preservaba la dirección general de la dinámica observada, especialmente en contextos con muestras pequeñas o compresión del rango.

Además del desempeño predictivo, se realizaron verificaciones de consistencia sobre semanas incompletas, agregación weekly → monthly → annual y control de leakage en la selección de covariables.

---

## 13. Resultados por frecuencia y criterios de selección

La estrategia multi-frecuencia permitió comparar alternativas de modelamiento y, más importante aún, reubicar cada resultado dentro de la arquitectura final del artefacto. La selección final no respondió a un único criterio de error predictivo, sino a la combinación entre desempeño, interpretabilidad, escala temporal y utilidad dentro del sistema.

### 13.1 Resultados weekly

En frecuencia weekly se compararon modelos Dummy, Ridge, Random Forest y XGBoost con diferentes subconjuntos de variables climáticas, derivadas y económicas. Los mejores resultados se concentraron en modelos no lineales, especialmente Random Forest y XGBoost. La comparación principal se resume así:

| Modelo weekly | val_RMSE | val_R2 | test_RMSE | test_R2 | test_Corr | Lectura |
|---|---:|---:|---:|---:|---:|---|
| `V7_clima_mas_economicas_rf` | 15.322 | 0.781 | 30.599 | 0.649 | 0.940 | Mejor balance global |
| `V5_clima_crudo_rf` | 15.397 | 0.779 | 36.011 | 0.511 | 0.877 | Buen benchmark no lineal |
| `V8_clima_derivado_xgb` | 15.953 | 0.762 | 36.555 | 0.499 | 0.888 | Alternativa boosting competitiva |
| `V1_baseline_ridge` | 17.537 | 0.713 | 44.226 | 0.266 | 0.910 | Baseline interpretable |
| `V0_dummy_mean` | 32.828 | -0.006 | 54.102 | -0.098 | 0.000 | Referencia mínima |

El mejor desempeño semanal correspondió a:

`V7_clima_mas_economicas_rf`

Se seleccionó porque presentó el mejor balance entre error de validación, error de prueba, capacidad explicativa y correlación fuera de muestra. En particular, superó con claridad al baseline lineal y al dummy, mostrando que la combinación de clima derivado y variables económicas aportaba valor operativo a escala semanal.

Sin embargo, el análisis posterior mostró una influencia importante del componente territorial, por lo que esta frecuencia debe interpretarse como:

- útil para monitoreo;
- útil para simulación y sensibilidad;
- menos fuerte como validación causal del índice climático.

En consecuencia, **weekly quedó como capa operativa del artefacto**, no como evidencia principal de causalidad climática.

### 13.2 Resultados monthly

En frecuencia monthly se compararon modelos con clima, clima + economía y clima + economía + estructura productiva. La competencia principal se dio entre `M5_clima_econ_rf`, `M6_clima_econ_struct_rf` y `M7_clima_econ_xgb`.

| Modelo monthly | val_RMSE | val_R2 | test_RMSE | test_R2 | test_Corr | Lectura |
|---|---:|---:|---:|---:|---:|---|
| `M6_clima_econ_struct_rf` | 62.917 | 0.804 | 144.718 | 0.593 | 0.883 | Mejor ajuste global |
| `M7_clima_econ_xgb` | 62.966 | 0.804 | 150.301 | 0.561 | 0.930 | Muy competitivo |
| `M5_clima_econ_rf` | 66.339 | 0.782 | 149.602 | 0.565 | 0.908 | Mejor lectura climática |
| `M4_clima_rf` | 72.813 | 0.737 | 161.853 | 0.491 | 0.840 | Clima sin economía |
| `M1_baseline_ridge` | 78.893 | 0.692 | 197.843 | 0.240 | 0.907 | Baseline mensual |

El mejor ajuste mensual se obtuvo con:

`M6_clima_econ_struct_rf`

Se seleccionó como mejor capa operativa mensual porque logró el menor error global y el mejor R² en validación y prueba. No obstante, la revisión de importancia por familias mostró dominancia de variables estructurales, especialmente `area_cosechada_departamental_ha`. La contribución agregada por familias fue:

- **estructural = 0.820590**
- **climática = 0.094971**
- **económica = 0.080937**
- **temporal = 0.002683**
- **territorial = 0.000819**

Por ello, además de `M6`, se conservó también:

`M5_clima_econ_rf`

como referencia más limpia para interpretar la lógica climática y económica del seguro indexado. Aunque M5 quedó ligeramente por debajo en desempeño, preservó una lectura más coherente con el objetivo de conectar señales climáticas y de mercado con la lógica del seguro.

En síntesis:

- **M6** = mejor capa operativa mensual.
- **M5** = mejor referencia mensual para la lógica climática del seguro.

### 13.3 Resultados annual

En annual se evaluaron dos targets:

- `rendimiento_departamental_t_ha`
- `produccion_anual_departamental_t`

Los modelos probados fueron Dummy y Ridge. La comparación mostró que el baseline territorial-temporal fue el más estable.

#### Target 1: rendimiento anual

| Modelo annual | val_RMSE | val_R2 | test_RMSE | test_R2 | test_Corr | Lectura |
|---|---:|---:|---:|---:|---:|---|
| `A1_baseline_ridge` | 0.120 | 0.626 | 0.427 | -6.343 | 0.788 | Mejor baseline |
| `A2_clima_ridge` | 0.153 | 0.394 | 0.269 | -1.914 | 0.671 | Clima anual no supera baseline |
| `A3_clima_econ_ridge` | 0.158 | 0.353 | 0.253 | -1.572 | 0.672 | Clima+economía no supera baseline |
| `A0_dummy` | 0.200 | -0.042 | 0.299 | -2.600 | 0.000 | Referencia mínima |

#### Target 2: producción anual

| Modelo annual | val_RMSE | val_R2 | test_RMSE | test_R2 | test_Corr | Lectura |
|---|---:|---:|---:|---:|---:|---|
| `A1_baseline_ridge` | 643.782 | 0.818 | 2030.095 | 0.252 | 0.999 | Mejor modelo annual |
| `A3_clima_econ_ridge` | 1388.694 | 0.152 | 2992.643 | -0.626 | 0.819 | Peor que baseline |
| `A0_dummy` | 1514.170 | -0.008 | 2502.155 | -0.136 | 0.000 | Referencia mínima |
| `A2_clima_ridge` | 1670.953 | -0.227 | 3495.363 | -1.217 | 0.824 | Clima anual agregado insuficiente |

El modelo retenido fue:

`A1_baseline_ridge`

No porque annual liderara el artefacto, sino porque funcionó como el mejor contraste metodológico disponible dada la escala y el tamaño muestral. A esta frecuencia:

- el baseline territorial-temporal fue superior o más estable;
- la señal climática anual agregada no superó claramente al baseline;
- el tamaño muestral fue demasiado pequeño para esperar una capa predictiva robusta.

Esto no invalida el proceso; más bien documenta una limitación importante:

> la agregación anual y la muestra reducida dificultan capturar relaciones climáticas complejas.

Por ello, **annual no quedó como capa principal del artefacto**, sino como nivel de contraste y defendibilidad.

### 13.4 Trazabilidad entre requerimiento, frecuencia y modelo

| Requerimiento / pregunta | Frecuencia más útil | Modelo o referencia | Razón técnica |
|---|---|---|---|
| Monitoreo operativo y sensibilidad del artefacto | Weekly | `V7_clima_mas_economicas_rf` | Mayor granularidad temporal y mejor ajuste semanal. |
| Comparación entre zonas y soporte analítico-operativo | Monthly | `M6_clima_econ_struct_rf` | Mejor desempeño mensual. |
| Lectura climática más alineada con seguro indexado | Monthly | `M5_clima_econ_rf` | Menor dependencia estructural que M6. |
| Contraste conservador de defendibilidad | Annual | `A1_baseline_ridge` | Parsimonia y mejor resultado annual frente a alternativas con clima. |

---

## 14. Síntesis metodológica y lectura final

Los resultados mostraron que no era metodológicamente correcto insistir en una narrativa de modelo único dominante. En cambio, la evidencia empírica apoyó una arquitectura por capas:

- **Weekly:** útil para operación, monitoreo y simulación, pero con alta influencia territorial.
- **Monthly:** mejor frecuencia intermedia para sostener el artefacto, con una lectura dual entre `M6` como mejor ajuste y `M5` como referencia más alineada con la lógica climática del seguro.
- **Annual:** útil como contraste metodológico, pero con muestra demasiado pequeña y señal climática anual insuficiente para desplazar al baseline.

Desde una perspectiva estadística, estas limitaciones no invalidan el proyecto; al contrario, ayudan a reubicar cada frecuencia en el rol metodológico que mejor puede cumplir. Weekly maximizó observaciones pero trabajó con una Y proxy; monthly ofreció el mejor compromiso entre estabilidad y operación; y annual, aunque conceptualmente más cercano a producción o rendimiento observados, operó con una muestra reducida para sostener relaciones más complejas.

En consecuencia, el artefacto se justifica mejor como una herramienta integrada de monitoreo, comparación territorial, simulación de escenarios y apoyo a la definición de primas y triggers, más que como un único modelo predictivo climático puro.

---

## 15. Limitaciones específicas del modelamiento

- La variable objetivo semanal no es producción observada, sino una proxy operativa.
- La mensualización y semanalización preservan coherencia temporal, pero no reemplazan observaciones reales de alta frecuencia.
- El modelamiento weekly mostró fuerte influencia territorial.
- El modelamiento monthly ofreció mayor utilidad operativa, aunque el mejor ajuste dependió en parte de variables estructurales.
- El modelamiento annual operó con una muestra muy reducida, lo que limita la estabilidad de las métricas y la capacidad de capturar relaciones climáticas complejas.
- Los promedios climáticos anuales pueden suavizar eventos extremos o ventanas críticas relevantes para el café.
- La base panel departamental resultó más valiosa que la proxy nacional agregada, porque preservó heterogeneidad territorial y permitió una comparación más útil entre zonas.

---

## 16. Matriz funcional del artefacto

La construcción del artefacto se definió a partir de tres páginas principales, alineadas con las preguntas analíticas, los modelos seleccionados y la utilidad esperada para el usuario final. Esta matriz busca hacer explícita la trazabilidad **requerimiento → frecuencia → modelo/capa → métrica → salida esperada**, respondiendo a una de las observaciones metodológicas más importantes del proceso de evaluación.

### 16.1 Página 1. Diagnóstico descriptivo y contexto territorial

**Objetivo.** Dar contexto al usuario sobre el comportamiento climático, productivo y económico por departamento, y permitir una lectura inicial del riesgo antes de entrar a modelos o decisiones del seguro.

**Preguntas analíticas.**
- ¿Cómo se comportan el clima, la producción proxy y el contexto económico por departamento y período?
- ¿Qué departamentos muestran mayor exposición o mayor variabilidad?

**Base principal.**
- `monthly.csv`

**Base complementaria.**
- `weekly.csv` para detalle reciente o alertas de corto plazo.

**Capa que la soporta.**
- Componente descriptivo del artefacto; no depende de un modelo predictivo único.

**Indicadores visibles.**
- Producción mensual proxy
- Rendimiento departamental
- Área cosechada
- Precipitación
- Temperatura media / máxima
- Humedad del suelo
- Precio interno
- Precio externo
- Exportaciones
- TRM

**Lectura esperada.**
Esta página no “predice”; organiza el contexto territorial y permite detectar diferencias relevantes para el monitoreo del riesgo.

**Supuestos / limitaciones.**
- La producción mensual es una proxy construida a partir de la lógica semanal y mensual del proyecto.
- La lectura es comparativa y descriptiva, no causal.
- La proxy nacional, si se muestra, se calcula agregando departamentos.

**Visuales sugeridos.**
- KPI cards
- Mapa por departamento
- Series mensuales
- Comparativos territoriales
- Tarjetas de alertas climáticas

**Decisión que apoya.**
Identificar departamentos con mayor exposición, contrastar contexto productivo y climático y orientar dónde profundizar el análisis.

---

### 16.2 Página 2. Modelos, métricas, supuestos y selección metodológica

**Objetivo.** Mostrar qué modelos se probaron, cuál se seleccionó en cada frecuencia, por qué se eligió, qué métrica lo respalda y cuáles son sus limitaciones.

**Preguntas analíticas.**
- ¿Qué modelo funciona mejor para cada propósito del artefacto?
- ¿Qué tan confiables son los resultados?
- ¿Qué capa sirve para monitoreo, cuál para operación y cuál para contraste metodológico?

**Bases principales.**
- Tablas resumen de resultados weekly, monthly y annual.

**Modelos / capas seleccionadas.**
- Weekly: `V7_clima_mas_economicas_rf`
- Monthly operativo: `M6_clima_econ_struct_rf`
- Monthly referencia climática: `M5_clima_econ_rf`
- Annual contraste: `A1_baseline_ridge`

**Métricas visibles.**
- RMSE
- MAE
- MAPE
- R²
- Corr

**Interpretación esperada.**
- `V7`: útil para monitoreo operativo, pero no como validación causal fuerte por su influencia territorial.
- `M6`: mejor ajuste mensual para operación.
- `M5`: modelo más alineado con la lógica climática del seguro indexado.
- `A1`: contraste metodológico parsimonioso; no capa principal del artefacto.

**Supuestos / limitaciones.**
- Weekly usa una Y proxy, no observada.
- Monthly presenta diferencia controlada entre target agregado desde semana y target mensual de referencia.
- Annual tiene muestra pequeña (`n = 20`), por lo que se privilegió parsimonia.
- Random Forest y XGBoost capturan no linealidades, pero son menos interpretables.
- Ridge es más interpretable, pero menos flexible.

**Ventajas y desventajas por familia de modelos.**

| Familia | Ventaja principal | Riesgo / limitación |
|---|---|---|
| Ridge | Interpretabilidad, estabilidad y utilidad con multicolinealidad | No capta toda la no linealidad |
| Random Forest | Captura interacciones y relaciones no lineales | Menor interpretabilidad; puede reflejar dominancia territorial o estructural |
| XGBoost | Alta flexibilidad y buen ajuste comparativo | Mayor complejidad y menor trazabilidad |
| Dummy | Benchmark mínimo | No sirve como capa operativa real |

**Visuales sugeridos.**
- Tabla comparativa de modelos
- Cards de modelo seleccionado por frecuencia
- Barras de importancia por familias
- Recuadro de supuestos y limitaciones
- Diagrama de trazabilidad: pregunta → modelo → métrica → uso

**Decisión que apoya.**
Justificar técnicamente por qué el artefacto usa unas capas y no otras, y dar confianza metodológica al usuario y evaluador.

---

### 16.3 Página 3. Herramienta analítica del seguro indexado

**Objetivo.** Traducir la información descriptiva y los hallazgos del modelamiento en una herramienta útil para monitorear riesgo, comparar zonas y apoyar decisiones técnicas del seguro.

**Preguntas analíticas.**
- ¿Qué zonas presentan mayor riesgo?
- ¿Qué señales justifican monitoreo o revisión técnica?
- ¿Cómo se traduce esto en una lectura útil para el seguro indexado?

**Base principal.**
- `monthly.csv`

**Bases complementarias.**
- `weekly.csv` para alertas y monitoreo fino
- `annual.csv` como soporte metodológico si se requiere una nota técnica

**Capas que la soportan.**
- Weekly: `V7` para señal operativa
- Monthly: `M6` como capa principal
- Monthly: `M5` como contraste más alineado con lógica climática
- Annual: `A1` solo como respaldo metodológico

**Indicadores visibles.**
- Señal de riesgo por departamento
- Estado de alerta climática
- Comparación mensual entre zonas
- Resumen técnico de desempeño
- Variables clave asociadas al riesgo
- Indicadores de apoyo a trigger / monitoreo / prima técnica

**Lectura esperada.**
La app no reemplaza una póliza ni calcula actuarialmente el producto final; actúa como artefacto de monitoreo, comparación territorial y apoyo técnico para el diseño del seguro indexado.

**Supuestos / limitaciones.**
- La capa principal es monthly, no annual.
- Weekly es útil para seguimiento, pero no para inferencia causal fuerte.
- La herramienta apoya decisiones técnicas; no automatiza decisiones regulatorias o actuariales completas.
- La señal de riesgo depende de proxies productivas y de variables agregadas disponibles.

**Visuales sugeridos.**
- Mapa de riesgo por departamento
- Ranking de departamentos por señal de riesgo
- Tarjetas de alerta climática
- Serie mensual de riesgo / producción / clima
- Bloque de lectura técnica
- Recuadro de decisión sugerida: monitoreo, revisión técnica, comparación entre zonas

**Decisión que apoya.**
Monitoreo técnico del riesgo, comparación entre zonas cafeteras y soporte a revisión de criterios del seguro indexado.

---

### 16.4 Trazabilidad entre requerimiento, frecuencia y modelo

| Requerimiento / pregunta | Página | Frecuencia | Modelo / capa | Métrica clave | Resultado esperado |
|---|---|---|---|---|---|
| Entender contexto climático-productivo por zona | 1 | Monthly | Descriptiva | No aplica | Diagnóstico territorial claro |
| Monitorear dinámica reciente | 1 / 3 | Weekly | `V7` | test_RMSE, test_R2, test_Corr | Señal operativa útil |
| Seleccionar modelos defendibles | 2 | Weekly / Monthly / Annual | `V7`, `M6`, `M5`, `A1` | RMSE, MAPE, R², Corr | Trazabilidad metodológica |
| Sostener análisis principal del artefacto | 3 | Monthly | `M6` y `M5` | val/test métricas monthly | Soporte técnico al seguro |
| Mostrar contraste conservador | 2 | Annual | `A1` | métricas annual | Transparencia metodológica |

---

## 17. Cronograma, métricas de éxito, riesgos y alistamiento del prototipo

La implementación del artefacto se desarrollará como un MVP web basado en **Dash + CSS + Docker + Render**, priorizando trazabilidad, claridad metodológica y utilidad técnica del dashboard antes que complejidad innecesaria de infraestructura.

### 17.1 Cronograma de implementación

| Fase | Actividad principal | Entregable | Responsable | Criterio de cierre |
|---|---|---|---|---|
| F1 | Consolidación de datos y repositorio | Cubos `weekly`, `monthly`, `annual` exportados y documentados | Desarrollo del prototipo | CSV exportados, sin duplicados en llaves y con validación básica completada |
| F2 | Definición funcional del artefacto | Matriz funcional del dashboard | Desarrollo del prototipo | Páginas, preguntas, bases y visuales definidos |
| F3 | Preparación de datasets app-ready | `weekly_app`, `monthly_app`, `annual_app` | Desarrollo del prototipo | Variables seleccionadas y listas para consumo en Dash |
| F4 | Construcción de la app en Dash | Estructura de tres páginas y navegación | Desarrollo del prototipo | App corre localmente y carga datos sin error |
| F5 | Integración visual y contenido analítico | Visuales, KPIs, tablas y módulos metodológicos | Desarrollo del prototipo | Las tres páginas responden a las preguntas analíticas definidas |
| F6 | Empaquetado y despliegue | Dockerfile + despliegue en Render | Desarrollo del prototipo | App desplegada y accesible |
| F7 | Validación final y ajustes | Prototipo final + revisión ejecutiva | Desarrollo del prototipo | MVP completo, documentado y listo para presentación |

### 17.2 Métricas de éxito del prototipo

| Dimensión | Métrica de éxito | Umbral deseado |
|---|---|---|
| Datos | Exportación correcta de cubos base | 100% de los cubos generados sin error |
| Datos | Duplicados por llave esperada | 0 duplicados |
| Datos | Diferencia annual entre target agregado y referencia | 0 |
| Dashboard | Navegación entre páginas | 100% funcional |
| Dashboard | Filtros principales (departamento, año, mes) | 100% funcionales |
| Dashboard | Tiempo de carga local por página | ≤ 5 segundos |
| Modelamiento | Trazabilidad visible requerimiento → modelo → métrica | Presente en la página 2 |
| Interpretación | Supuestos y limitaciones visibles | Presente en página 2 y documentado |
| Artefacto | Señal de riesgo y lectura técnica disponibles | Presente en página 3 |
| Despliegue | App publicada | URL funcional en Render |

### 17.3 Riesgos y bloqueantes principales

| Riesgo / bloqueante | Efecto posible | Mitigación prevista |
|---|---|---|
| Diferencias entre target mensual agregado y target mensual de referencia | Confusión metodológica en la lectura de resultados | Documentar `diff_target_mensual` y explicarlo como limitación controlada |
| Sobrecarga visual del dashboard | Pérdida de claridad para el usuario | Limitar el artefacto a tres páginas con propósito definido |
| Exceso de variables en la app | Lentitud y complejidad innecesaria | Crear datasets `*_app.csv` curados |
| Interpretación errónea de modelos weekly | Sobreventa del componente predictivo | Aclarar que weekly es capa operativa, no validación causal fuerte |
| Muestra pequeña en annual | Sobreinterpretación de métricas | Usar annual como contraste metodológico |
| Problemas de despliegue | Retraso en entrega funcional | Probar localmente primero, luego Docker y finalmente Render |

### 17.4 Componentes pendientes por implementar

- [x] Cubos base exportados (`weekly`, `monthly`, `annual`)
- [x] Validación básica de llaves, nulos y consistencia annual
- [ ] Datasets app-ready
- [ ] Estructura Dash de tres páginas
- [ ] CSS del artefacto
- [ ] Visuales descriptivos
- [ ] Módulo de modelos y métricas
- [ ] Módulo del artefacto del seguro
- [ ] Dockerfile
- [ ] Despliegue en Render
- [ ] Validación final de funcionamiento

### 17.5 Criterio de alistamiento del MVP

El prototipo se considerará listo para evaluación cuando cumpla simultáneamente con las siguientes condiciones:

1. carga correctamente los datos curados del proyecto;
2. presenta tres páginas funcionales y navegables;
3. hace explícita la relación entre preguntas analíticas, capas de modelamiento y uso dentro del artefacto;
4. muestra métricas, supuestos y limitaciones de forma interpretable;
5. traduce los resultados del modelamiento en una lectura útil para monitoreo y soporte técnico del seguro;
6. puede ejecutarse localmente y desplegarse mediante contenedor.

---

## 18. Diccionario resumido de variables clave

| Variable | Tipo | Uso recomendado |
|----------|------|-----------------|
| `produccion_semanal_proxy_t` | Target semanal | Y principal operativa |
| `produccion_mensual_proxy_t` | Productiva construida | Validación/agregación; evitar como X semanal |
| `produccion_anual_departamental_t` | Productiva observada/anual | Target anual o control estructural; evitar como X semanal si predice Y semanal |
| `area_cosechada_departamental_ha` | Estructural | Útil en modelos operativos mensuales/anuales |
| `rendimiento_departamental_t_ha` | Productiva/eficiencia | Target anual alternativo |
| `PRECTOTCORR` | Climática | X central de precipitación |
| `IMERG_PRECTOT` | Climática | X central de precipitación alternativa |
| `T2M` | Climática | X central de temperatura media |
| `T2M_MAX` | Climática | X de estrés térmico |
| `T2M_MIN` | Climática | X de temperatura mínima |
| `RH2M` | Climática | X de humedad relativa |
| `QV2M` | Climática | X de humedad específica |
| `GWETTOP` | Climática | X de humedad superficial |
| `GWETROOT` | Climática | X de humedad radicular |
| `ALLSKY_SFC_SW_DWN` | Climática | X de radiación |
| `WS2M` | Climática | X de viento |
| `indice_climatico_base_x` | Climática derivada | X agregada de clima |
| `indice_climatico_ajustado_x` | Climática derivada | X agregada suavizada |
| `lluvia_acum_4s` | Climática derivada | X de acumulado corto |
| `lluvia_acum_8s` | Climática derivada | X de acumulado medio |
| `anomalia_lluvia_semana_iso` | Climática derivada | X de desviación frente a patrón semanal |
| `precio_interno_cop_carga` | Económica | Contexto de mercado interno |
| `precio_externo_exdock_cent_usd_lb` | Económica | Contexto de mercado externo |
| `exportaciones_mensual_miles_sacos` | Económica | Contexto comercial |
| `trm_viernes_cop_usd` | Económica | Presión cambiaria / costo de insumos importados |
| `valor_cosecha_anual_millones` | Financiera | Exposición económica; no usar como X para Y semanal |


---

## 19. Uso esperado del artefacto

El artefacto analítico no se limita a predecir producción. Su valor está en integrar capas de información para apoyar decisiones de aseguramiento:

- monitoreo semanal del riesgo climático;
- comparación territorial entre departamentos cafeteros;
- simulación de escenarios de estrés climático;
- análisis de sensibilidad frente a variables económicas;
- estimación de exposición económica;
- soporte para calibración de primas;
- exploración de triggers climáticos para seguros indexados.

---

## 20. Referencias metodológicas

- Denton, F. T. (1971). *Adjustment of Monthly or Quarterly Series to Annual Totals: An Approach Based on Quadratic Minimization*. Journal of the American Statistical Association.
- Dagum, E. B., & Cholette, P. (2006). *Benchmarking, Temporal Distribution, and Reconciliation Methods for Time Series*.
- Sax, C., & Steiner, P. (2013). *Temporal Disaggregation of Time Series*. The R Journal.
- Eurostat / ESS Guidelines (2018). *ESS Guidelines on Temporal Disaggregation, Benchmarking and Reconciliation*.

---

## 21. Nota final

Este proyecto debe interpretarse como una aproximación analítica progresiva para un seguro agrícola indexado. La base semanal permite operación y simulación, la base mensual mejora la estabilidad del análisis y la base anual sirve como contraste metodológico frente a la frecuencia original de la producción observada.

La principal decisión metodológica fue separar la construcción del target semanal de las variables climáticas, para conservar el clima como señal explicativa limpia dentro del modelamiento. Esto permite que los modelos exploren relaciones entre clima, economía y producción proxy sin inducir correlaciones artificiales por construcción de la Y.

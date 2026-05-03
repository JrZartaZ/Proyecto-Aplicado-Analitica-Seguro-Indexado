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

## 12. Estrategia de modelamiento multi-frecuencia

La implementación se estructura en tres niveles: semanal, mensual y anual.

### 12.1 Modelamiento semanal

El modelamiento semanal se interpreta como una capa operativa. Permite monitoreo, sensibilidad y simulación del artefacto. En esta frecuencia se comparan modelos lineales regularizados, árboles y boosting con distintos subconjuntos de variables climáticas, derivadas y económicas.

Modelos probados:

- Dummy mean
- Ridge baseline
- Ridge con clima crudo
- Ridge con clima derivado
- Ridge con índice agregado
- Random Forest con clima crudo
- Random Forest con clima derivado
- Random Forest con clima derivado + económicas
- XGBoost con clima derivado

Modelo seleccionado:

```text
V7_clima_mas_economicas_rf
```

Lectura metodológica:

El mejor resultado semanal correspondió a un Random Forest con clima derivado y variables económicas. Sin embargo, el resultado debe interpretarse como capa de monitoreo y simulación, no como validación climática pura, debido a que la Y semanal es una proxy operativa y el componente territorial puede dominar parte del ajuste.

---

### 12.2 Modelamiento mensual

El modelamiento mensual funciona como puente entre consistencia productiva y utilidad operativa. En esta frecuencia se comparan modelos con clima, clima + economía y clima + economía + estructura productiva.

Modelos probados:

- Dummy mean
- Ridge baseline
- Ridge con clima
- Ridge con clima + economía
- Random Forest con clima
- Random Forest con clima + economía
- Random Forest con clima + economía + estructurales
- XGBoost con clima + economía

Modelos seleccionados:

```text
M6_clima_econ_struct_rf
M5_clima_econ_rf
```

Lectura metodológica:

`M6_clima_econ_struct_rf` se conserva como mejor ajuste operativo mensual. Sin embargo, debido a que incorpora variables estructurales como área cosechada, también se conserva `M5_clima_econ_rf` como referencia más limpia para interpretar el componente climático y económico del seguro indexado.

---

### 12.3 Modelamiento anual

El modelamiento anual permite contrastar si las variables climáticas agregadas anualmente logran explicar producción o rendimiento frente a un baseline territorial-temporal.

Targets considerados:

```text
rendimiento_departamental_t_ha
produccion_anual_departamental_t
```

Modelos probados:

- Dummy mean
- Ridge baseline
- Ridge con clima
- Ridge con clima + economía

Modelo seleccionado:

```text
A1_baseline_ridge
```

Lectura metodológica:

Los resultados mostraron que el mejor desempeño anual correspondió al baseline Ridge. Esto sugiere que, con solo 20 observaciones y clima agregado a escala anual, la señal climática no fue suficiente para superar el componente estructural-territorial. Esta capa anual se interpreta como contraste metodológico y documentación de limitaciones.

---

## 13. Modelos seleccionados para la herramienta analítica

| Frecuencia | Modelo seleccionado | Rol en el artefacto |
|-----------|---------------------|---------------------|
| Semanal | `V7_clima_mas_economicas_rf` | Monitoreo, sensibilidad y simulación operativa |
| Mensual | `M6_clima_econ_struct_rf` | Mejor ajuste operativo mensual |
| Mensual alternativo | `M5_clima_econ_rf` | Lectura más limpia del componente climático-económico |
| Anual | `A1_baseline_ridge` | Contraste metodológico anual |

---

## 14. Conclusiones del modelamiento

1. No existe un único modelo dominante para todos los propósitos del proyecto.
2. La capa semanal es útil para monitoreo operativo, sensibilidad y simulación del artefacto.
3. La capa mensual es la frecuencia intermedia más útil para conectar señales climáticas, económicas y productivas.
4. La capa anual sirve como contraste metodológico, pero no como núcleo final del artefacto por el tamaño reducido de la muestra.
5. Las variables climáticas deben interpretarse como señales explicativas del riesgo, no como garantía causal automática de pérdida productiva.
6. La heterogeneidad territorial y la estructura productiva siguen siendo determinantes importantes.
7. El artefacto se justifica mejor como herramienta integrada de monitoreo, comparación territorial, simulación de escenarios y apoyo a primas/triggers, más que como un único modelo predictivo climático puro.

---

## 15. Limitaciones documentadas

- La variable objetivo semanal no es producción observada, sino una proxy operativa.
- La mensualización y semanalización preservan coherencia temporal, pero no reemplazan observaciones reales de alta frecuencia.
- El modelamiento semanal puede estar influenciado por heterogeneidad territorial.
- El modelamiento mensual mejora utilidad operativa, pero el mejor ajuste puede incorporar variables estructurales que dominan parte de la señal climática.
- El modelamiento anual tiene una muestra reducida, lo que limita la estabilidad de métricas y la capacidad de capturar relaciones climáticas complejas.
- Los promedios climáticos anuales pueden suavizar eventos extremos o ventanas críticas relevantes para café.
- Las variables económicas deben interpretarse como contexto de mercado y exposición financiera, no como drivers climáticos directos.

---

## 16. Diccionario resumido de variables clave

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

## 17. Uso esperado del artefacto

El artefacto analítico no se limita a predecir producción. Su valor está en integrar capas de información para apoyar decisiones de aseguramiento:

- monitoreo semanal del riesgo climático;
- comparación territorial entre departamentos cafeteros;
- simulación de escenarios de estrés climático;
- análisis de sensibilidad frente a variables económicas;
- estimación de exposición económica;
- soporte para calibración de primas;
- exploración de triggers climáticos para seguros indexados.

---

## 19. Referencias metodológicas

- Denton, F. T. (1971). *Adjustment of Monthly or Quarterly Series to Annual Totals: An Approach Based on Quadratic Minimization*. Journal of the American Statistical Association.
- Dagum, E. B., & Cholette, P. (2006). *Benchmarking, Temporal Distribution, and Reconciliation Methods for Time Series*.
- Sax, C., & Steiner, P. (2013). *Temporal Disaggregation of Time Series*. The R Journal.
- Eurostat / ESS Guidelines (2018). *ESS Guidelines on Temporal Disaggregation, Benchmarking and Reconciliation*.

---

## 20. Nota final

Este proyecto debe interpretarse como una aproximación analítica progresiva para un seguro agrícola indexado. La base semanal permite operación y simulación, la base mensual mejora la estabilidad del análisis y la base anual sirve como contraste metodológico frente a la frecuencia original de la producción observada.

La principal decisión metodológica fue separar la construcción del target semanal de las variables climáticas, para conservar el clima como señal explicativa limpia dentro del modelamiento. Esto permite que los modelos exploren relaciones entre clima, economía y producción proxy sin inducir correlaciones artificiales por construcción de la Y.

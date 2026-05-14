# Guía de usuario — Faro Cafetero ☕

## 1. ¿Qué es esta herramienta?
Faro Cafetero es una herramienta web para apoyar el monitoreo de riesgo climático y la simulación técnica de escenarios relacionados con un seguro indexado para café en Colombia.

La herramienta no calcula una prima actuarial definitiva. Su objetivo es ayudar a explorar el comportamiento del sistema cafetero, entender la lógica metodológica del proyecto y simular impactos proxy sobre la producción y sobre una cobertura indicativa.

---

## 2. ¿Qué puede hacer la herramienta?
La herramienta tiene tres capítulos principales:

### Diagnóstico
Permite observar el contexto territorial del sistema cafetero:
- producción mensual proxy,
- rendimiento,
- índice climático ajustado,
- alertas climáticas,
- contexto económico.

Sirve para responder: ¿qué está pasando en cada departamento y cómo se está comportando el sistema?

### Modelos
Presenta la trazabilidad metodológica del proyecto:
- qué modelos se probaron,
- qué métricas se usaron,
- cuáles modelos fueron seleccionados,
- qué ventajas y limitaciones tiene cada uno.

Sirve para responder: ¿por qué se eligieron estos modelos y no otros?

### Artefacto
Integra monitoreo y simulación técnica:
- muestra señal de riesgo,
- permite comparar departamentos,
- y habilita una simulación de escenario con impacto proxy sobre producción, cobertura indicativa y prima de referencia.

Sirve para responder: ¿cómo cambiaría el resultado bajo un escenario climático y económico diferente?

---

## 3. ¿Cómo usar la herramienta?

## Paso 1. Entrar a la plataforma
Abra la URL del artefacto en su navegador.

## Paso 2. Revisar el capítulo Diagnóstico
En esta página:
1. seleccione un departamento,
2. seleccione un año,
3. revise los indicadores principales,
4. observe las gráficas de producción, clima y contexto económico.

Recomendación: use esta página primero para entender el comportamiento general antes de interpretar modelos o simular escenarios.

## Paso 3. Revisar el capítulo Modelos
En esta página:
1. filtre por frecuencia, familia de modelo o target,
2. compare métricas,
3. consulte la tabla resumen,
4. revise la trazabilidad metodológica.

Recomendación: use esta página para entender qué modelo sostiene cada parte del artefacto.

## Paso 4. Revisar el capítulo Artefacto
En esta página:
1. seleccione departamento y año,
2. revise la señal de riesgo y la lectura técnica,
3. observe gráficos de alertas, producción y riesgo,
4. al final use el simulador técnico de escenario.

---

## 4. ¿Cómo usar el simulador técnico de escenario?
El simulador parte de una fila base mensual real del dataset y permite modificar algunas variables dentro de rangos controlados.

### Entradas principales
- mes base,
- hectáreas aseguradas,
- porcentaje de cobertura,
- tasa prima de referencia,
- índice climático ajustado,
- precipitación,
- temperatura media,
- humedad del suelo,
- precio interno,
- TRM.

### Salidas principales
- producción base operativa,
- producción simulada,
- pérdida proxy,
- valor expuesto proxy,
- cobertura indicativa,
- prima indicativa.

### Importante
La simulación combina dos capas:
- M6 como base operativa mensual,
- M5 como sensibilidad climática.

Esto permite una lectura más útil para fines de monitoreo y soporte técnico.

---

## 5. ¿Qué significan los resultados?
### Producción base operativa
Es la producción mensual proxy de referencia para el escenario base.

### Producción simulada
Es la producción ajustada bajo el escenario definido por el usuario.

### Pérdida proxy
Es la diferencia estimada entre la producción base y la producción simulada cuando el escenario es adverso.

### Valor expuesto proxy
Es una aproximación económica del impacto productivo, expresada en dinero.

### Cobertura indicativa
Es una aproximación del valor que podría ser cubierto según el porcentaje de cobertura seleccionado.

### Prima indicativa
Es una referencia técnica de simulación, no una prima actuarial real.

---

## 6. Recomendaciones de uso
- Empiece siempre por Diagnóstico.
- Luego revise Modelos para entender la lógica metodológica.
- Use el simulador solo después de comprender el contexto territorial.
- Interprete los resultados como apoyo técnico, no como reemplazo de una evaluación actuarial formal.
- Compare escenarios, no solo valores aislados.

---

## 7. Limitaciones importantes
- La producción usada en el proyecto es una proxy operacional.
- La herramienta no reemplaza una póliza ni una cotización actuarial.
- El simulador no debe interpretarse como predicción causal definitiva.
- Las salidas son útiles para monitoreo, sensibilidad y soporte a decisiones técnicas.

---

## 8. ¿Para quién sirve?
La herramienta puede ser útil para:
- equipos académicos,
- analistas de riesgo,
- equipos técnicos del sector agro,
- tomadores de decisión que necesiten una lectura simple del riesgo climático y productivo.

---

## 9. Mensaje final
La mejor forma de usar Faro Cafetero es seguir la lógica completa del artefacto:
1. entender el contexto,
2. entender la metodología,
3. usar la simulación como apoyo a decisiones.
"""

---
title: "Afinación del control de oxígeno disuelto en un biorreactor"
autor: "Emiliano Balderas · Instituto de Biotecnología, UNAM"
---

**Taller:** Afinación del control de oxígeno disuelto en un biorreactor

**Duración:** máximo 45 min por equipo (3 equipos de 6 personas, uno tras otro en el mismo biorreactor)

**Equipo:** Sartorius Biostat B, vasija de 8 L


# 1. ¿Qué es el control y por qué importa en bioprocesos?

Las células necesitan condiciones adecuadas para crecer y producir: temperatura, pH y oxígeno disuelto, entre otras. Esas condiciones cambian durante el cultivo; por ejemplo, al aumentar la cantidad de células puede aumentar el consumo de oxígeno.

**Controlar un bioproceso significa** medir una variable, compararla con el valor deseado y hacer ajustes para mantenerla cerca de ese valor. Esto ayuda a cuidar el cultivo, obtener resultados reproducibles y reducir la variación entre lotes.

Pensemos en el oxígeno disuelto: una sonda lo mide y el controlador decide si debe aumentar o disminuir la agitación. Así ajusta la entrada de oxígeno al líquido según lo que necesita el proceso. No controla directamente a las células, sino las condiciones de su entorno.

| Elemento | Qué significa | En esta práctica |
|---|---|---|
| Variable controlada ($y$) | Lo que queremos mantener | Oxígeno disuelto, indicado como $pO_2$ (% de saturación) |
| Setpoint ($SP$) | El valor que queremos alcanzar | 80 % de saturación, si es alcanzable en la prueba |
| Error ($e$) | Cuánto falta para llegar: $e = SP - y$ | Si queremos 80 % y medimos 75 %, el error es +5 puntos porcentuales |
| Variable manipulada ($u$) | Lo que podemos ajustar | Agitación (rpm: revoluciones por minuto) |
| Perturbación | Un cambio que afecta la variable controlada | Mayor consumo de oxígeno por las células |
| Controlador | El que calcula el ajuste a partir de la medición | El controlador de la torre Biostat B |

En **modo manual (`MAN`, lazo abierto)**, una persona fija la agitación.

En **modo automático (`AUTO`, lazo cerrado)**, el controlador compara continuamente la medición con el setpoint y ajusta la agitación. El aire permanecerá fijo durante toda la práctica.

# 2. Un tipo de controlador: el PID

Un controlador muy utilizado es el **PID**, llamado así por sus acciones proporcional, integral y derivativa. Podemos entenderlas como tres preguntas:

| Acción | Pregunta que responde | Qué aporta |
|---|---|---|
| **P: proporcional** | ¿Qué tan lejos estoy del valor deseado ahora? | Corrige más cuando el error es mayor. Por sí sola puede dejar una diferencia persistente con el SP. |
| **I: integral** | ¿Cuánto error se ha acumulado? | Sigue ajustando cuando la diferencia persiste y ayuda a eliminarla. Una acción demasiado fuerte puede causar oscilaciones. |
| **D: derivativa** | ¿Qué tan rápido está cambiando el error? | Puede ayudar a frenar una respuesta excesiva, pero también amplifica el ruido de la medición. |

**Se pueden usar las combinaciones que el proceso requiera:** P, PI, PD o PID. Aquí usaremos **PI**: la acción integral ayuda a corregir diferencias persistentes y omitimos la derivativa porque las burbujas pueden producir ruido en la señal de oxígeno.

## La fórmula, paso a paso

La idea es una suma: **salida = valor base + corrección P + corrección I + corrección D**. Una forma habitual de escribirla es:

$$u(t) = u_0 + K_c\,e(t) + \frac{K_c}{T_I}\int_0^t e(t)\,dt + K_c\,T_D\,\frac{de(t)}{dt}$$

No hace falta resolver integrales ni derivadas para realizar la práctica. Basta con leer cada parte:

- $u(t)$ es la salida que calcula el controlador en ese momento.
- $e(t)$ es el error actual. El término $K_c\,e(t)$ es la corrección **P**: multiplicar el error por una ganancia.
- El símbolo $\int$ significa **acumular el error con el tiempo**. El término que lo contiene es la corrección **I**.
- $de/dt$ significa **qué tan rápido cambia el error**. El último término es la corrección **D**; al usar PI lo omitimos ($T_D = 0$).

Las constantes son $K_c$ (ganancia), $T_I$ (tiempo integral) y $T_D$ (tiempo derivativo). Con el mismo error, un $K_c$ mayor produce una corrección mayor. Con el mismo $K_c$, un $T_I$ menor hace que la acción integral corrija más rápido. En algunos textos los tiempos aparecen como $\tau_I$ y $\tau_D$: significan lo mismo.

## Afinar el controlador: el propósito de esta práctica

**Afinar** significa encontrar valores adecuados para esas constantes. Un ajuste demasiado intenso puede hacer que la agitación y el oxígeno oscilen; uno demasiado suave puede tardar demasiado en corregir. Buscamos una respuesta útil para el cultivo y el equipo.

Una forma de empezar es usar **métodos semiempíricos**: reglas que otros ingenieros han desarrollado a lo largo de los años combinando modelos sencillos con observaciones de procesos reales. Medimos cómo responde nuestro reactor a un cambio conocido y usamos esa información en las reglas. El resultado es un ajuste inicial que después debemos comprobar en automático, no una garantía de comportamiento perfecto.

**Eso haremos aquí:** cambiar la agitación, observar el oxígeno, calcular un ajuste PI y comprobar cómo responde. Cada equipo usará una regla distinta para comparar los resultados.

# 3. Objetivo de la práctica

Obtener la curva de reacción del oxígeno disuelto ($pO_2$) ante un escalón en la agitación, sacar de ella un modelo sencillo y usarlo para calcular los parámetros de un controlador PI con un método semiempírico. Después se comprueba en el equipo cómo responde el lazo cerrado. Participan 3 equipos de 6 personas, con 45 minutos como máximo por equipo. El aire se mantiene en 0.5 vvm (2.5 L/min para 5 L de líquido) en todas las etapas; vvm significa litros de gas por litro de líquido por minuto.

Cada equipo usa un método distinto y al final se comparan los tres:

| Equipo | Método | Idea |
|---|---|---|
| 1 | Ziegler-Nichols (curva de reacción) | Respuesta rápida; acepta oscilación |
| 2 | SIMC (Skogestad) | Busca un compromiso entre rapidez y suavidad |
| 3 | ITAE para perturbaciones | Busca reducir el error persistente ante perturbaciones |


# 4. El sistema

| Parámetro | Valor |
|---|---|
| Volumen de trabajo | 5 L de agua con 10 g/L de azúcar (50 g) |
| Biomasa | Levadura seca (*S. cerevisiae*), 3 g/L (15 g), inoculada ~20 min antes del primer equipo |
| Temperatura | 30 °C (lazo de temperatura activo) |
| Aireación | 0.5 vvm fijos (2.5 L/min; es el mínimo del equipo) |
| Agitación de reposo | 200 rpm en modo manual |
| Escalón | 200 → 500 rpm ($\Delta u = 300$ rpm) |
| Cascada de $pO_2$ (solo agitador) | $N_{\min} = 200$ rpm, $N_{\max} = 1200$ rpm → **Span = 1000 rpm** |

**¿Por qué cambia el $pO_2$?** El oxígeno que pasa del aire al líquido compite con el que consumen las levaduras. Al aumentar la agitación se favorece esa transferencia y el oxígeno disuelto puede subir hasta un nuevo equilibrio. Durante los pocos minutos de la medición suponemos que el consumo cambia poco. No necesitamos calcular ese consumo para realizar la práctica.

# 5. La curva de reacción del proceso

La curva de reacción es la respuesta de la variable controlada a un escalón en la variable manipulada con el controlador desconectado (lazo abierto, modo `MAN`). Es la "huella dinámica" del proceso: muestra cuánto cambia la salida, cuánto tarda en empezar a cambiar y qué tan rápido llega a su nuevo valor. Ziegler y Nichols (1942) propusieron sintonizar controladores a partir de esta sola prueba, sin necesidad de un modelo teórico; por eso estos métodos se llaman *semiempíricos*.

En esta práctica:

- Variable manipulada ($u$): agitación, de 200 a 500 rpm.
- Variable controlada ($y$): $pO_2$ en % de saturación.

![Escalón de agitación: de 200 a 500 rpm en el instante cero](../figuras/04_escalon_agitacion.png)

La línea vertical marca el cambio de agitación. Antes del instante cero mantenemos 200 rpm; después mantenemos 500 rpm mientras medimos el oxígeno. Este dibujo muestra el cambio que ordenamos en MAN; la respuesta del oxígeno se observa después.

Para que la curva sea útil:

1. El proceso debe estar estable antes del escalón ($pO_2$ estable).
2. Se hace un solo cambio, de golpe, y no se toca nada más.
3. Se espera hasta que la salida llegue a un nuevo valor estable.
4. El escalón debe ser lo bastante grande para verse claramente sobre el ruido, pero no tanto que el sistema salga de la zona de interés (aquí, entre ~65 y ~91 %).

La curva se resume con un modelo de primer orden con tiempo muerto (FOPDT):

No hace falta usar una función de transferencia: para esta actividad basta describir la curva con tres números.

- $K_p$ (ganancia): cuánto cambia el $pO_2$ por cada unidad de cambio en la agitación. $K_p = \Delta y/\Delta u$.
- $\theta$ (tiempo muerto): lo que tarda la señal en empezar a moverse. Incluye el mezclado y la respuesta de la sonda.
- $\tau$ (constante de tiempo): una medida de la rapidez de la respuesta. En este modelo, tras el tiempo muerto, en un tiempo $\tau$ se recorre aproximadamente el 63 % del cambio total; no significa que ya haya terminado.

Todos los equipos leen igual $y_0$, $y_\infty$ y $\Delta y = y_\infty - y_0$. Lo que cambia entre métodos es cómo se leen $\theta$ y $\tau$ (sección 7).


# 6. Antes de calcular: unidades y símbolos

$\Delta$ se lee «cambio»: valor final menos valor inicial. Por ejemplo, de 200 a 500 rpm, $\Delta u = 300$ rpm. $y_0$ es la lectura inicial y $y_\infty$ la lectura final estable; el subíndice $\infty$ no implica esperar infinitamente.

La salida de Biostat va de 0 a 100 % y se traduce en 200 a 1200 rpm en la configuración de esta práctica. Por tanto, el intervalo o **Span** es $1200 - 200 = 1000$ rpm. El escalón de 300 rpm equivale a 30 % de esa salida:

$$\Delta u_\% = 100\,\frac{\Delta u}{\text{Span}} = 100\,\frac{300}{1000} = 30\ \%$$

Para usar las reglas de la siguiente sección calculamos:

$$K_{p,\text{norm}} = \frac{y_\infty-y_0}{\Delta u_\%}$$

Esta ganancia describe **el proceso**: cuánto cambia el oxígeno por cada punto porcentual de salida. No es la ganancia $K_c$ **del controlador**. Por ejemplo, si el oxígeno pasa de 65 a 90 %, el cambio es 25 puntos y $K_{p,\text{norm}} = 25/30 = 0.83$.

Usa segundos en todos los tiempos. Las reglas darán $K_{c,\text{norm}}$ y el tiempo integral **TI**; después convertiremos la ganancia al campo **Xp** de la pantalla, como explica la nota final.

# 7. Cada método lee la curva a su manera

Para esta actividad asignamos a cada equipo una forma de estimar $\theta$ y $\tau$. SIMC e ITAE también pueden aplicarse a modelos obtenidos con otros procedimientos: esta elección es didáctica. Por tanto, la comparación incluye tanto la regla de ajuste como la lectura de la curva:

![Cómo lee la curva cada método](../figuras/12_B1.20261014.2_escalon2_criterios_vertical.png)

## Equipo 1: Ziegler-Nichols, recta tangente

1. Busca el tramo de **máxima pendiente**: entre qué dos lecturas consecutivas subió más el $pO_2$.
2. Traza una recta por ese tramo y prolóngala hacia abajo hasta $y_0$ y hacia arriba hasta $y_\infty$.
3. $\theta$ = tiempo desde $t_0$ hasta donde la recta cruza $y_0$.
4. $\tau$ = tiempo entre el cruce con $y_0$ y el cruce con $y_\infty$.

$$K_{c,\text{norm}} = \frac{0.9}{K_{p,\text{norm}}}\cdot\frac{\tau}{\theta}\qquad\qquad TI = 3.33\,\theta$$

## Equipo 2: SIMC, inicio de la respuesta y 63.2 %

1. $\theta$ = tiempo desde $t_0$ hasta la **primera lectura que sube 0.5 % o más sobre $y_0$** (cuando la respuesta empieza a notarse).
2. Calcula $y_{63} = y_0 + 0.632\,\Delta y$ y busca en qué tiempo $t_{63}$ se alcanza.
3. $\tau = t_{63} - \theta$ (con $t_{63}$ medido desde $t_0$).

$$K_{c,\text{norm}} = \frac{1}{K_{p,\text{norm}}}\cdot\frac{\tau}{2\theta}\qquad\qquad TI = \min(\tau,\ 8\theta)$$

Aquí $\min$ significa «elige el menor de los dos valores». Por ejemplo, si $\tau = 70$ s y $8\theta = 160$ s, TI = 70 s.

(Es la regla SIMC con $\tau_c = \theta$: $K_c = \tau / [K_p(\tau_c+\theta)]$, $\tau_I = \min[\tau, 4(\tau_c+\theta)]$.)

## Equipo 3: ITAE, dos puntos (Smith)

ITAE da más peso al error que persiste con el tiempo. En las fórmulas siguientes, usa la tecla de potencia de la calculadora para los exponentes decimales; primero calcula el cociente $\theta/\tau$.

1. Calcula $y_{28} = y_0 + 0.283\,\Delta y$ y $y_{63} = y_0 + 0.632\,\Delta y$.
2. Busca los tiempos $t_{28}$ y $t_{63}$ (medidos desde $t_0$).
3. $\tau = 1.5\,(t_{63} - t_{28})$ y $\theta = t_{63} - \tau$.

$$K_{c,\text{norm}} = \frac{0.859}{K_{p,\text{norm}}}\left(\frac{\theta}{\tau}\right)^{-0.977}\qquad\qquad TI = \frac{\tau}{0.674}\left(\frac{\theta}{\tau}\right)^{0.680}$$

**Antes de usar las reglas:** $K_{p,\text{norm}}$, $\theta$ y $\tau$ deben ser positivos. Si el tiempo muerto parece cero o sale negativo, revisar la lectura con el instructor; no dividir entre cero.

**En los tres casos:** $X_p = 100/K_{c,\text{norm}}$, **TD = 0 s**, **Deadband = 1.5 %**. TD se deja en cero porque las burbujas meten ruido en la señal de pO₂ y la acción derivativa lo amplificaría.


# 8. Seis personas, seis roles

1. **Operación:** cambia la agitación, introduce Xp/TI y cambia entre MAN y AUTO con el instructor.
2. **Tiempo:** marca el instante del escalón ($t_0$) y anuncia cada lectura.
3. **Registro:** anota oxígeno y rpm en la hoja de datos.
4. **Gráfica:** representa los datos y localiza los puntos que requiere el método.
5. **Cálculo:** obtiene las constantes con calculadora y las convierte a Xp y TI.
6. **Verificación y comparación:** revisa unidades y cálculos, registra la respuesta en automático y comparte los resultados.

# 9. Procedimiento (máximo 45 min por equipo)

| Min | Qué se hace | Agitador |
|---|---|---|
| 0–7 | Introducción y reparto de roles mientras el reactor se estabiliza. | MAN 200 rpm |
| 7–9 | Verificar pO₂ estable (cambio menor a 0.5 puntos en 1 min). Anotar $y_0$. | MAN 200 rpm |
| 9–17 | **Escalón:** cambiar de 200 a 500 rpm y marcar $t_0$. Registrar pO₂ cada 10 s durante 3 min, luego cada 30 s hasta estabilizarse. Anotar $y_\infty$. | MAN 500 rpm |
| 17–26 | Graficar y calcular $\Delta y$, $K_{p,\text{norm}}$, $\theta$, $\tau$, Xp y TI según el método del equipo. | MAN 500 rpm |
| 26–28 | Revisar cálculos con el instructor. Introducir Xp y TI; TD = 0 s; Deadband = 1.5 %. | MAN 500 rpm |
| 28–35 | **Prueba de setpoint:** pasar a AUTO con SP = 80 % si es alcanzable. Registrar pO₂ y rpm cada 15 s; observar mínimo, oscilación y tiempo de entrada en la banda 80 ± 1.5 %. | AUTO |
| 35–40 | **Segundo cambio de setpoint:** si ya está estable, cambiar de 80 a 85 % solo si ambos valores son alcanzables. Registrar máximo y tiempo de entrada en 85 ± 1.5 %. Si no se estabilizó, continuar la primera observación. | AUTO |
| 40–41 | Regresar a MAN 200 rpm para iniciar la recuperación antes del siguiente equipo. | MAN 200 rpm |
| 41–45 | Completar la comparación y discutir resultados. | MAN 200 rpm |

**El aire permanece fijo a 0.5 vvm (2.5 L/min) durante toda la actividad.** El segundo cambio es una prueba de seguimiento de setpoint; no es una prueba de perturbación. El método ITAE se calcula con una regla diseñada para perturbaciones, pero aquí solo observamos su respuesta a cambios de setpoint.

**¿Por qué 80 %?** En el piloto, a 200 rpm el oxígeno estaba cerca de 65 % y a 500 rpm cerca de 91 %. Por eso 80 % quedaba dentro del intervalo observado. Cada equipo debe verificar su propia curva: el cultivo cambia con el tiempo. No usar un setpoint fuera del intervalo observado para estas pruebas.

**¿Qué significa 80 ± 1.5 %?** Una banda de observación de 78.5 a 81.5 % de saturación, es decir, ±1.5 puntos porcentuales. Se configura además Deadband = 1.5 %; el instructor debe comprobar cómo aplica esa zona muerta la versión de la DCU instalada.

**Si falta tiempo o estabilidad:** no calcular a partir de una curva incompleta. El instructor puede proporcionar la curva del piloto para practicar los cálculos y señalar qué datos se usaron. Si una prueba no termina antes de su límite, registrar «no se estabilizó durante el tiempo observado». La recuperación a 200 rpm puede requerir más de 10 minutos: comprobarla antes del siguiente escalón, usando una pausa entre equipos si hace falta.

# 10. Hoja de datos

**Equipo:** ______  **Método:** ☐ Ziegler-Nichols ☐ SIMC ☐ ITAE  **Hora del escalón ($t_0$):** ________

**Escalón**

| u₀ | u₁ | Δu | Span | Δu% = 100·Δu / Span |
|---|---|---|---|---|
| 200 rpm | 500 rpm | 300 rpm | ______ rpm | ______ % |

**Registro de pO₂** (t medido desde $t_0$)

| t [s] | pO₂ [%] | t [s] | pO₂ [%] | t [s] | pO₂ [%] |
|---|---|---|---|---|---|
| −60 | | 70 | | 210 | |
| −30 | | 80 | | 240 | |
| 0 | | 90 | | 270 | |
| 10 | | 100 | | 300 | |
| 20 | | 110 | | 330 | |
| 30 | | 120 | | 360 | |
| 40 | | 150 | | 390 | |
| 50 | | 180 | | 420 | |
| 60 | | | | 450 | |

**Planta**

| y₀ [%] | y∞ [%] | Δy = y∞ − y₀ [%] | Kp,norm = Δy / Δu% |
|---|---|---|---|
| | | | |

**Lectura de θ y τ** (llena solo la de tu método)

| Método | Lo que se lee | Valor |
|---|---|---|
| Ziegler-Nichols | Tramo de máxima pendiente (entre qué tiempos) | ____ a ____ s |
| | Cruce de la tangente con $y_0$ → $\theta$ | ____ s |
| | Cruce de la tangente con $y_\infty$ → $\tau$ = cruce $y_\infty$ − cruce $y_0$ | ____ s |
| SIMC | Primera lectura ≥ $y_0$ + 0.5 % → $\theta$ | ____ s |
| | $y_{63} = y_0 + 0.632\,\Delta y$ → $t_{63}$ | ____ % → ____ s |
| | $\tau = t_{63} - \theta$ | ____ s |
| ITAE | $y_{28} = y_0 + 0.283\,\Delta y$ → $t_{28}$ | ____ % → ____ s |
| | $y_{63} = y_0 + 0.632\,\Delta y$ → $t_{63}$ | ____ % → ____ s |
| | $\tau = 1.5\,(t_{63} - t_{28})$; $\theta = t_{63} - \tau$ | τ = ____ s; θ = ____ s |

**Sintonía para la DCU**

| Kc,norm | Xp = 100 / Kc,norm | TI | TD | Deadband |
|---|---|---|---|---|
| | ______ % | ______ s | 0 s | 1.5 % |

# 11. Comparación de los tres equipos

| | Equipo 1: Z-N | Equipo 2: SIMC | Equipo 3: ITAE |
|---|---|---|---|
| $\theta$ [s] / $\tau$ [s] / $K_{p,\text{norm}}$ | | | |
| Xp [%] / TI [s] | | | |
| Setpoint: pO₂ mínimo al bajar a 80 % | | | |
| Setpoint: tiempo para quedar en 80 ± 1.5 % [s] | | | |
| ¿Oscila la agitación? | | | |
| Segundo setpoint: pO₂ máximo al subir a 85 % (si se realizó) | | | |
| Segundo setpoint: tiempo para entrar en 85 ± 1.5 % [s] | | | |


# 12. Preguntas para la discusión

1. **Misma curva, distintos números.** Los tres equipos obtuvieron un $\theta$ y un $\tau$ ligeramente distintos de curvas casi iguales. ¿De dónde viene la diferencia? ¿Cuál de las tres lecturas es más sensible a un error al leer la gráfica?
2. **Xp contra Kc.** Un equipo introduce por error su $K_{c,\text{norm}}$ (por ejemplo 3) en el campo Xp. ¿El controlador queda más agresivo o más suave que lo calculado, y por cuánto?
3. **El Span importa.** Si alguien supone Span = 600 rpm (cascada de 200 a 800) cuando en realidad es 1000 rpm, ¿su Xp sale más grande o más chico? ¿El controlador queda más agresivo o más suave?
4. **Alcance de la comparación.** Con aire fijo solo probamos cambios de setpoint. ¿Por qué estas observaciones no bastan para concluir qué método rechaza mejor un cambio en el consumo de oxígeno?
5. **Células sensibles.** Si en lugar de levadura fueran células animales sensibles al esfuerzo de corte y a la espuma, ¿qué método elegirías y por qué?


# Anexo para el instructor

## A. Preparar el reactor y el trabajo de los equipos

- **Configuración común:** 5 L de líquido, 30 °C y aire fijo a **0.5 vvm (2.5 L/min)** durante toda la actividad. Cascada de oxígeno con **solo agitación**, mínimo 200 y máximo 1200 rpm (Span = 1000 rpm). Verificar estos límites en pantalla antes de calcular.
- **Preparación propuesta para el taller:** 10 g/L de azúcar (50 g en 5 L) y 3 g/L de levadura seca (15 g). Rehidratar la levadura unos 15 min en aproximadamente 100 mL de agua tibia e inocular unos 20 min antes del primer equipo. Calibrar previamente la sonda al 100 % con aire a 30 °C.
- **Antes de cada escalón:** MAN a 200 rpm, oxígeno estable y registro activo. Mantener fijos aire, temperatura y composición durante la medición. Revisar que la agitación efectivamente pase a 500 rpm.
- **Entre equipos:** volver a MAN 200 rpm en el minuto 40. La recuperación observada tardó al menos 10 min; la explicación del siguiente equipo puede aprovechar parte de ese tiempo, pero no sustituye verificar estabilidad. Prever una pausa si hace falta.

## B. Qué se hizo el 14 de octubre de 2026

Se registraron dos escalones de **200 a 500 rpm** en el mismo lote, separados aproximadamente 30 min, en la hoja `B1.20261014.2` del Excel. Las notas del piloto indican **5 g/L de azúcar**; la preparación propuesta arriba usa 10 g/L. Por tanto, no presentar el piloto como una repetición con condiciones idénticas al taller. Verificar la concentración del día y anotarla.

El cultivo evolucionó entre escalones: el oxígeno inicial bajó de 68.8 a 65.7 %. Cada equipo debe obtener su propio valor inicial y final. Las cifras siguientes son referencias para revisar cálculos o trabajar con el piloto cuando no alcance el tiempo para obtener una curva completa.

![Registro del 14 de octubre: oxígeno disuelto y agitación durante los dos escalones y las pruebas posteriores](../figuras/05_piloto_14oct_registro.png)

En esta gráfica se muestran las mediciones originales de oxígeno y agitación. El registro disponible no contiene el modo MAN/AUTO, el setpoint ni los parámetros Xp/TI: las variaciones posteriores a cada escalón deben interpretarse junto con las notas de operación, sin asignarles automáticamente un método.

![Los dos escalones del 14 de octubre alineados: respuesta de oxígeno arriba y agitación medida abajo](../figuras/06_piloto_14oct_escalones.png)

Ambas curvas comienzan en el instante en que cambia la agitación. Aunque el oxígeno inicial cambia, el incremento total es parecido: 23.2 y 25.3 puntos porcentuales. El escalón de 300 rpm representa 30 % de salida con el Span de 1000 rpm usado en el recálculo.

## C. Ajustes recalculados para cada método

Estos resultados se obtuvieron **después del piloto**, leyendo las curvas con los criterios de la sección 7 y convirtiendo la ganancia con **Span = 1000 rpm**. Proceden del bloque `por_metodo` de los archivos de `resultados/`; los bloques `modelos` comparan otras estimaciones y no son los valores asignados a cada equipo.

| Lectura o ajuste | Escalón 1 | Escalón 2 |
|---|---|---|
| Oxígeno inicial / final [%] | 68.8 / 92.0 | 65.7 / 90.9 |
| Cambio de oxígeno [puntos] / $K_{p,\text{norm}}$ | 23.2 / 0.77 | 25.3 / 0.84 |
| Z-N: $\theta$ / $\tau$ [s] | 18 / 96 | 18 / 85 |
| **Z-N: Xp [%] / TI [s]** | **16.5 / 61** | **19.7 / 60** |
| SIMC: $\theta$ / $\tau$ [s] | 16 / 77 | 16 / 68 |
| **SIMC: Xp [%] / TI [s]** | **31.9 / 77** | **38.6 / 68** |
| ITAE: $\theta$ / $\tau$ [s] | 22 / 71 | 22 / 61 |
| **ITAE: Xp [%] / TI [s]** | **28.0 / 47** | **35.7 / 45** |

En todos los casos: **TD = 0 s** y **Deadband = 1.5 %**. No reutilizar sin comprobar los valores de Xp si cambió la configuración de la cascada.

![Lectura del segundo escalón del piloto para los tres métodos](../figuras/12_B1.20261014.2_escalon2_criterios_vertical.png)

### Qué revisar para que cada cálculo tenga sentido

| Método | Comprobación de la lectura | Cómo interpretar su ajuste |
|---|---|---|
| **Ziegler–Nichols** | Trazar la tangente sobre el tramo de subida más pronunciado, evitando elegir un salto aislado de ruido. Medir $\theta$ desde el escalón al cruce inferior; $\tau$ es la separación entre los dos cruces. | Dio el Xp más pequeño: una corrección proporcional más intensa. Vigilar oscilación y límites de rpm. |
| **SIMC** | Usar el inicio visible (umbral de 0.5 puntos sobre $y_0$) y el tiempo al 63.2 % del cambio. Restar el tiempo muerto para obtener $\tau$. El umbral es una aproximación didáctica y es sensible al ruido. | Aquí se eligió $\tau_c = \theta$. Un $\tau_c$ mayor en la regla general reduce la ganancia y permite un arranque más suave; recalcular también TI si se cambia esa elección. |
| **ITAE para perturbaciones** | Leer 28.3 % y 63.2 % **del cambio total**, no 28.3 y 63.2 % de saturación. Ambos tiempos parten del escalón. Revisar potencias y que $\theta$ resulte positivo. | Dio un TI más corto que SIMC: la corrección integral es más rápida. Su objetivo original son perturbaciones; los cambios de setpoint del taller no verifican ese objetivo. |

**Ejemplo de revisión, segundo escalón:** $\Delta y = 25.26$ puntos y $K_{p,\text{norm}} = 25.26/30 = 0.842$. Para ITAE, los niveles son aproximadamente 72.80 y 81.62 % de saturación, alcanzados a 42.21 y 83.04 s. Así, $\tau = 1.5(83.04-42.21) = 61.25$ s y $\theta = 83.04-61.25 = 21.79$ s. La regla da $K_{c,\text{norm}} = 2.80$, por lo que Xp = 35.7 % y TI = 45.0 s.

## D. Qué se probó realmente en automático

Las notas de operación del 14 de octubre reportan estos ajustes con **SP = 80 %**:

| Ajuste introducido | Observación anotada | Qué permite concluir |
|---|---|---|
| Xp = 10 %, TI = 80 s | Oscilación sostenida de oxígeno (aprox. 79–81.6 %) y agitación entre 200 y unas 500 rpm. | Ese ajuste produjo oscilación en aquellas condiciones. |
| Xp = 18 %, TI = 120 s, Deadband = 1.5 % | Oxígeno cerca de 79 % y agitación aproximadamente constante en 307 rpm. | Ese ajuste resultó más estable en esa prueba. Estar cerca de 79 % es compatible con la banda de observación alrededor de 80 %. |

**Estos dos ajustes no equivalen a probar los tres métodos de la tabla anterior.** Durante la sesión se usaron estimaciones preliminares de $\tau$ a partir del tiempo de estabilización ($\tau \approx t_s/4$) y un Span supuesto de 600 rpm. El recálculo posterior usa las lecturas de las curvas y Span = 1000 rpm. Por eso **Xp = 18 %, TI = 120 s no debe presentarse como el resultado de SIMC**, ni como una validación experimental de los ajustes recalculados.

Con el mismo TI y configuración, bajar Xp aumenta la acción proporcional; con el mismo Xp, bajar TI acelera la acción integral. Entre los dos ajustes ensayados cambiaron ambos parámetros, de modo que no puede atribuirse toda la diferencia a uno solo.

## E. Cómo comprobar y corregir el ajuste durante el taller

1. **Revisar antes de AUTO:** escala de oxígeno, Span real, conversión $X_p = 100/K_{c,\text{norm}}$, TI en segundos, TD = 0 y setpoint alcanzable. Si la salida aumenta, la agitación debe aumentar; en esta zona de operación se espera que eso eleve el oxígeno.
2. **Empezar por el ajuste calculado y registrar qué se introdujo.** Observar oxígeno y rpm juntos. Registrar tiempo de entrada en la banda, si permanece ahí y si la agitación oscila o se mantiene en un límite. No prometer que una regla garantiza estabilidad.
3. **Si hay oscilación sostenida:** volver a MAN si no conviene continuar. Revisar primero curva, ruido, unidades y saturación. Para una nueva prueba más suave se puede aumentar Xp o aumentar TI; cambiar un parámetro a la vez, anotar el nuevo valor y dejar tiempo para observar. Es una corrección posterior, distinta del resultado original del método.
4. **Si responde demasiado lento:** descartar primero setpoint inalcanzable, límite de agitación o cultivo todavía cambiante. Si el problema es el ajuste, reducir Xp o TI con el instructor, de uno en uno. Mantener el aire fijo.
5. **Si queda pegado en 200 o 1200 rpm:** comprobar si la agitación disponible basta para llegar al setpoint. Una salida limitada no se resuelve simplemente aumentando la ganancia. Si faltan minutos, documentar la limitación y cerrar la prueba.

**Aspectos del piloto que afectan la lectura:** el pH bajó aproximadamente de 5.8 a 4.5 y el oxígeno a 200 rpm siguió descendiendo con el tiempo. El intervalo automático fue de unos 5 s: con registro manual cada 10 s, la incertidumbre al leer un tiempo muerto de 15–22 s es apreciable. No exigir que la lectura manual reproduzca los decimales del análisis computacional.

Si el oxígeno inicial sube inesperadamente, revisar agitación, aire, sonda y estado del cultivo. El agotamiento del azúcar es una posibilidad, no una conclusión basada solo en la señal de oxígeno. Cualquier adición cambia las condiciones: anotarla y esperar un nuevo estado estable antes de repetir el escalón.

# Nota final: de las constantes del PI a los campos del Sartorius Biostat

En la configuración de esta práctica, la DCU pide **Xp, TI y TD**. TI es el tiempo integral en segundos y TD el derivativo (aquí, 0 s). **Xp es la banda proporcional**, por lo que no debemos escribir directamente la ganancia $K_c$ en ese campo.

Las reglas de la sección 7 usan una salida normalizada de 0 a 100 %. Con el oxígeno expresado sobre una escala de 0 a 100 % de saturación:

$$X_p = \frac{100}{K_{c,\text{norm}}}$$

Por ejemplo, si calculamos $K_{c,\text{norm}} = 2.5$ y $T_I = 70$ s, introducimos **Xp = 40 %, TI = 70 s y TD = 0 s**. Una banda Xp menor produce una corrección proporcional mayor. En ese ejemplo, un error de 4 puntos de oxígeno aporta una corrección P de 10 puntos de salida, equivalentes a 100 rpm con Span = 1000 rpm; la acción integral se suma a esa corrección.

Si el cálculo se hizo con la agitación en rpm, en vez de porcentajes, la ganancia $K_c$ tendrá unidades de rpm por punto de oxígeno. En ese caso el atajo es **$X_p = \text{Span}/K_c$**. No mezclar esa ganancia con $K_{c,\text{norm}}$.

Antes de introducir valores, comprobar que la cascada usa solo agitación, sus límites reales y la escala de medición de oxígeno: si cambia el Span o la escala, cambia la conversión. La documentación de Sartorius describe [los campos XP, TI, TD y DEADB en sus controladores DCU](https://www.sartorius.com/download/10106/biostat-d-dcu-customer-presentation-v2-data.pdf); los límites y la configuración concreta deben verificarse en el Biostat B de la actividad.

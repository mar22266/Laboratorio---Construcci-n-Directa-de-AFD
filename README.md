# Regex to AFD

Este proyecto implementa una herramienta en Python que convierte una expresión regular en un Autómata Finito Determinista (AFD) utilizando el algoritmo de FollowPos. La aplicación procesa la expresión regular en varias etapas: inserción de operadores de concatenación, conversión a notación postfija, construcción del árbol de sintaxis, cálculo de las funciones `firstpos`, `lastpos` y `followpos`, y finalmente, la construcción del AFD.


## Descripción

El programa realiza los siguientes pasos:

1. **Inserción de operadores de concatenación:**  
   Agrega operadores de concatenación explícitos a la expresión regular cuando sea necesario.

2. **Conversión a notación postfija:**  
   Transforma la expresión regular de su forma infija a notación postfija (Reverse Polish Notation) utilizando el algoritmo Shunting-yard.

3. **Construcción del árbol de sintaxis:**  
   Genera un árbol sintáctico a partir de la expresión postfija, donde cada nodo representa un operando o un operador (como `|`, `.`, `*`).

4. **Cálculo de FollowPos:**  
   Calcula la función `followpos` para cada posición del árbol, lo cual es fundamental para la generación del AFD.

5. **Construcción del AFD:**  
   Utiliza la información del árbol y de `followpos` para construir el Autómata Finito Determinista, definiendo sus estados y transiciones.

6. **Impresión del AFD:**  
   Muestra los estados y las transiciones resultantes en la consola.

## Características

- Conversión de expresión regular infija a notación postfija.
- Inserción automática de operadores de concatenación.
- Construcción y evaluación de un árbol de sintaxis.
- Cálculo de las funciones `firstpos`, `lastpos` y `followpos`.
- Construcción e impresión de un AFD basado en la expresión regular ingresada.


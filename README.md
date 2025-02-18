# Implementación del AFD Directo y AFD Minimizado

Este laboratorio implementa la conversión de expresiones regulares (regexp) en autómatas finitos deterministas (AFD), tanto en su versión directa como minimizada. A continuación, se detallan los pasos y el diseño de la implementación de cada parte del laboratorio.

## 1. AFD Directo

### Descripción

La implementación del AFD directo convierte una expresión regular en un autómata finito determinista (AFD) utilizando un enfoque directo desde la regexp hasta el AFD. A continuación, se describen las funciones principales que permiten realizar esta conversión.

### Clases y Funciones

#### Clase `Node`

La clase `Node` representa los nodos en el árbol sintáctico de la expresión regular. Cada nodo tiene:

- Un valor que puede ser un operador o un operando.
- Nodos hijos izquierdo y derecho.
- Conjuntos como `primerapos`, `ultimapos` y `anulable`, que son utilizados en los siguientes pasos del algoritmo.

#### Funciones para la Preparación de la Expresión Regular

- **`is_operator` y `is_operand`**: Identifican si un carácter es un operador o un operando (símbolo o letra).
- **`insert_concatenation_operators`**: Asegura que los operadores de concatenación (.) estén correctamente insertados en la expresión regular.
- **`toPostFix`**: Convierte la expresión regular de notación infix a notación postfix.

#### Construcción del Árbol Sintáctico

- **`build_syntax_tree`**: Convierte la expresión regular en notación postfix a un árbol de sintaxis utilizando una pila. Se procesan operadores como la unión (`|`), concatenación (`.`) y cerradura de Kleene (`*`).

#### Cálculo de Propiedades de los Nodos

- **`nullable`**: Determina si un nodo puede generar una cadena vacía (epsilon). Depende del tipo de nodo (operando, unión, concatenación, cerradura de Kleene).
- **`primerapos`**: Conjunto de posiciones que pueden aparecer primero en la cadena derivada de un nodo.
- **`ultimapos`**: Conjunto de posiciones que pueden aparecer al final de la cadena derivada de un nodo.
- **`siguientepos`**: Calcula las posiciones a las que se puede llegar desde una posición dada.

#### Construcción del AFD

- **`construct_afd`**: Utiliza la información calculada (como `primerapos`, `ultimapos` y `siguientepos`) para construir el AFD a partir del árbol sintáctico.

#### Minimización del AFD

- **`minimize_afd`**: Minimiza el AFD utilizando el algoritmo de partición de estados equivalentes.

#### Visualización del AFD

- **`visualize_afd` y `visualize_minimized_afd`**: Generan representaciones gráficas del AFD original y minimizado usando la librería `graphviz`.

#### Verificación de Cadenas

- **`procesar_cadena`**: Permite verificar si una cadena es aceptada por el AFD minimizado.

### Flujo del AFD Directo

1. Se sanitiza la expresión regular.
2. Se convierte la expresión regular a notación postfix.
3. Se construye el árbol sintáctico a partir de la notación postfix.
4. Se calculan las propiedades como anulabilidad, `primerapos`, `ultimapos` y `siguientepos`.
5. Se construye el AFD.
6. Se minimiza el AFD.
7. Se visualizan el AFD original y el minimizado.
8. Se puede probar si una cadena es aceptada por el AFD.

## 2. Explicación de la implementación siguiendo todos los pasos para poder calcular el AFD minimizado.

### Descripción

La implementación para calcular el AFD minimizado sigue una serie de pasos estructurados en módulos, cada uno enfocado en una tarea específica. El diseño modular facilita la implementación y el mantenimiento del código.

### Diseño de la Aplicación

La aplicación está dividida en los siguientes módulos:

#### Módulo 1: Algoritmo Shunting Yard

Convierte la expresión regular de notación infix a notación postfix.

- **Entrada**: Expresión regular en notación infix.
- **Salida**: Expresión en notación postfix.

#### Módulo 2: Conversión de Regex a AFN (Algoritmo de Thompson)

Convierte la expresión regular en notación postfix a un autómata finito no determinista (AFN) utilizando el algoritmo de Thompson.

- **Entrada**: Expresión regular en notación postfix.
- **Salida**: Un AFN con transiciones y estados de aceptación.

#### Módulo 3: Construcción de Subconjuntos

Convierte el AFN en un AFD utilizando el algoritmo de construcción de subconjuntos.

- **Entrada**: AFN con transiciones y estados.
- **Salida**: Un AFD determinista.

#### Módulo 4: Minimización del AFD

Implementa un algoritmo de minimización para reducir el número de estados del AFD manteniendo el mismo comportamiento.

- **Entrada**: AFD generado.
- **Salida**: AFD minimizado.

#### Módulo 5: Simulación

Permite simular la aceptación o rechazo de una cadena de entrada utilizando el AFD minimizado.

- **Entrada**: AFD minimizado y cadena de prueba.
- **Salida**: Resultado de aceptación o rechazo de la cadena.

### Interfaz de Usuario (UI)

Se implementó una interfaz de línea de comandos (CLI) que permite al usuario ingresar una expresión regular, generar los autómatas correspondientes y probar diferentes cadenas de manera directa.

## Cómo Ejecutar el laboratorio

1. Clona el repositorio en tu máquina local.
2. Instala las dependencias necesarias.
3. Compila el laboratorio.
4. Ejecuta el programa en la línea de comandos.

Para usar la aplicación:

```python
python .\Primera_parte\regexpToAFD.py
python .\Segunda_parte\simulate.py
```

El sistema te pedirá que ingreses una expresión regular, y luego generará el AFD correspondiente. Podrás probar diferentes cadenas y ver si son aceptadas por el autómata.

## Referencias

1. Aho, A. V., Sethi, R., & Ullman, J. D. (1986). Compilers. Pearson.
2. ast — Abstract Syntax Trees. (s. f.). Python Documentation. https://docs.python.org/3/library/ast.html
3. E. Rafael. (2015.) CURSO: PROGRAMACION DE SISTEMAS. https://slideplayer.es/slide/1674667/
4. How to find the last occurrence of an item in a Python list. (s. f.). Stack Overflow. https://stackoverflow.com/questions/6890170/how-to-find-the-last-occurrence-of-an-item-in-a-python-list
5. José Luis Gómez Ramos. (2022, 28 noviembre). Árbol Binario de Expresiones utilizando Python [Vídeo]. YouTube. https://www.youtube.com/watch?v=ic7pbN3UKkI

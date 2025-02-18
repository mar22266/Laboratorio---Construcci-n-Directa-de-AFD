# Laboratorio - Construcción directa de un AFD a partir de una expresión regular
# Andre Marroquin 22266
# Rodrigo Mansilla
# Sergio Orellana 221122

"""
Referencias

https://programminghistorian.org/es/lecciones/manipular-cadenas-de-caracteres-en-python

"""

# Importamos las librerías necesarias
import itertools
from colorama import Fore, Style
import graphviz
import os
import string


# Clase Nodo encargada de inicializar los valores de los nodos en el árbol de sintaxis
class Node:
    """
    Esta parte se hizo con ayuda de LLMs para poder entender mejor el funcionamiento de los nodos

    Promt utilizado:

    Could you give me a structure or class of node type in python where I can represent the important parts of an AFD with direct construction, I want it to have, the value of the node, if it has children (both left and right), if it is voidable, a set of sets for first pos, another for last pos and another for the identification of the position.
    """

    def __init__(self, value, left=None, right=None):
        self.value = value  # Valor del nodo
        self.left = left  # Nodo izquierdo
        self.right = right  # Nodo derecho
        self.nullable = False  # Esto funciona para representar si es anulable o no
        self.firstpos = set()  # Contiene el conjunto de posiciones de primera-pos
        self.lastpos = set()  # # Contiene el conjunto de posiciones de última-pos
        self.position = None  # Sirve para identificar la posición del nodo


# Función para sanitizar el nombre de la carpeta
def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name)


# Definimos las precedencias de los operadores
precedence = {"|": 1, ".": 2, "*": 3}


# Función que verifica si es un operador
def is_operator(c: str) -> bool:
    return c in precedence


# Función que verifica si es un operando
def is_operand(c: str) -> bool:
    return c.isalnum() or c == "_" or c == "#"


# Función que inserta operadores de concatenación (Se utilizó el mismo algoritmo que se implementó el semestre pasado)
def insert_concatenation_operators(infix: str) -> str:
    result = []
    length = len(infix)

    for i in range(length):
        result.append(infix[i])

        if i < length - 1:
            if (
                (
                    is_operand(infix[i])
                    and (is_operand(infix[i + 1]) or infix[i + 1] == "(")
                )
                or (
                    infix[i] == ")"
                    and (is_operand(infix[i + 1]) or infix[i + 1] == "(")
                )
                or (
                    infix[i] == "*"
                    and (is_operand(infix[i + 1]) or infix[i + 1] == "(")
                )
            ):
                result.append(".")

    return "".join(result)


# Función que convierte la expresión regular a postfix (Se utilizó el mismo algoritmo que se implementó el semestre pasado)
def toPostFix(infixExpression: str) -> str:
    infixExpression = insert_concatenation_operators(infixExpression)
    output = []
    operators = []

    i = 0
    while i < len(infixExpression):
        c = infixExpression[i]
        if is_operand(c):
            output.append(c)
        elif c == "(":
            operators.append(c)
        elif c == ")":
            while operators and operators[-1] != "(":
                output.append(operators.pop())
            operators.pop()
        elif is_operator(c):
            while (
                operators
                and operators[-1] != "("
                and precedence[operators[-1]] >= precedence[c]
            ):
                output.append(operators.pop())
            operators.append(c)
        i += 1

    while operators:
        output.append(operators.pop())

    return "".join(output)


# Función que construye el árbol de sintaxis
def build_syntax_tree(postfix):
    stack = []  # Pila para almacenar los nodos
    pos_counter = itertools.count(1)  # Contador para las posiciones
    position_symbol_map = {}  # Diccionario para mapear las posiciones a los símbolos

    # Recorremos la expresión postfix
    for char in postfix:
        # Si es un operando, creamos un nodo y lo agregamos a la pila
        if is_operand(char):
            node = Node(char)
            node.position = next(pos_counter)  # Asignamos la siguiente posición al nodo
            node.firstpos.add(node.position)  # Añadimos la posición a firstpos
            node.lastpos.add(node.position)  # Añadimos la posición a lastpos
            position_symbol_map[node.position] = char  # Mapeamos la posición al símbolo
            stack.append(node)  # Agregamos el nodo a la pila

        # Si el caracter es una cerradura de Kleene
        elif char == "*":
            child = stack.pop()  # Sacamos el nodo de la pila
            node = Node("*", left=child)  # Creamos un nodo con el operador *
            node.nullable = True  # El nodo es anulable ya que la cerradura de Kleene produce un vacío
            node.firstpos = child.firstpos  # firstpos es igual al firstpos del hijo
            node.lastpos = child.lastpos  # lastpos es igual al lastpos del hijo
            stack.append(node)  # Agregamos el nodo a la pila

        # Si el caracter es una concatenación
        elif char == ".":
            right = stack.pop()  # Sacamos el nodo derecho de la pila
            left = stack.pop()  # Sacamos el nodo izquierdo de la pila
            node = Node(
                ".", left, right
            )  # Creamos un nodo con el operador "." (concatenación)
            node.nullable = (
                left.nullable and right.nullable
            )  # El nodo es anulable si ambos hijos lo son
            node.firstpos = left.firstpos | (
                right.firstpos if left.nullable else set()
            )  # firstpos es la unión de los firstpos de los hijos si c1 o el hijo izquierdo es anulable de caso contrario se toma el firstpos del hijo izquierdo (c1)
            node.lastpos = right.lastpos | (
                left.lastpos if right.nullable else set()
            )  # lastpos es la unión de los lastpos de los hijos si c2 o el hijo derecho es anulable de caso contrario se toma el lastpos del hijo derecho (c2)
            stack.append(node)

        # Si el caracter es una unión
        elif char == "|":
            right = stack.pop()
            left = stack.pop()
            node = Node("|", left, right)  # Creamos un nodo con el operador |
            node.nullable = (
                left.nullable or right.nullable
            )  # El nodo es anulable si alguno de los hijos lo es
            node.firstpos = (
                left.firstpos | right.firstpos
            )  # firstpos es la unión de los firstpos de los hijos
            node.lastpos = (
                left.lastpos | right.lastpos
            )  # lastpos es la unión de los lastpos de los hijos
            stack.append(node)

    return stack.pop(), position_symbol_map


# Función que calcula el siguientepos
def compute_followpos(node, followpos):
    # Si el nodo es nulo, retornamos None porque lo único que nos sirve para el siguiente pos es la cerradura de Kleene y la concatenación
    if node is None:
        return

    # Si el nodo es una concatenación
    if node.value == ".":
        # Entonces para cada posición en lastpos del hijo izquierdo se encuentran en las posiciones de firstpos del hijo derecho
        for pos in node.left.lastpos:
            followpos[pos] |= node.right.firstpos

    # Si el nodo es una cerradura de Kleene
    if node.value == "*":
        # Entonces para cada posición en lastpos del hijo se encuentran en las posiciones de firstpos del hijo
        for pos in node.lastpos:
            followpos[pos] |= node.firstpos

    # Llamamos recursivamente a la función para el hijo izquierdo y el hijo derecho
    compute_followpos(node.left, followpos)
    compute_followpos(node.right, followpos)


# Función que construye el AFD
def construct_afd(root, position_symbol_map):
    followpos = {pos: set() for pos in position_symbol_map}
    compute_followpos(root, followpos)

    states = {}
    state_queue = [frozenset(root.firstpos)]
    transitions = {}
    state_names = {}
    current_name = itertools.count(ord("A"))
    accepting_states = set()

    while state_queue:
        state = state_queue.pop(0)
        if not state:
            continue

        # Si el estado no está en el diccionario de estados, lo agregamos
        if state not in state_names:
            state_names[state] = chr(next(current_name))
            states[state_names[state]] = state

        # Mapeamos los símbolos a los siguientes estados
        symbol_map = {}

        for pos in state:
            symbol = position_symbol_map.get(pos)
            # Si el símbolo no es "#" ni "_", lo agregamos al mapeo
            if symbol and symbol != "#" and symbol != "_":
                # Si el símbolo no está en el mapeo, lo agregamos y le asignamos un conjunto vacío
                if symbol not in symbol_map:
                    symbol_map[symbol] = set()

                # Agregamos las posiciones de followpos al mapeo
                symbol_map[symbol] |= followpos.get(pos, set())

        # Para cada símbolo en el mapeo, creamos un nuevo estado
        for symbol, next_state in symbol_map.items():
            # Si el siguiente estado no está en el diccionario de estados, lo agregamos
            next_state = frozenset(next_state)
            if not next_state:
                continue

            # Si el siguiente estado no está en el diccionario de estados, lo agregamos y lo agregamos a la cola de estados a procesar
            if next_state not in state_names:
                state_queue.append(next_state)
                state_names[next_state] = chr(next(current_name))
                states[state_names[next_state]] = next_state

            # Agregamos la transición al diccionario de transiciones
            transitions[(state_names[state], symbol)] = state_names[next_state]

    # Estados de aceptación
    for state_name, positions in states.items():
        if any(position_symbol_map.get(pos) == "#" for pos in positions):
            accepting_states.add(state_name)

    return states, transitions, accepting_states


# Función para imprimir el AFD
def print_afd(states, transitions, accepting_states):
    print(Fore.CYAN + "\n--- Tabla de Estados - AFD directo ---" + Style.RESET_ALL)
    for state, positions in states.items():
        highlight = Fore.YELLOW if state in accepting_states else ""
        print(f"{highlight}Estado {state}: {sorted(positions)}{Style.RESET_ALL}")

    print(Fore.CYAN + "\n--- Transiciones ---" + Style.RESET_ALL)
    for (state, symbol), next_state in transitions.items():
        highlight = Fore.YELLOW if state in accepting_states else ""
        print(f"{highlight}{state} --({symbol})--> {next_state}{Style.RESET_ALL}")

    if accepting_states:
        print(
            Fore.YELLOW
            + f"\nEstados de aceptación: {', '.join(accepting_states)}"
            + Style.RESET_ALL
        )


# Función para imprimir el AFD minimizado
def print_mini_afd(states, transitions, accepting_states):
    print(Fore.CYAN + "\n--- Tabla de Estados - AFD Minimizado ---" + Style.RESET_ALL)
    for state, positions in states.items():
        highlight = Fore.YELLOW if state in accepting_states else ""
        print(f"{highlight}Estado {state}: {sorted(positions)}{Style.RESET_ALL}")

    print(Fore.CYAN + "\n--- Transiciones ---" + Style.RESET_ALL)
    for (state, symbol), next_state in transitions.items():
        highlight = Fore.YELLOW if state in accepting_states else ""
        print(f"{highlight}{state} --({symbol})--> {next_state}{Style.RESET_ALL}")

    if accepting_states:
        print(
            Fore.YELLOW
            + f"\nEstados de aceptación: {', '.join(accepting_states)}"
            + Style.RESET_ALL
        )


"""

Esta función se realizó con ayuda de LLMs para poder entender mejor el funcionamiento de la minimización de un AFD

Promt utilizado:

Could you help me with a function that minimizes an AFD using the method of equivalent state partitioning? I need to minimize the AFD that I built from a regular expression. I need to minimize the states, transitions, and accepting states if possible.

"""


def minimize_afd(states, transitions, accepting_states):
    """
    Implementa la minimización de un AFD utilizando el método de partición de estados equivalentes.
    """

    # 1. Inicializar particiones
    P = [set(accepting_states), set(states.keys()) - set(accepting_states)]
    W = [
        set(accepting_states),
        set(states.keys()) - set(accepting_states),
    ]  # Conjunto de trabajo

    def get_partition(state, partitions):
        """Devuelve el índice de la partición a la que pertenece un estado."""
        for i, group in enumerate(partitions):
            if state in group:
                return i
        return None

    # 2. Refinar particiones hasta que sean estables
    while W:
        A = W.pop()  # Extraemos un grupo de trabajo

        for symbol in set(sym for _, sym in transitions.keys()):
            X = {
                state
                for state in states
                if (state, symbol) in transitions and transitions[(state, symbol)] in A
            }

            for Y in P[:]:  # Iteramos sobre una copia de P
                interseccion = X & Y
                diferencia = Y - X

                if interseccion and diferencia:
                    P.remove(Y)  # Eliminamos el conjunto original
                    P.append(interseccion)  # Agregamos las nuevas particiones
                    P.append(diferencia)

                    # Actualizar W con las nuevas particiones si es necesario
                    if Y in W:
                        W.remove(Y)
                        W.append(interseccion)
                        W.append(diferencia)
                    else:
                        W.append(
                            interseccion
                            if len(interseccion) <= len(diferencia)
                            else diferencia
                        )

    # 3. Construcción del nuevo AFD minimizado
    new_states = {chr(65 + i): group for i, group in enumerate(P)}
    state_mapping = {
        state: new_state for new_state, group in new_states.items() for state in group
    }

    new_transitions = {}
    for (state, symbol), next_state in transitions.items():
        new_transitions[(state_mapping[state], symbol)] = state_mapping[next_state]

    # Determinar el nuevo estado inicial
    initial_state = "A"  # Estado inicial del AFD original
    new_initial_state = state_mapping[initial_state]

    # Determinar los nuevos estados de aceptación
    new_accepting_states = {
        new_state
        for new_state, group in new_states.items()
        if any(s in accepting_states for s in group)
    }

    return new_states, new_transitions, new_accepting_states, new_initial_state


# Función para generar la representación gráfica del AFD en una carpeta específica
def visualize_afd(states, transitions, accepting_states, regex):
    sanitized_regex = sanitize_filename(regex)
    output_dir = f"./Primera_parte/grafos/{sanitized_regex}/direct_AFD"
    os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe

    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")

    # Nodo especial para el estado inicial
    dot.node("start", shape="none", label="Inicio")
    dot.edge("start", "A")  # Flecha hacia el estado inicial

    for state in states:
        if state in accepting_states:
            dot.node(state, state, shape="doublecircle", color="blue")
        else:
            dot.node(state, state, shape="circle")

    for (state, symbol), next_state in transitions.items():
        dot.edge(state, next_state, label=symbol)

    output_path = os.path.join(output_dir, "grafo_AFD")
    dot.render(output_path, view=True)


# Función para generar la representación gráfica del AFD minimizado
def visualize_minimized_afd(
    states, transitions, accepting_states, initial_state, regex
):
    """
    Genera la representación gráfica del AFD minimizado.
    """

    # Sanitizar el nombre de la expresión regular para crear la carpeta
    sanitized_regex = sanitize_filename(regex)
    output_dir = f"./Primera_parte/grafos/{sanitized_regex}/minimize_AFD"
    os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe

    # Crear el objeto Graphviz
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")  # Dirección de izquierda a derecha

    # Nodo especial para el estado inicial
    dot.node("start", shape="none", label="Inicio")
    dot.edge("start", initial_state)  # Flecha hacia el estado inicial

    # Dibujar los estados
    for state in states:
        if state in accepting_states:
            dot.node(
                state, state, shape="doublecircle", color="blue"
            )  # Estado de aceptación
        else:
            dot.node(state, state, shape="circle")  # Estado normal

    # Dibujar las transiciones
    for (state, symbol), next_state in transitions.items():
        dot.edge(state, next_state, label=symbol)

    # Guardar y visualizar el gráfico
    output_path = os.path.join(output_dir, "grafo_mini_AFD")
    dot.render(output_path, view=True)


# Función para procesar cadenas y verificar si son aceptadas por el AFD
def procesar_cadena(afd_transitions, accepting_states, initial_state, input_string):
    current_state = initial_state

    for symbol in input_string:
        if (current_state, symbol) in afd_transitions:
            current_state = afd_transitions[(current_state, symbol)]
        else:
            print(
                Fore.RED
                + f"La cadena '{input_string}' NO es aceptada."
                + Style.RESET_ALL
            )
            return False

    if current_state in accepting_states:
        print(Fore.GREEN + f"La cadena '{input_string}' es aceptada." + Style.RESET_ALL)
        return True
    else:
        print(
            Fore.RED + f"La cadena '{input_string}' NO es aceptada." + Style.RESET_ALL
        )
        return False


# Main del programa
if __name__ == "__main__":
    regex = input(
        Fore.GREEN
        + "Ingresa la regexp que deseas convertir a AFD (or = '|', '+', Cerradura de Kleene = '*'): "
        + Style.RESET_ALL
    )
    regex += "#"
    postfix = toPostFix(regex)
    syntax_tree, position_symbol_map = build_syntax_tree(postfix)
    states, transitions, accepting_states = construct_afd(
        syntax_tree, position_symbol_map
    )

    new_states, new_transitions, new_accepting_states, new_initial_state = minimize_afd(
        states, transitions, accepting_states
    )

    # Prints de los AFD
    print_afd(states, transitions, accepting_states)
    print_mini_afd(new_states, new_transitions, new_accepting_states)

    # Generar visualización del AFD directo y minimizado
    visualize_afd(states, transitions, accepting_states, regex)
    visualize_minimized_afd(
        new_states, new_transitions, new_accepting_states, new_initial_state, regex
    )

    # Probar cadenas en el AFD minimizado
    while True:
        test_string = input(
            Fore.CYAN
            + "\nIngresa una cadena para probar (o 'salir' para terminar): "
            + Style.RESET_ALL
        ).strip()

        if test_string.lower() == "salir":
            break

        procesar_cadena(
            new_transitions, new_accepting_states, new_initial_state, test_string
        )

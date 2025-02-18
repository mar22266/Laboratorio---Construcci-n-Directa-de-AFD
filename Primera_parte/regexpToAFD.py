# Andre Marroquin 22266
# Rodrigo Mansilla
# Sergio Orellana 22122

# Importamos las librerías necesarias
import itertools
from colorama import Fore, Style
import graphviz
import os
import string


# Clase Nodo encargada de inicializar los valores de los nodos
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()
        self.position = None


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


# Función que inserta operadores de concatenación
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


# Función que convierte la expresión regular a postfijo
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
    stack = []
    pos_counter = itertools.count(1)
    position_symbol_map = {}

    for char in postfix:
        if is_operand(char):
            node = Node(char)
            node.position = next(pos_counter)
            node.firstpos.add(node.position)
            node.lastpos.add(node.position)
            position_symbol_map[node.position] = char
            stack.append(node)
        elif char == "*":
            child = stack.pop()
            node = Node("*", left=child)
            node.nullable = True
            node.firstpos = child.firstpos
            node.lastpos = child.lastpos
            stack.append(node)
        elif char == ".":
            right = stack.pop()
            left = stack.pop()
            node = Node(".", left, right)
            node.nullable = left.nullable and right.nullable
            node.firstpos = left.firstpos | (right.firstpos if left.nullable else set())
            node.lastpos = right.lastpos | (left.lastpos if right.nullable else set())
            stack.append(node)
        elif char == "|":
            right = stack.pop()
            left = stack.pop()
            node = Node("|", left, right)
            node.nullable = left.nullable or right.nullable
            node.firstpos = left.firstpos | right.firstpos
            node.lastpos = left.lastpos | right.lastpos
            stack.append(node)

    return stack.pop(), position_symbol_map


# Función que calcula el followpos
def compute_followpos(node, followpos):
    if node is None:
        return

    if node.value == ".":
        for pos in node.left.lastpos:
            followpos[pos] |= node.right.firstpos

    if node.value == "*":
        for pos in node.lastpos:
            followpos[pos] |= node.firstpos

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

        if state not in state_names:
            state_names[state] = chr(next(current_name))
            states[state_names[state]] = state

        symbol_map = {}
        for pos in state:
            symbol = position_symbol_map.get(pos)
            if symbol and symbol != "#" and symbol != "_":
                if symbol not in symbol_map:
                    symbol_map[symbol] = set()
                symbol_map[symbol] |= followpos.get(pos, set())

        for symbol, next_state in symbol_map.items():
            next_state = frozenset(next_state)
            if not next_state:
                continue

            if next_state not in state_names:
                state_queue.append(next_state)
                state_names[next_state] = chr(next(current_name))
                states[state_names[next_state]] = next_state

            transitions[(state_names[state], symbol)] = state_names[next_state]

    # Estados de aceptación
    for state_name, positions in states.items():
        if any(position_symbol_map.get(pos) == "#" for pos in positions):
            accepting_states.add(state_name)

    return states, transitions, accepting_states


# Función para imprimir el AFD
def print_afd(states, transitions, accepting_states):
    print(Fore.CYAN + "\n--- Tabla de Estados ---" + Style.RESET_ALL)
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
    print(Fore.CYAN + "\n--- Tabla de Estados ---" + Style.RESET_ALL)
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


def minimize_afd(states, transitions, accepting_states):
    """Minimiza un AFD utilizando la partición de estados equivalentes."""

    # Paso 1: Inicializar particiones de estados de aceptación y no aceptación
    P = [set(accepting_states), set(states.keys()) - set(accepting_states)]

    def get_partition(state):
        """Devuelve el índice de la partición a la que pertenece el estado."""
        for i, group in enumerate(P):
            if state in group:
                return i
        return None

    # Paso 2: Refinar particiones hasta que sean estables
    changed = True
    while changed:
        changed = False
        new_P = []

        for group in P:
            partition_map = {}

            for state in group:
                signature = tuple(
                    (symbol, get_partition(transitions.get((state, symbol), None)))
                    for symbol in sorted(set(sym for _, sym in transitions.keys()))
                )

                if signature not in partition_map:
                    partition_map[signature] = set()
                partition_map[signature].add(state)

            new_P.extend(partition_map.values())

        if new_P != P:
            P = new_P
            changed = True

    # Paso 3: Construir nuevo AFD minimizado
    new_states = {chr(65 + i): group for i, group in enumerate(P)}
    state_mapping = {
        state: new_state for new_state, group in new_states.items() for state in group
    }

    new_transitions = {}
    for (state, symbol), next_state in transitions.items():
        new_transitions[(state_mapping[state], symbol)] = state_mapping[next_state]

    new_accepting_states = {
        new_state for new_state, group in new_states.items() if group & accepting_states
    }

    return new_states, new_transitions, new_accepting_states


# Función para generar la representación gráfica del AFD en una carpeta específica
def visualize_afd(states, transitions, accepting_states, regex):
    sanitized_regex = sanitize_filename(regex)
    output_dir = f"./Primera_parte/grafos/{sanitized_regex}/direct_AFD"
    os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe

    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")

    for state in states:
        if state in accepting_states:
            dot.node(state, state, shape="doublecircle", color="blue")
        else:
            dot.node(state, state, shape="circle")

    for (state, symbol), next_state in transitions.items():
        dot.edge(state, next_state, label=symbol)

    output_path = os.path.join(output_dir, "grafo_AFD")
    dot.render(output_path, view=False)


# Función para generar la representación gráfica del AFD minimizado
def visualize_minimized_afd(states, transitions, accepting_states, regex):
    sanitized_regex = sanitize_filename(regex)
    output_dir = f"./Primera_parte/grafos/{sanitized_regex}/minimize_AFD"
    os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe

    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")

    for state in states:
        if state in accepting_states:
            dot.node(state, state, shape="doublecircle", color="blue")
        else:
            dot.node(state, state, shape="circle")

    for (state, symbol), next_state in transitions.items():
        dot.edge(state, next_state, label=symbol)

    output_path = os.path.join(output_dir, "grafo_mini_AFD")
    dot.render(output_path, view=False)


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

    visualize_afd(states, transitions, accepting_states, regex)
    visualize_minimized_afd(states, transitions, accepting_states, regex)

    while True:
        test_string = input(
            Fore.CYAN
            + "\nIngresa una cadena para probar (o 'salir' para terminar): "
            + Style.RESET_ALL
        ).strip()

        if test_string.lower() == "salir":
            break

        procesar_cadena(transitions, accepting_states, "A", test_string)

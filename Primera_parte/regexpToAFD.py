# Andre Marroquin 22266
# Rodrigo Mansilla
# Sergio Orellana 22122

# Importamos las librerías necesarias
import itertools
from colorama import Fore, Style
import graphviz


# Definimos signos
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
            if symbol and symbol != "#":
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


# Función para generar la representación gráfica del AFD
def visualize_afd(states, transitions, accepting_states):
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")

    for state in states:
        if state in accepting_states:
            dot.node(state, state, shape="doublecircle", color="blue")
        else:
            dot.node(state, state, shape="circle")

    for (state, symbol), next_state in transitions.items():
        dot.edge(state, next_state, label=symbol)

    dot.render("./Primera_parte/grafos/grafo_AFD", view=True)


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
    print_afd(states, transitions, accepting_states)
    visualize_afd(states, transitions, accepting_states)

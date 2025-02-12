# Andre Marroquin 22266
# Rodrigo Mansilla
# Sergio Orellana 22122
import itertools

precedence = {"|": 1, ".": 2, "*": 3}


def is_operator(c: str) -> bool:
    return c in precedence


def is_operand(c: str) -> bool:
    return c.isalnum() or c == "_" or c == "#"


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


class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()
        self.position = None


def build_syntax_tree(postfix):
    stack = []
    pos_counter = itertools.count(1)
    position_symbol_map = {}

    for char in postfix:
        if char.isalnum() or char == "#":
            node = Node(char)
            node.position = next(pos_counter)
            node.firstpos.add(node.position)
            node.lastpos.add(node.position)
            position_symbol_map[node.position] = char  # Mapeamos la posición al símbolo
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


def construct_afd(root, position_symbol_map):
    followpos = {pos: set() for pos in position_symbol_map}
    compute_followpos(root, followpos)

    states = {}
    state_queue = [frozenset(root.firstpos)]
    transitions = {}
    state_names = {}
    current_name = itertools.count(ord("A"))

    while state_queue:
        state = state_queue.pop(0)
        if state not in state_names:
            state_names[state] = chr(next(current_name))
            states[state_names[state]] = state

        symbol_map = {}
        for pos in state:
            symbol = position_symbol_map.get(
                pos
            )  # Obtener el símbolo asociado a la posición
            if symbol:
                if symbol not in symbol_map:
                    symbol_map[symbol] = set()
                symbol_map[symbol] |= followpos.get(pos, set())

        for symbol, next_state in symbol_map.items():
            if symbol == "#":
                continue
            next_state = frozenset(next_state)
            if next_state and next_state not in state_names:
                state_queue.append(next_state)
                state_names[next_state] = chr(next(current_name))
            transitions[(state_names[state], symbol)] = state_names.get(next_state, "?")

    return states, transitions


def print_afd(states, transitions):
    print("Estados:", states)
    print("Transiciones:")
    for (state, symbol), next_state in transitions.items():
        print(f"{state} -- {symbol} --> {next_state}")


if __name__ == "__main__":
    regex = input(
        "Ingresa la regexp que deseas convertir a AFD (| - or, * - Cerradura de Kleene): "
    )
    regex += "#"
    postfix = toPostFix(regex)
    # print(postfix)
    syntax_tree, position_symbol_map = build_syntax_tree(postfix)
    states, transitions = construct_afd(syntax_tree, position_symbol_map)
    print_afd(states, transitions)

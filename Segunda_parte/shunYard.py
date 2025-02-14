# Prioridades de los operadores (más alto número, mayor prioridad)
precedence = {'+': 1, '.': 2, '*': 3}

# Función para verificar si un carácter es un operador
def is_operator(c: str) -> bool:
    # Devuelve True si el carácter es uno de los operadores +, ., o *
    return c in precedence

# Función para verificar si un carácter es un operando
def is_operand(c: str) -> bool:
    # Un operando es cualquier carácter alfanumérico o el guion bajo '_', 
    # que en este caso representa el símbolo epsilon (vacío)
    return c.isalnum() or c == '_'

# Función para insertar puntos de concatenación '.' en la expresión infix
def insert_concatenation_operators(infix: str) -> str:
    result = []  # Lista donde se almacenará la nueva expresión con los puntos
    length = len(infix)  # Longitud de la expresión infix
    
    # Iteramos sobre cada carácter de la expresión
    for i in range(length):
        result.append(infix[i])  # Añadimos el carácter actual a la lista resultado
        
        # Si no estamos en el último carácter, comprobamos si necesitamos insertar un '.'
        if i < length - 1:
            # Insertar un '.' si:
            # 1. El carácter actual es un operando y el siguiente es un operando o un paréntesis abierto
            # 2. El carácter actual es un paréntesis cerrado y el siguiente es un operando o un paréntesis abierto
            # 3. El carácter actual es '*' y el siguiente es un operando o un paréntesis abierto
            if (is_operand(infix[i]) and (is_operand(infix[i+1]) or infix[i+1] == '(')) or \
               (infix[i] == ')' and (is_operand(infix[i+1]) or infix[i+1] == '(')) or \
               (infix[i] == '*' and (is_operand(infix[i+1]) or infix[i+1] == '(')):
                result.append('.')  # Insertar el punto de concatenación

    # Devolver la expresión con los puntos de concatenación como cadena
    return ''.join(result)

# Función principal para convertir una expresión infix a postfix
def toPostFix(infixExpression: str) -> str:
    # Primero, inserta los puntos de concatenación explícitos
    infixExpression = insert_concatenation_operators(infixExpression)

    output = []  # Lista para almacenar el resultado en notación postfix
    operators = []  # Pila para almacenar los operadores

    i = 0
    # Recorremos la expresión infix carácter por carácter
    while i < len(infixExpression):
        c = infixExpression[i]

        if is_operand(c):  # Si es un operando, lo añadimos directamente al resultado
            output.append(c)
        elif c == '(':  # Si es un paréntesis abierto, lo apilamos
            operators.append(c)
        elif c == ')':  # Si es un paréntesis cerrado, desapilamos hasta encontrar un paréntesis abierto
            while operators and operators[-1] != '(':
                output.append(operators.pop())  # Añadimos operadores a la salida
            operators.pop()  # Eliminamos el paréntesis abierto de la pila
        elif is_operator(c):  # Si es un operador
            # Desapilamos operadores de mayor o igual precedencia y los añadimos a la salida
            while (operators and operators[-1] != '(' and
                   precedence[operators[-1]] >= precedence[c]):
                output.append(operators.pop())
            # Finalmente, apilamos el operador actual
            operators.append(c)
        i += 1

    # Desapilar cualquier operador restante en la pila
    while operators:
        output.append(operators.pop())
    
    # Devolver la expresión en notación postfix
    return ''.join(output)

# Ejemplo de uso
if __name__ == "__main__":
    infix = "(0+1)*11(0+1)*"
    postfix = toPostFix(infix)
    print(f"Infijo: {infix}")  # Imprime la expresión en notación infix
    print(f"Postfijo: {postfix}")  # Imprime la expresión en notación postfix

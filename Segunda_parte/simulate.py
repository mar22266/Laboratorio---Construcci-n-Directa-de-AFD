import os
import time
import json
from shunYard import toPostFix
from regexpToAFN import toAFN
from AFNToAFD import fromAFNToAFD
from minimizeAFD import minimize_afd
import graphviz
from colorama import Fore, Style, init

init(autoreset=True)  # Para que los colores se reinicien automáticamente


def sanitize_folder_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)


def generate_graph(automaton, name, folder):
    dot = graphviz.Digraph(comment=name)

    if isinstance(automaton["transitions"], list):  # Para AFN (lista de transiciones)
        for state_idx, transitions in enumerate(automaton["transitions"]):
            state_label = str(state_idx)
            for input_char, next_states in transitions.items():
                for next_state in next_states:
                    next_state_label = str(next_state)
                    dot.edge(state_label, next_state_label, label=input_char)
    else:  # Para AFD o AFD minimizado (diccionario de transiciones)
        for state, transitions in automaton["transitions"].items():
            state_label = ",".join(map(str, state))
            for input_char, next_state in transitions.items():
                next_state_label = ",".join(map(str, next_state))
                dot.edge(state_label, next_state_label, label=input_char)

    accepted_states = (
        automaton["accepted"]
        if isinstance(automaton["accepted"], (list, set))
        else [automaton["accepted"]]
    )

    for accepted_state in accepted_states:
        accepted_label = (
            ",".join(map(str, accepted_state))
            if isinstance(accepted_state, frozenset)
            else str(accepted_state)
        )
        dot.node(accepted_label, shape="doublecircle")

    output_path = os.path.join(folder, f"{name}.gv")
    dot.render(output_path, format="png")
    print(f"{Fore.GREEN}Generated {name} graph at {output_path}.png")


def write_automaton_to_json(automaton, filename):
    if isinstance(automaton["transitions"], list):
        estados = list(range(len(automaton["transitions"])))
        transiciones = set()
        simbolos = set()

        for state_idx, transitions in enumerate(automaton["transitions"]):
            for simbolo, next_states in transitions.items():
                simbolos.add(simbolo)
                for next_state in next_states:
                    transiciones.add((state_idx, simbolo, next_state))

        automaton_data = {
            "ESTADOS": estados,
            "SIMBOLOS": list(simbolos),
            "INICIO": [estados[0]],
            "ACEPTACION": [automaton["accepted"]],
            "TRANSICIONES": [
                (origen, simbolo, destino)
                for (origen, simbolo, destino) in transiciones
            ],
        }

    else:
        estados = list(automaton["transitions"].keys())
        transiciones = set()
        simbolos = set()

        for origen, transitions in automaton["transitions"].items():
            for simbolo, destino in transitions.items():
                simbolos.add(simbolo)
                transiciones.add((tuple(origen), simbolo, tuple(destino)))

        automaton_data = {
            "ESTADOS": [list(state) for state in estados],
            "SIMBOLOS": list(simbolos),
            "INICIO": [list(next(iter(estados)))],
            "ACEPTACION": [list(state) for state in automaton["accepted"]],
            "TRANSICIONES": [
                (list(origen), simbolo, list(destino))
                for (origen, simbolo, destino) in transiciones
            ],
        }

    with open(filename, "w") as file:
        json.dump(automaton_data, file, indent=4)

    print(f"{Fore.YELLOW}Automaton written to {filename}")


def simulate_regexp_process(infix_expression, test_string):
    # Sanitizar nombre de la carpeta usando la expresión regular
    sanitized_infix = sanitize_folder_name(infix_expression)
    folder = f"./Segunda_parte/automaton_graphs/{sanitized_infix}"

    # Crear la carpeta específica para esta expresión si no existe
    os.makedirs(folder, exist_ok=True)

    # Paso 1: Convertir infix a postfix
    postfix = toPostFix(infix_expression)
    print(f"Postfix: {postfix}")

    # Paso 2: Convertir postfix a AFN
    afn = toAFN(postfix)
    print(f"AFN: {afn}")
    generate_graph(afn, "AFN", folder)
    write_automaton_to_json(afn, os.path.join(folder, "afn.json"))

    # Paso 3: Convertir AFN a AFD
    afd = fromAFNToAFD(afn)
    print(f"AFD Transitions:")
    for state, transitions in afd["transitions"].items():
        print(f"State: {state} -> Transitions: {transitions}")
    print(f"AFD Accepted States: {afd['accepted']}")
    generate_graph(afd, "AFD", folder)
    write_automaton_to_json(afd, os.path.join(folder, "afd.json"))

    # Paso 4: Minimizar AFD
    minimized_afd = minimize_afd(afd)
    print(f"Minimized AFD Transitions:")
    for state, transitions in minimized_afd["transitions"].items():
        print(f"State: {state} -> Transitions: {transitions}")
    print(f"Minimized AFD Accepted States: {minimized_afd['accepted']}")
    generate_graph(minimized_afd, "Minimized_AFD", folder)
    write_automaton_to_json(minimized_afd, os.path.join(folder, "minimized_afd.json"))

    # Paso 5: Simular la cadena de entrada
    current_state = next(iter(minimized_afd["transitions"].keys()))  # Estado inicial
    print(f"Initial state: {current_state}")

    if not test_string:
        # Aquí se cambia la lógica para no aceptar la cadena vacía por defecto.
        print(f"String is empty, checking if the initial state is an accepting state.")
        if current_state in minimized_afd["accepted"]:
            print(
                f"String '{test_string}' is accepted because the initial state is an accepting state."
            )
        else:
            print(
                f"String '{test_string}' is not accepted because the initial state is not an accepting state."
            )
        return

    start_time = time.time()  # Comienza a medir el tiempo

    for char in test_string:
        print(f"Processing character: {char}")
        if char in minimized_afd["transitions"][current_state]:
            next_state = minimized_afd["transitions"][current_state][char]
            print(f"Transition from {current_state} to {next_state} on '{char}'")
            current_state = next_state
        else:
            print(f"No transition from {current_state} on '{char}'")
            print(f"String '{test_string}' is not accepted.")
            end_time = time.time()  # Finaliza el tiempo de verificación
            elapsed_time = end_time - start_time
            print(f"Verification time: {elapsed_time} seconds")
            return False

    # Verificar si el estado final es un estado aceptado
    if current_state in minimized_afd["accepted"]:
        print(f"String '{test_string}' is accepted.")
    else:
        print(f"Final state: {current_state} is not an accepted state.")
        print(f"String '{test_string}' is not accepted.")

    end_time = time.time()  # Finaliza el tiempo de verificación
    elapsed_time = end_time - start_time
    print(f"Verification time: {elapsed_time} seconds")


if __name__ == "__main__":
    infix_expr = input("Ingrese la expresión regular en infix: ")
    test_str = input("Ingrese la cadena a probar: ")

    simulate_regexp_process(infix_expr, test_str)

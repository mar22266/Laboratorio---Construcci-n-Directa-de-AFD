import string


def minimize_afd(afd):
    accepted_states = set(afd["accepted"])
    non_accepted_states = set(afd["transitions"].keys()) - accepted_states

    grouped = {}

    for state, transitions in afd["transitions"].items():
        is_accepted = state in accepted_states
        key = (frozenset(transitions.items()), is_accepted)
        grouped.setdefault(key, []).append(state)

    minimized_transitions = {}
    minimized_accepted = set()
    state_mapping = {}

    # Asignar nombres de letra a los grupos
    for i, group in enumerate(grouped.values()):
        letter = string.ascii_uppercase[i]  # A, B, C, ...
        state_mapping[frozenset(group)] = letter
        minimized_transitions[letter] = {}
        if any(state in accepted_states for state in group):
            minimized_accepted.add(letter)

    # Reasignar transiciones con los nuevos nombres
    for group, letter in state_mapping.items():
        sample_state = next(
            iter(group)
        )  # Tomar un estado de muestra para las transiciones
        for input_char, next_state in afd["transitions"][sample_state].items():
            for next_group, next_letter in state_mapping.items():
                if next_state in next_group:
                    minimized_transitions[letter][input_char] = next_letter
                    break

    return {"transitions": minimized_transitions, "accepted": list(minimized_accepted)}

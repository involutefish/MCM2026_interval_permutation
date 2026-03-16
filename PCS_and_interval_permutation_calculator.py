# helper: parse input pcs string or iterable, support note names and '-' or ',' as separators
# Helper function: parse input pitch class set (string or iterable), supports note names and uses '-' or ',' as separators

import warnings

warnings.filterwarnings('ignore')


def parse_pcs(pcs):
    """
    Parses input pitch class set (string or iterable), supporting note names and integers.
    Separators can be ',' or '-'.
    Returns: A built-in set of integers in the range 0-11.
    """
    import builtins  # Use built-in types to avoid shadowing by external variables

    note_map = {
        "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4,
        "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8,
        "A": 9, "A#": 10, "BB": 10, "B": 11
    }

    # If input is an iterable collection of values (list / set / tuple), process elements directly
    if isinstance(pcs, (list, builtins.set, tuple)):
        result = builtins.set()
        for x in pcs:
            if isinstance(x, int):
                result.add(x % 12)
            elif isinstance(x, str) and x.strip().isdigit():
                result.add(int(x.strip()) % 12)
            else:
                token = str(x).strip().upper().replace('♯', '#').replace('♭', 'B')
                if token in note_map:
                    result.add(note_map[token])
        return result

    # Otherwise, process as a string (allowing '-' or ',' as separators)
    text = str(pcs)
    text = text.replace('-', ',')  # Unify separators to commas
    tokens = [t.strip() for t in text.split(',') if t.strip() != '']

    result = builtins.set()
    for t in tokens:
        tok = t.upper().replace('♯', '#').replace('♭', 'B')  # Standardize accidentals (handle unicode)
        # Match note names first
        if tok in note_map:
            result.add(note_map[tok])
            continue
        # Then parse as pure integers
        if tok.lstrip('-').isdigit():
            try:
                result.add(int(tok) % 12)
                continue
            except ValueError:
                pass
        # Ignore unrecognized tokens (maintaining original code style)
    return result


# calculate all rotated sets
def generate_rotations(pcs):
    """Generate all cyclic rotations of the set"""
    pcs = parse_pcs(pcs)
    pcs_sorted = sorted(pcs)  # Sort the set ascending
    return [pcs_sorted[i:] + pcs_sorted[:i] for i in range(len(pcs_sorted))]


# calculate inversional sets
def inversion(pcs):
    """Calculate the inversion of the set"""
    pcs = parse_pcs(pcs)
    pcs_sorted = sorted(pcs)  # Sort ascending
    inversion_pcs = []
    for i in pcs:
        pitch_class = (12 - i) % 12
        inversion_pcs.append(pitch_class)
    inversion_pcs = sorted(inversion_pcs)
    return inversion_pcs


# calculate compacted sets
def compacted_sets(pcs):
    """Calculate the most compact (narrowest span) sets"""
    rotations = generate_rotations(pcs)  # Generate all rotated sets
    interval_set = []
    # Calculate the span (width) of each rotation
    for ps in rotations:
        interval = (ps[-1] - ps[0]) % 12
        interval_set.append(interval)
    # Find the minimal width and its corresponding indices
    min_value = min(interval_set)  # Get minimal span
    min_indices = [index for index, value in enumerate(interval_set) if
                   value == min_value]  # Get indices of minimal width
    # Extract compacted sets
    compacted_sets_list = []
    for i in min_indices:
        compacted_sets_list.append(rotations[i])
    return compacted_sets_list


# normal form
def forte_normal_form(pcs):
    """Compute the Forte Normal Form"""
    set_list = compacted_sets(pcs)  # Get the narrowest sets
    if len(set_list) == 1:
        return set_list[0]  # If only one narrowest set exists, return it

    def recursive_selection(sets, index):
        # If only one set remains or index exceeds set length, choose the one with the smallest packed intervals
        if len(sets) == 1 or index >= len(sets[0]):
            return min(sets)  # If multiple candidates remain, choose the leftmost minimal

        # Compute interval differences from the first note
        interval_diffs = []
        for ps in sets:
            interval = (ps[index] - ps[0]) % 12  # Compute interval of the n-th note relative to the 1st note mod 12
            interval_diffs.append(interval)

        min_value = min(interval_diffs)  # Get minimal interval
        min_indices = [i for i, value in enumerate(interval_diffs) if
                       value == min_value]  # Get indices of minimal intervals
        filtered_sets = [sets[i] for i in min_indices]  # Filter sets that match the minimal interval
        return recursive_selection(filtered_sets, index + 1)

    final_normal_form = recursive_selection(set_list, 1)  # Compute the final normal form
    return final_normal_form


# calculate prime form
def forte_prime_form(pcs):
    """Compute the Forte Prime Form"""
    pcs_normal_form = forte_normal_form(pcs)  # Normal form of the original set
    inversion_pcs = inversion(pcs)  # Inversion of the set
    inversion_pcs_normal_form = forte_normal_form(",".join(map(str, inversion_pcs)))  # Pass as string after conversion

    candidate_sets = [pcs_normal_form,
                      inversion_pcs_normal_form]  # Create candidate list (Original NF and Inversion NF)

    def recursive_selection(sets, index):
        """Recursive selection for the best Normal Form candidate to determine Prime Form"""
        if len(sets) == 1 or index >= len(sets[0]):
            return min(sets)  # Choose the leftmost minimal

        interval_diffs = [(ps[index] - ps[0]) % 12 for ps in sets]  # Compute intervals relative to the first note
        min_value = min(interval_diffs)  # Get minimal interval
        min_indices = [i for i, value in enumerate(interval_diffs) if value == min_value]  # Get indices
        filtered_sets = [sets[i] for i in min_indices]  # Filter candidates

        return recursive_selection(filtered_sets, index + 1)  # Recurse to next index

    forte_prime_form_temp = recursive_selection(candidate_sets, 1)  # Compute temporary result
    a = (forte_prime_form_temp[0] - 0) % 12
    final_prime_form = [(i - a) % 12 for i in forte_prime_form_temp]  # Transpose so the first element is 0
    return final_prime_form


# calculate subsets
def subsets(pcs):
    """Compute all possible subsets of a set, ensuring elements are integers"""
    pcs = parse_pcs(pcs)  # Convert to integer set
    pcs_sorted = sorted(pcs)  # Sort ascending
    n = len(pcs_sorted)
    all_subsets = []
    for i in range(2 ** n):  # 2^n iterations to enumerate the power set
        subset = []
        for j in range(n):  # Iterate through each element
            if (i >> j) & 1:  # Check if the j-th bit of i is 1
                subset.append(pcs_sorted[j])  # Append based on index
        all_subsets.append(subset)
    return all_subsets


# 12 transpositions
def all_transpositions(pcs):
    """Generate all 12 transpositions (Tn) of the set"""
    pcs = parse_pcs(pcs)
    pcs_sorted = sorted(pcs)  # Sort ascending
    transposition_sets = []
    for i in range(0, 12):
        T_i = []
        for j in pcs:
            j = (j + i) % 12
            T_i.append(j)
        transposition_sets.append(T_i)
    return transposition_sets


def all_transpositions_with_prime_form_as_reference_frame(pcs):
    """Calculate 12 transpositions relative to the Set Class (Prime Form)"""
    pcs = forte_prime_form(pcs)  # Use prime form as base
    transposition_sets_ref = []
    for i in range(0, 12):
        T_i = []
        for j in pcs:
            j = (j + i) % 12
            T_i.append(j)
        transposition_sets_ref.append(T_i)
    return transposition_sets_ref


# 12 inversions
def all_inversions(pcs):
    """Generate all 12 inversions (TnI) of the set"""
    pcs = inversion(pcs)
    inversion_sets = []
    for i in range(0, 12):
        I_i = []
        for j in pcs:
            j = (j + i) % 12
            I_i.append(j)
        inversion_sets.append(I_i)
    return inversion_sets


def all_inversions_with_prime_form_as_reference_frame(pcs):
    """Generate 12 inversions using the Prime Form as the reference frame"""
    pcs = forte_prime_form(pcs)
    pcs = inversion(pcs)
    inversion_sets_ref = []
    for i in range(0, 12):
        I_i = []
        for j in pcs:
            j = (j + i) % 12
            I_i.append(j)
        inversion_sets_ref.append(I_i)
    return inversion_sets_ref


def Dihedral_12_order(pcs):
    """Elements of the Dihedral group D12 (24 operations: 12 Transpositions + 12 Inversions)"""
    Dihedral_12 = all_transpositions(pcs) + all_inversions(pcs)
    return Dihedral_12


def subset_class(pcs):
    """Compute subset classes (unique Prime Forms) found within the set"""
    all_subsets_list = subsets(pcs)  # Generate all subsets
    unique_prime_forms = []  # Use list to avoid shadowing 'set' keyword

    for i in all_subsets_list:
        if len(i) < 3:  # Filter out empty set and sets with fewer than 3 elements (dyads/monads)
            continue
        prime_form = forte_prime_form(",".join(map(str, i)))  # Calculate prime form
        if prime_form not in unique_prime_forms:  # Avoid duplicates
            unique_prime_forms.append(prime_form)

    return unique_prime_forms  # Return list of subset prime forms


def complementary_set(pcs):
    """Compute the complement of set 'pcs' relative to the universal set [0,1,...,11]"""
    universal_set = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}  # Explicit set to avoid shadowing
    pcs_data = parse_pcs(pcs)  # Convert to integer set
    complement = sorted(universal_set - pcs_data)  # Calculate difference and sort
    return complement  # Return the sorted complement


def complement_set_class(pcs):
    """Compute the Prime Form of the complementary set"""
    complement = complementary_set(pcs)
    # Convert list to string format for forte_prime_form() input
    complement_str = ",".join(map(str, complement))
    # Calculate the Forte Prime Form of the complement
    comp_prime_form = forte_prime_form(complement_str)
    return comp_prime_form


def find_tetrachord_genres(set1, set2):
    """
    Computes 24 variants of two trichords, merges them to find tetrachords,
    calculates their Forte Prime Forms, and analyzes their complements and subsets.
    """
    print("Prime Form of Set 1:", forte_prime_form(set1))
    print("Prime Form of Set 2:", forte_prime_form(set2))

    set1_variants = all_transpositions(set1) + all_inversions(set1)
    set2_variants = all_transpositions(set2) + all_inversions(set2)

    merged_sets = []
    four_note_sets = set()

    for variant1 in set1_variants:
        for variant2 in set2_variants:
            merged_set = sorted(set(variant1) | set(variant2))
            merged_sets.append(merged_set)

            if len(merged_set) == 4:
                forte_form = tuple(forte_prime_form(",".join(map(str, merged_set))))
                four_note_sets.add(forte_form)

    print("Prime Forms of tetrachords containing both trichords:", [list(s) for s in four_note_sets])

    four_note_complements = []
    valid_complements = []
    valid_complement_classes = []

    set1_prime = forte_prime_form(set1)
    set2_prime = forte_prime_form(set2)

    for s in four_note_sets:
        complement = complementary_set(",".join(map(str, s)))
        if complement:
            four_note_complements.append(complement)

            complement_subsets = subset_class(",".join(map(str, complement)))

            for subset in complement_subsets:
                if set1_prime in subset_class(",".join(map(str, subset))) and set2_prime in subset_class(
                        ",".join(map(str, subset))):
                    valid_complements.append(complement)
                    complement_class = forte_prime_form(",".join(map(str, complement)))
                    valid_complement_classes.append(complement_class)
                    break

    print("Complements of all tetrachords:", four_note_complements)
    print("Filtered tetrachord complements:", valid_complements)
    print("Prime Forms of valid complements:", valid_complement_classes)

    return ([list(s) for s in four_note_sets], four_note_complements, valid_complements, valid_complement_classes)


def interval_vector(pcs):
    """
    Calculates the Interval Vector of a Pitch Class Set.
    Returns: A list of 6 integers representing occurrences of intervals 1-6 (Interval Classes).
    """
    pcs_data = parse_pcs(pcs)  # Process input using existing parser
    pcs_list = sorted(pcs_data)  # Convert to sorted list for calculation
    n = len(pcs_list)

    # Initialize counters for intervals 1-6
    counts = [0] * 6

    # Calculate all pairwise intervals
    for i in range(n):
        for j in range(i + 1, n):
            # Calculate interval mod 12
            diff = abs(pcs_list[i] - pcs_list[j]) % 12
            # Map to Interval Class (1-6)
            if diff > 6:
                diff = 12 - diff
            # Increment counter (index diff-1)
            counts[diff - 1] += 1
    return counts


def find_one_more_pitch_pcs(pcs):
    """
    Extends the input set by adding one pitch class, calculates the resulting Forte Prime Form,
    and checks if the original set class is contained within the complement's subset classes.
    """
    pcs_set = parse_pcs(pcs)  # Convert to integer set
    existing_prime_form = forte_prime_form(pcs)  # Forte Prime Form of original set

    print(f"Original Set: {sorted(pcs_set)}")
    print(f"Original Forte Prime Form: {existing_prime_form}\n")

    final_results = []  # Store matching extended sets and their complements

    # Iterate through 0-11, try adding a new pitch class
    for new_pitch in range(12):
        if new_pitch not in pcs_set:  # Pitch must not already exist in set
            new_set = sorted(pcs_set | {new_pitch})  # Generate new set

            # Compute Prime Form of the new set
            prime_form = forte_prime_form(",".join(map(str, new_set)))

            # Compute Prime Form of the complement
            complement = complementary_set(",".join(map(str, new_set)))
            complement_prime = forte_prime_form(",".join(map(str, complement)))

            # Compute subset classes of the complement
            complement_subsets = subset_class(",".join(map(str, complement)))

            # **Check if the complement's subset classes contain the original set's Prime Form**
            if existing_prime_form in complement_subsets:
                final_results.append((new_set, complement))  # Store results

    # **Final Output**
    print("\n[Qualified Extended Sets & Their Complements]")
    for new_set, complement in final_results:
        print(f"Extended Set: {new_set}  -> Complement: {complement}")

    return final_results  # Return results


def parse_pcs_ordered(pcs):
    """
    Parses pitch class set in the input order, returning an ordered list.
    (Used to prevent set operations from scrambling the original sequence)
    """
    note_map = {
        "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4,
        "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8,
        "A": 9, "A#": 10, "BB": 10, "B": 11
    }

    # Handle iterable objects
    if isinstance(pcs, (list, tuple)):
        ordered = []
        for x in pcs:
            if isinstance(x, int):
                ordered.append(x % 12)
            elif isinstance(x, str):
                token = x.strip().upper().replace('♯', '#').replace('♭', 'B')
                if token in note_map:
                    ordered.append(note_map[token])
                elif token.lstrip('-').isdigit():
                    ordered.append(int(token) % 12)
        return ordered

    # Handle string inputs (split by separators, maintain order)
    text = str(pcs).replace('-', ',')
    tokens = [t.strip() for t in text.split(',') if t.strip()]

    ordered = []
    for t in tokens:
        tok = t.upper().replace('♯', '#').replace('♭', 'B')
        if tok in note_map:
            ordered.append(note_map[tok])
        elif tok.lstrip('-').isdigit():
            ordered.append(int(tok) % 12)
    return ordered


# Corrected interval series function using ordered parsing
def generate_interval_series(pcs):
    """Generates an interval series based on input order (maintaining stability)"""
    ordered_pcs = parse_pcs_ordered(pcs)

    # Calculate adjacent intervals (Next note - Current note, mod 12)
    interval_series = []
    for i in range(1, len(ordered_pcs)):
        interval = (ordered_pcs[i] - ordered_pcs[i - 1]) % 12
        interval_series.append(interval)
    return interval_series


# Symmetric Group actions
def generate_symmetrical_group_actions(pcs):
    """Returns all unique permutations of the interval series"""
    intervals = generate_interval_series(pcs)

    # Recursive permutation generator
    def _permute(elems):
        if len(elems) <= 1:
            return [elems.copy()]
        result = []
        seen = set()
        for i in range(len(elems)):
            current = elems[i]
            if current in seen:
                continue
            seen.add(current)
            remaining = elems[:i] + elems[i + 1:]
            for perm in _permute(remaining):
                result.append([current] + perm)
        return result

    return _permute(intervals)


def generate_pcs_through_permutations(pcs):
    """Generates melodic fragments based on permutations of the interval series"""
    ordered_pcs = parse_pcs_ordered(pcs)
    if not ordered_pcs:  # Handle empty input
        return []
    first_note = ordered_pcs[0]
    interval_permutations = generate_symmetrical_group_actions(pcs)
    pcs_collection = []
    for perm in interval_permutations:
        current = first_note  # Restart for each permutation
        new_pcs = [current]  # The first element is fixed to the original first note
        for interval in perm:
            current = (current + interval) % 12  # Accumulate based on interval
            new_pcs.append(current)
        pcs_collection.append(new_pcs)
    return pcs_collection


def generate_sc_through_permutations(pcs):
    """Generates unique Set Classes (Prime Forms) derived from interval permutations"""
    set_collections = generate_pcs_through_permutations(pcs)
    prime_forms = []
    seen_primes = set()
    for pcs_set in set_collections:
        prime = forte_prime_form(pcs_set)
        # Convert list to tuple to check for membership in 'seen_primes'
        prime_tuple = tuple(prime)
        if prime_tuple not in seen_primes:
            seen_primes.add(prime_tuple)
            prime_forms.append(prime)
    return prime_forms


warnings.filterwarnings('ignore')

# Main execution block
pcs_input = input("Please input pitch class set: ")
print("Generated Interval Series:", generate_interval_series(pcs_input))
print(f"Data Type of Interval Series: {type(generate_interval_series(pcs_input))}")
print("Interval Vector:", interval_vector(pcs_input))
print("Forte Prime Form:", forte_prime_form(pcs_input))
print("Forte Normal Form:", forte_normal_form(pcs_input))
print("Symmetric Group actions on melodic fragment:", generate_symmetrical_group_actions(pcs_input))
print("Melodic fragments generated through permutations:", generate_pcs_through_permutations(pcs_input))
print("Set classes associated through permutations:", generate_sc_through_permutations(pcs_input))
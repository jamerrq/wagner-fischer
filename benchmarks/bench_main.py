# SHOW_RESULTS = False

def load_dictionary(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def wagner_fischer(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    current_row = range(len_s1 + 1)
    for i in range(1, len_s2 + 1):
        previous_row, current_row = current_row, [i] + [0] * len_s1
        for j in range(1, len_s1 + 1):
            add, delete, change = previous_row[j] + \
                1, current_row[j-1] + 1, previous_row[j-1]
            if s1[j-1] != s2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[len_s1]

def spell_check(word, dictionary, method=wagner_fischer):
    suggestions = []

    for correct_word in dictionary:
        distance = method(word, correct_word)
        suggestions.append((correct_word, distance))

    suggestions.sort(key=lambda x: x[1])
    results = suggestions[:10]
    # if SHOW_RESULTS:
    #     print("Results:", results)
    return results

dictionary = load_dictionary("words.txt")

misspelled_word = "wrlod"

def bench_no_cache():
    spell_check(misspelled_word, dictionary)

def bench_with_cache():
    spell_check(misspelled_word, dictionary, wagner_fischer_dict)

def bench_with_branch_pruning():
    spell_check(misspelled_word, dictionary, wagner_fischer_branch)

def bench_with_cache_and_branch_pruning():
    spell_check(misspelled_word, dictionary, wagner_fischer_branch_cache)

"""
IMPROVEMENTS:
"""

# 1. Use a dictionary to store the words and their distances,
# so in case the same word is checked multiple times, the distance
# is not calculated again.

cache = {}

def wagner_fischer_dict(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    # Check if the distance is already calculated
    if (s1, s2) in cache:
        return cache[(s1, s2)]

    current_row = range(len_s1 + 1)
    for i in range(1, len_s2 + 1):
        previous_row, current_row = current_row, [i] + [0] * len_s1
        for j in range(1, len_s1 + 1):
            add, delete, change = previous_row[j] + \
                1, current_row[j-1] + 1, previous_row[j-1]
            if s1[j-1] != s2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)

    # Store the distance in the cache
    cache[(s1, s2)] = current_row[len_s1]
    return current_row[len_s1]

# 2. Use branch pruning to avoid unnecessary calculations
# DISCLAIMER: This idea is not mine, it was taken from the
# article "Can We Optimize the Wagner-Fischer Algorithm?"
# by Fujimoto Seiji
# https://ceptord.net/wagner-fischer/index.html

def wagner_fischer_branch(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    if len_s2 == 0:
        return len_s1
    if len_s2 == 1:
        return len_s1 - (s2[0] in s1)
    if len_s2 == 2:
        p1 = s1.find(s2[0])
        if p1 != -1:
            return len_s1 - (s2[1] in s1[p1+1:]) - 1
        else:
            return len_s1 - (s2[1] in s1[1:])

    buf = [i for i in range(len_s2 + 1)]

    Mx = (len_s2 - 1) // 2
    mx = 1 - Mx - (len_s1 - len_s2)

    for j in range(Mx + 1):
        buf[j] = j

    for i in range(1, len_s1 + 1):
        buf[0] = i - 1
        m = max(mx, 1)
        M = min(Mx, len_s2)
        mx += 1
        Mx += 1
        dia = buf[m - 1]
        top = buf[m]
        if s1[i - 1] != s2[m - 1]:
            dia = min(dia, top) + 1
        buf[m] = dia
        left = dia
        dia = top
        for j in range(m + 1, M + 1):
            top = buf[j]
            if s1[i - 1] != s2[j - 1]:
                dia = min(min(dia, top), left) + 1
            buf[j] = dia
            left = dia
            dia = top
        if len_s2 == M:
            continue
        if s1[i - 1] != s2[M]:
            dia = min(dia, left) + 1
        buf[M + 1] = dia
    dia = buf[len_s2]
    return dia

# 3. Use the cache and branch pruning together

cache_for_branch = {}

def wagner_fischer_branch_cache(s1, s2):
    if (s1, s2) in cache_for_branch:
        return cache_for_branch[(s1, s2)]

    len_s1, len_s2 = len(s1), len(s2)
    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    if len_s2 == 0:
        return len_s1
    if len_s2 == 1:
        return len_s1 - (s2[0] in s1)
    if len_s2 == 2:
        p1 = s1.find(s2[0])
        if p1 != -1:
            return len_s1 - (s2[1] in s1[p1+1:]) - 1
        else:
            return len_s1 - (s2[1] in s1[1:])

    buf = [i for i in range(len_s2 + 1)]

    Mx = (len_s2 - 1) // 2
    mx = 1 - Mx - (len_s1 - len_s2)

    for j in range(Mx + 1):
        buf[j] = j

    for i in range(1, len_s1 + 1):
        buf[0] = i - 1
        m = max(mx, 1)
        M = min(Mx, len_s2)
        mx += 1
        Mx += 1
        dia = buf[m - 1]
        top = buf[m]
        if s1[i - 1] != s2[m - 1]:
            dia = min(dia, top) + 1
        buf[m] = dia
        left = dia
        dia = top
        for j in range(m + 1, M + 1):
            top = buf[j]
            if s1[i - 1] != s2[j - 1]:
                dia = min(min(dia, top), left) + 1
            buf[j] = dia
            left = dia
            dia = top
        if len_s2 == M:
            continue
        if s1[i - 1] != s2[M]:
            dia = min(dia, left) + 1
        buf[M + 1] = dia
    dia = buf[len_s2]
    cache_for_branch[(s1, s2)] = dia
    return dia

__benchmarks__ = [
    # (bench_no_cache, bench_with_cache, "using cache"),
    (bench_no_cache, bench_with_branch_pruning, "using branch pruning"),
    # (bench_no_cache, bench_with_cache_and_branch_pruning, "using both"),
    # (bench_with_branch_pruning, bench_with_cache_and_branch_pruning, "branch pruning cache comparison"),
]

# if SHOW_RESULTS:
#     print("Results for 'wrlod':\n")
#     print("No cache results:")
#     bench_no_cache()
#     print("\nWith cache results:")
#     bench_with_cache()
#     print("\nWith branch pruning results:")
#     bench_with_branch_pruning()


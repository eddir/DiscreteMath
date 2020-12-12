from pprint import pprint


def union(variety1, variety2):
    variety3 = []

    for item in variety1 + variety2:
        if item not in variety3:
            variety3.append(item)

    return variety3


def intersection(variety1, variety2):
    variety3 = []

    for item1 in variety1:
        for item2 in variety2:
            if item1 == item2 and item2 not in variety3:
                variety3.append(item1)

    return variety3


def difference(variety1, variety2):
    return [item for item in variety1 if item not in intersection(variety1, variety2)]


def symmetric_difference(variety1, variety2):
    return [item for item in variety1 + variety2 if item not in intersection(variety1, variety2)]


def addition(variety1, variety2):
    return difference(variety2, variety1)


def cartesian_product(variety1, variety2):
    variety3 = []

    for item1 in variety1:
        for item2 in variety2:
            variety3.append([item1, item2])

    return variety3


def properties(varieties):
    description = {
        "reflexivity": True,
        "anti_reflexivity": True,

        "symmetry": True,
        "anti_symmetry": True,

        "coreflexivity": True,
        "asymmetry": True,

        "transitivity": True,
        "euclidean": True,

        "linearity": True,
        "coherence": True,

        "trichotomy": True,
        "tolerance": False,

        "private": False,
        "full": False,

        "equivalence": False,
    }
    multiplicity = varieties[0]
    relationships = varieties[1:]

    for a in multiplicity:
        if not [a, a] in relationships:
            description["reflexivity"] = False
            break

    for a in multiplicity:
        if [a, a] in relationships:
            description["anti_reflexivity"] = False
            break

    for a in multiplicity:
        for b in multiplicity:
            if [a, b] in relationships and a != b:
                description["coreflexivity"] = False
                break

    for a in multiplicity:
        for b in multiplicity:
            if [a, b] in relationships and [b, a] not in relationships:
                description["symmetry"] = False
                break

    for a in multiplicity:
        for b in multiplicity:
            if [a, b] in relationships and [b, a] in relationships and a != b:
                description["anti_symmetry"] = False
                break

    for a in multiplicity:
        for b in multiplicity:
            if [a, b] in relationships and [b, a] in relationships:
                description["asymmetry"] = False
                break

    for a in multiplicity:
        for b in multiplicity:
            for c in multiplicity:
                if [a, b] in relationships and [b, c] in relationships and [a, c] not in relationships:
                    description["transitivity"] = False
                    break

    for a in multiplicity:
        for b in multiplicity:
            for c in multiplicity:
                if [a, b] in relationships and [a, c] in relationships and [b, c] not in relationships:
                    description['euclidean'] = False
                    break

    for a in multiplicity:
        for b in multiplicity:
            if a != b and not ([a, b] in relationships or [b, a] in relationships):
                description["linearity"] = False
                break

    for a in multiplicity:
        for b in multiplicity:
            if a != b and not ([a, b] in relationships or [b, a] in relationships):
                description["coherence"] = False
                break

    for a in multiplicity:
        for b in multiplicity:
            if ([a, b] in relationships) + ([b, a] in relationships) + (a == b) != 1:
                description["trichotomy"] = False
                break

    if description["reflexivity"] and description["symmetry"] and description["transitivity"]:
        description["equivalence"] = True

    if description["reflexivity"] and description["symmetry"]:
        description["tolerance"] = True

    if description["reflexivity"] and description["anti_symmetry"] and description["transitivity"]:
        description["private"] = True

    if description["transitivity"] and description["anti_reflexivity"]:
        description["full"] = True

    return description


def logic_not(left, right):
    return not right


def logic_and(left, right):
    return left and right


def logic_or(left, right):
    return left or right


def logic_nand(left, right):
    return not (left and right)


def logic_nor(left, right):
    return not (left or right)


def logic_xor(left, right):
    return left != right


def logic_xnor(left, right):
    return left == right


def logic_impl(left, right):
    return not left or right


def functions(varieties):
    description = {
        "everywhere_definitely": True,
        "simple": True,
        "surjection": True,
        "injection": True,
        "bijection": False
    }

    for a in varieties[0]:
        found = False
        for f in varieties[2:]:
            if f[0] == a:
                found = True
                break
        if not found:
            description['everywhere_definitely'] = False
            break

    for i in range(2, len(varieties)):
        for j in range(2, len(varieties)):
            if varieties[i] == varieties[j] and i != j:
                description['simple'] = False
                break
        if not description['simple']:
            break

    for b in varieties[1]:
        found = False
        for f in varieties[2:]:
            if f[1] == b:
                found = True
                break
        if not found:
            description['surjection'] = False
            break

    for b in varieties[1]:
        found = 0
        for f in varieties[2:]:
            if f[1] == b:
                found += 1
        if found != 1:
            description['injection'] = False
            break
            
        description['bijection'] = description['injection'] and description['surjection']

    return description

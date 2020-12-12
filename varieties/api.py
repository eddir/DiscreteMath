import json
import traceback
from pprint import pprint

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from varieties.math import discrete


@csrf_exempt
def binary(request, method: str) -> JsonResponse:
    try:
        multiplicity = json.loads(request.body)

        result = multiplicity[0]

        for i in range(1, len(multiplicity)):
            result = getattr(discrete, method)(result, multiplicity[i])

        return JsonResponse({
            "ok": True,
            "message": "Success",
            "data": result
        }, safe=False)

    except Exception as e:
        return JsonResponse({
            "ok": False,
            "message": "Error: %s. %s" % (e, traceback.format_exc()),
            "data": None
        })


@csrf_exempt
def properties(request, method: str) -> JsonResponse:
    try:
        multiplicity = json.loads(request.body)

        return JsonResponse({
            "ok": True,
            "message": "Success",
            "data": getattr(discrete, method)(multiplicity)
        }, safe=False)

    except Exception as e:
        return JsonResponse({
            "ok": False,
            "message": "Error: %s. %s" % (e, traceback.format_exc()),
            "data": None
        })


@csrf_exempt
def truth_table(request) -> JsonResponse:
    try:
        expression = json.loads(request.body)

        predicates = list(set(get_vars(expression)))
        predicates.sort()
        predicates_count = len(predicates)
        predicates_table = {}
        lines = 2 ** predicates_count
        c = 0

        table = [{
            "title": None,
            "rows": [1] * lines
        }] * predicates_count

        for predicate in predicates:
            table[c] = {
                "title": predicate,
                "role": "constant",
                "rows": []
            }
            for x in range(lines):
                table[c]["rows"].append(bool((x >> (predicates_count - c - 1)) % 2))

            predicates_table[predicate] = table[c]["rows"]
            c += 1

        table += evaluate(expression, predicates_table, lines)
        result_table = []
        add = True

        for column in table:
            for result_column in result_table:
                if column['title'] == result_column['title']:
                    add = False
                    break
            if add:
                result_table.append(column)

        answer_column = 0
        for i in range(len(result_table)):
            if len(result_table[i]["title"]) > len(result_table[answer_column]["title"]):
                answer_column = i

        disjunctive = ""
        conjunctive = ""

        for v in range(len(result_table[answer_column]["rows"])):
            token = ""

            if result_table[answer_column]["rows"][v]:
                operator = "and"
                expectation = True
            else:
                operator = "or"
                expectation = False

            for c in result_table:
                if c["role"] == "constant":
                    if c["rows"][v] == expectation:
                        part = c["title"]
                    else:
                        part = "not(" + c["title"] + ")"

                    if token:
                        token = operator + "(" + token + ", " + part + ")"
                    else:
                        token = part

            if expectation:
                if disjunctive:
                    disjunctive = "or(" + disjunctive + ", " + token + ")"
                else:
                    disjunctive = token
            else:
                if conjunctive:
                    conjunctive = "and(" + conjunctive + ", " + token + ")"
                else:
                    conjunctive = token

        return JsonResponse({
            "ok": True,
            "message": "Success",
            "data": {
                "table": result_table,
                "perfect_disjunctive_normal_form": disjunctive,
                "perfect_conjunctive_normal_form": conjunctive
            }
        }, safe=False)

    except Exception as e:
        return JsonResponse({
            "ok": False,
            "message": "Error: %s. %s" % (e, traceback.format_exc()),
            "data": None
        })


@csrf_exempt
def primality_test(request) -> JsonResponse:
    try:
        data = json.loads(request.body)

        return JsonResponse({
            "ok": True,
            "message": "Success",
            "data": discrete.primality_test(int(data[0][0]), int(data[1][0]))
        }, safe=False)

    except Exception as e:
        return JsonResponse({
            "ok": False,
            "message": "Error: %s. %s" % (e, traceback.format_exc()),
            "data": type(e).__name__
        })


def get_vars(expression):
    if not expression:
        return []
    elif expression['operator']['type'] == 'constant':
        return [expression['right']]
    else:
        return get_vars(expression['left']) + get_vars(expression['right'])


def evaluate(expression, predicates, lines):
    if expression['operator']['type'] == 'constant':
        return []
    elif expression['operator']['type'] == 'unary':
        return calculate(expression, predicates, lines) + evaluate(expression['right'], predicates, lines)
    else:
        return calculate(expression, predicates, lines) + evaluate(expression['right'], predicates, lines) + \
               evaluate(expression['left'], predicates, lines)


def calculate(expression, predicates, lines):
    table = {
        # "title": expression['transcript'][1:-1] if expression['transcript'][0] == '(' else expression['transcript'],
        "title": expression['transcript'],
        "role": "statement",
        "rows": [1] * lines
    }

    for i in range(lines):  # проход по строкам таблицы истинности
        values = {}
        for predicate in predicates:
            values[predicate] = predicates[predicate][i]

        result = logic(expression, values)  # расчёт
        table["rows"][i] = result

    return [table]


def logic(expression, values):
    if expression['operator']['type'] == 'constant':
        return values[expression['right']]
    elif expression['operator']['type'] == 'unary':
        left = None
        right = logic(expression['right'], values)
    else:
        left = logic(expression['left'], values)
        right = logic(expression['right'], values)

    return getattr(discrete, "logic_" + expression['operator']['name'])(left, right)

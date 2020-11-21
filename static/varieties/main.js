let activeOperation = "union";
let activeTab = "binary";

let truth_table_formula;

let multiplicityAmount = {
    "binary": 2,
    "properties": 4
}

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    const type = e.target.getAttribute('data-operation-type');
    if (type === 'binary') {
        activeOperation = e.target.getAttribute('data-operation');
    } else if (type === 'menu') {
        activeTab = e.target.getAttribute('data-operation');

        switch (activeTab) {
            case 'binary':
                activeOperation = "union";
                break;
            case 'properties':
                activeOperation = "properties";
                break;
            case 'truth_table':
                activeOperation = "";
                parseFormula();
                break;
        }
    }
    calculate();
});

$(window).on("load", calculate);


$(".add-line").on("click", function () {
    $('<div class="task-input-group"><div class="form-group user-inputs"><input type="text" class="varieties-input">' +
        '<a class="add-field"><i class="material-icons md-36">add_box</i></a></div></div>').insertBefore($(this).prev());

    multiplicityAmount[activeTab]++;
    registerFocusOutEvent();
    registerClickEvent();
});

registerFocusOutEvent();
registerClickEvent();

function registerClickEvent() {
    let button = $(".add-field");
    button.off("click");
    button.on("click", function () {
        $('<input type="text" class="varieties-input">').insertBefore(this);
        registerFocusOutEvent();
    });

    let line = $("#formula_present");
    line.off("click");
    line.on("click", function () {
        line.hide();
        $("#formula").show();
    });
}

function registerFocusOutEvent() {
    let input = $("input");
    input.off("focusout");
    input.on("focusout", function () {

        if (activeTab === "binary") {
            let inputs = $('#binary_relationships').find('.user-inputs');
            clearLines(inputs, multiplicityAmount[activeTab]);

            for (let p = 0; p < multiplicityAmount[activeTab]; p++) {
                let o = $(inputs[p]).find("input");
                if (o.length === 0) {
                    $(inputs[p]).parent().remove();
                    multiplicityAmount[activeTab]--;
                }
            }
        } else if (activeTab === "properties") {
            let inputs = $('#properties').find('.user-inputs');
            clearLines(inputs, multiplicityAmount[activeTab]);

            for (let p = 1; p < multiplicityAmount[activeTab]; p++) {
                let o = $(inputs[p]).find("input");
                if (o.length === 0) {
                    $(inputs[p]).parent().remove();
                    multiplicityAmount[activeTab]--;
                }
            }
        } else if (activeTab === "truth_table") {
            parseFormula();
        }

        calculate();
    });
}

function clearLines(lines, count) {
    for (let p = 0; p < count; p++) {
        let o = $(lines[p]).find("input");
        for (let i = o.length - 1; i >= 0; i--) {
            if (!o[i].value || o[i].value.length === 0) {
                $(lines[p]).children().eq(i).remove();
            }
        }
    }
}

function calculate() {
    $.ajax({
        url: "/api/" + activeTab + (activeOperation ? "/" + activeOperation : ""),
        type: "POST",
        data: JSON.stringify(getInputOperation()),
        success: show
    });
}

function parseOperation(formula, parentOperator = null) {

    let position;
    let operator = "";
    let part;
    let brackets = 0;

    let operations = ["not", "and", "or", "xor", "nand", "nor", "xnor"];
    let symbols = {
        "not": "¬",
        "and": "∧",
        "or": "∨",
        "nand": "|",
        "xor": "⊕",
        "nor": "↓",
        "xnor": "↔"
    }

    let leftOperand, rightOperand, commaPosition = 0, lastBracketPosition = 0;

    let re = '(' + operations.join('|') + ')\\(';

    if (formula && (position = formula.search(re)) !== -1) {
        part = formula.slice(position);

        for (let o in operations) {
            if (part.startsWith(operations[o])) {
                operator = operations[o];
                break;
            }
        }

        for (let i = position; i < formula.length; i++) {
            if (formula[i] === '(') {
                brackets++;
            } else if (formula[i] === ')') {
                if (brackets > 1) {
                    brackets--;
                } else {
                    if (operator === "not") {
                        rightOperand = formula.slice(formula.indexOf('(') + 1, i);
                    } else {
                        rightOperand = formula.slice(commaPosition + 1, i);
                    }
                }
            } else if (formula[i] === ',' && brackets === 1) {
                leftOperand = formula.slice(position + operator.length + 1, i);
                commaPosition = i;
            }
        }

        let transcript;
        if (operator === "not") {
            let right = parseOperation(rightOperand, operator);

            if (parentOperator !== null && operator !== parentOperator) {
                transcript = "(" + symbols[operator] + right["transcript"] + ")";
            } else {
                transcript = symbols[operator] + right["transcript"];
            }

            return {
                "operator": {
                    type: "unary",
                    name: operator
                },
                "left": null,
                "right": right,
                "transcript": symbols[operator] + right["transcript"],
            }

        } else {
            let left = parseOperation(leftOperand, operator);
            let right = parseOperation(rightOperand, operator);

            if (parentOperator !== null && operator !== parentOperator) {
                transcript = "(" + left["transcript"] + " " + symbols[operator] + " " + right["transcript"] + ")";
            } else {
                transcript = left["transcript"] + " " + symbols[operator] + " " + right["transcript"];
            }

            return {
                "operator": {
                    type: "binary",
                    name: operator
                },
                "left": left,
                "right": right,
                "transcript": transcript,
            }

        }

    }

    return {
        "operator": {
            type: "constant",
            name: "const"
        },
        "left": null,
        "right": formula.trim(),
        "transcript": formula.trim(),
    }

}

function parseFormula() {
    let tab = $('#truth_table');
    let input = tab.find('input')[0];
    let line = tab.find('span')[0];

    $(input).hide();
    $(line).show();

    truth_table_formula = parseOperation(input.value);

    if (truth_table_formula["transcript"].startsWith('(')) {
        truth_table_formula["transcript"] = truth_table_formula["transcript"].slice(1, -1);
    }


    line.innerHTML = truth_table_formula["transcript"];
}

function show(response) {
    if (response.ok) {
        let content = "";

        if (activeTab === "binary") {
            response.data.forEach(value => content += '<button class="btn btn-outline-primary">' + value + "</button>");
            $("#binary_relationships").find(".task-output").html(content);
        } else if (activeTab === "properties") {
            const description = {
                "reflexivity": "Рефлексивность",
                "anti_reflexivity": "Антирефлексивность",
                "coreflexivity": "Корефлексивность",
                "symmetry": "Симметричность",
                "anti_symmetry": "Антисимметричность",
                "asymmetry": "Асимметричность",
                "transitivity": "Транзитивность",
                "euclidean": "Евклидность",
                "linearity": "Линейность (полнота)",
                "coherence": "Связность",
                "trichotomy": "Трихотомия",
                "equivalence": "Эквивалентность",
                "tolerance": "Толенрантность",
                "private": "Отношение частного порядка",
                "full": "Отношение полного порядка"
            }

            for (const [key, value] of Object.entries(response.data)) {
                content += '<div class="form-group"><div class="form-check form-check-inline">\n' +
                    '  <input class="form-check-input" type="checkbox"' + (value === true ? ' checked' : '') + '>\n' +
                    '  <label class="form-check-label">' + description[key] + '</label>\n' +
                    '</div></div>'
            }

            $('#properties').find('.task-output').html(content);

            let checkboxes = $('input[type="checkbox"]');
            checkboxes.off("click");
            checkboxes.click(function (e) {
                e.preventDefault();
                e.stopPropagation();
            })
        } else if (activeTab === "truth_table") {
            let data = response.data.table.sort(function (a, b) {
                return a["title"].length < b["title"].length ? -1 : 1;
            });

            content += '<table class="table table-bordered truth-table">';
            content += "<thead class='thead-light'><tr>"

            for (let i = 0; i < data.length; i++) {
                content += '<th scope="col" data-toggle="tooltip" data-placement="top" title="' + data[i]["title"] + '">' + data[i]["title"] + '</th>';
            }

            content += "</tr></thead><tbody>"

            for (let i = 0; i < data[0]["rows"].length; i++) {
                content += '<tr>';

                for (let j = 0; j < data.length; j++) {
                    if (data[j]["rows"][i]) {
                        content += '<td class="text-success">1</td>';
                    } else {
                        content += '<td class="text-danger">0</td>';
                    }
                }

                content += '</th>';
            }

            content += "</tbody></table>";

            console.log(response)

            content += "<span>СДНФ: " + parseOperation(response.data["perfect_disjunctive_normal_form"])["transcript"] + "</span><br>";
            content += "<span>СКНФ: " + parseOperation(response.data["perfect_conjunctive_normal_form"])["transcript"] + "</span>";

            $('#truth_table').find('.task-output').html(content);
            $(function () {
                $('[data-toggle="tooltip"]').tooltip()
            })
        }
    } else {
        alert(response.message);
        console.log(response.message);
    }
}

function getInputOperation() {

    if (activeTab === 'truth_table') {
        return truth_table_formula;
    }

    const multiplicity = [...Array(multiplicityAmount[activeTab])].map(x => []);
    let inputs, tabsCount;

    if (activeTab === 'binary') {
        inputs = $('#binary_relationships').find('.task-input-group > .user-inputs');
    } else if (activeTab === 'properties') {
        inputs = $('#properties').find('.task-input-group > .user-inputs');
    }
    tabsCount = multiplicityAmount[activeTab];

    for (let p = 0; p < tabsCount; p++) {
        $.each(inputs[p].children, function (i, v) {
            if (v.value && v.value.length > 0) {
                multiplicity[p].push(v.value);
            }
        });
    }

    return multiplicity;
}
import string
import re
import ray
from flask import Flask, jsonify, request

app = Flask(__name__)


# Functions for calculations
@ray.remote
def map_r(array, f):
    return f(array)


def plus_minus_cal(holder_f: str) -> str:
    all_characters = []
    selected_math_exp = []
    x = ""
    if holder_f[0] == "-":
        return str(eval(holder_f))

    if "-" in holder_f or "+" in holder_f:
        if "--" in holder_f or "-+" in holder_f or "+-" in holder_f:
            holder_f = holder_f.replace("--", "+")
            holder_f = holder_f.replace("-+", "-")
            holder_f = holder_f.replace("+-", "-")
        else:
            if holder_f.count("-") == 1 and holder_f[0] != "-":
                arr_for_parallel = holder_f.split("-")
                arr_for_parallel[0] = plus_minus_cal(arr_for_parallel[0])
                arr_for_parallel.insert(1, "-")
                return str(eval("".join(arr_for_parallel)))
            else:
                return str(eval(holder_f))
    if "-" in holder_f and "+" not in holder_f and holder_f[0] == "-" and holder_f[1] == "-":
        return str(eval(holder_f))
    holder_f = holder_f.replace("++", "+")
    # If pluses only in holder_f
    for k, item in enumerate(holder_f):
        if k == len(holder_f) - 1:
            x += item
            all_characters.append(x)
        if x.count("+") == 1:
            if item.isdigit() or item == ".":
                x += item
            else:
                all_characters.append(x)
                all_characters.append(item)
                selected_math_exp.append(x)
                x = ""
        else:
            x += item
    if holder_f.count("+") == 1:
        return str(eval(holder_f))
    else:
        calculation_score = ray.get([map_r.remote(i, lambda i: eval(i)) for i in selected_math_exp])
        for i in range(len(all_characters)):
            if len(all_characters[i]) > 1:
                if "+" in all_characters[i]:
                    all_characters[i] = calculation_score[0]
                    calculation_score.remove(calculation_score[0])
                elif "-" in all_characters[i]:
                    all_characters[i] = calculation_score[0]
                    calculation_score.remove(calculation_score[0])
            if len(calculation_score) == 0:
                break
        second_stage_of_calculation_f = "".join(map(str, all_characters))
        return plus_minus_cal(second_stage_of_calculation_f)


def div_multi_cal(holder_f: str) -> str:
    # ZeroDivisionError verification
    if "/0" in holder_f:
        return "error"
    elif holder_f[0] == "0" and holder_f[1] != ".":
        return "error"
    elif "0/" in holder_f:
        for k, i in enumerate(holder_f):
            if i == "/":
                if holder_f[k - 1] == "0":
                    if not holder_f[k - 2].isdigit():
                        if holder_f[k - 2] == ".":
                            break
                        else:
                            return "error"
    # if everything ok
    all_characters = []
    selected_math_exp = []
    helper_2 = []
    helper_3 = []
    for_minus_output = []
    if "*-" in holder_f or "/-" in holder_f or "^" in holder_f or "_" in holder_f:
        holder_f = holder_f.replace("*-", "_")
        holder_f = holder_f.replace("/-", "^")
        helper_1 = re.split("[+|-]", holder_f)
        for item in holder_f:
            if item == "-" or item == "+":
                helper_3.append(item)

        for i in range(len(helper_1)):
            if "_" in helper_1[i] or "^" in helper_1[i]:
                helper_1[i] = helper_1[i].replace("_", "*")
                helper_1[i] = helper_1[i].replace("^", "/")
                helper_2.append((helper_1[i]))

        brackets_score_f = ray.get([map_r.remote(i, lambda z: -eval(z)) for i in helper_2])

        for i in range(len(helper_1)):
            if len(brackets_score_f) == 0:
                break
            if "*" in helper_1[i]:
                helper_1[i] = brackets_score_f[0]
            elif "/" in helper_1[i]:
                helper_1[i] = brackets_score_f[0]
        while True:
            for_minus_output.append(helper_1[0])
            if len(helper_3) == 0:
                break
            helper_1.remove(helper_1[0])
            for_minus_output.append(helper_3[0])
            helper_3.remove(helper_3[0])

        for_minus_output = list(map(lambda z: str(z), for_minus_output))
        x = "".join(for_minus_output)

        if x != "":
            if "/" in x or "*" in x:
                div_multi_cal(x)
            else:
                plus_minus_cal(x)
            return x
    # If everything ok
    x = ""
    for k, item in enumerate(holder_f):
        if k == len(holder_f) - 1:
            x += item
            all_characters.append(x)
        if x.count("*") == 1 or x.count("/") == 1:
            if item.isdigit() or item == ".":
                x += item
            else:
                all_characters.append(x)
                all_characters.append(item)
                selected_math_exp.append(x)
                x = ""
        else:
            x += item

    if len(selected_math_exp) == 0 or len(all_characters) == 1:
        return str(eval(holder_f))
    elif holder_f.count("*") == 1 and holder_f.count("/") == 0:
        return holder_f
    elif holder_f.count("*") == 0 and holder_f.count("/") == 1:
        return str(eval(holder_f))
    else:
        for i in range(len(selected_math_exp)):
            if "*-" in selected_math_exp[i]:
                selected_math_exp[i] = selected_math_exp[i].replace("-", "")

        brackets_score_f = ray.get([map_r.remote(i, lambda z: eval(z)) for i in selected_math_exp])
        for i in range(len(all_characters)):
            if len(all_characters[i]) > 1:
                if "*" in all_characters[i]:
                    all_characters[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
                elif "/" in all_characters[i]:
                    all_characters[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
            if len(brackets_score_f) == 0:
                break
            else:
                continue
        second_stage_of_calculation_f = ''.join(map(str, all_characters))

        if "*" in second_stage_of_calculation_f:
            return div_multi_cal(second_stage_of_calculation_f)
        elif "/" in second_stage_of_calculation_f:
            return div_multi_cal(second_stage_of_calculation_f)

    # Special function for isolation / and * from +-


def minus_plus_in_div_multi(holder_f: str) -> str:
    holder_f = holder_f.replace("/-", "^")
    holder_f = holder_f.replace("*-", "_")
    helper = []
    magazine = ""
    for i in range(len(holder_f)):
        if holder_f[i] == "+" or holder_f[i] == "-":
            helper.append(magazine)
            helper.append(holder_f[i])
            magazine = ""
        else:
            magazine += holder_f[i]
    helper.append(magazine)
    for i in range(len(helper)):
        if "*" in helper[i] or "/" in helper[i] or "^" in helper[i] or "_" in helper[i]:
            helper[i] = div_multi_cal(helper[i])
    return "".join(helper)


def brackets(holder_f: str) -> str:
    helper = ""
    x = 0
    storage_all = []
    storage_b = []
    counter = 0
    for i in range(len(holder_f)):
        if x > i:
            continue
        if holder_f[i] == "(":
            helper += holder_f[i]
            x = i
            flag = True
            while flag:
                if ")" not in helper:
                    counter = helper.count("(")
                    x += 1
                    helper += holder_f[x]
                else:
                    if counter > 1:
                        while counter != helper.count(")"):
                            counter = helper.count("(")
                            x += 1
                            helper += holder_f[x]
                    flag = False
            storage_all.append(helper)
            storage_b.append(helper)
            helper = ""
        else:
            storage_all.append(holder_f[i])
    while ")" in storage_all:
        storage_all.remove(")")
    for i in range(len(storage_b)):
        if storage_b[i].count(")") > 1:
            x = storage_b[i][1:-1]
            storage_b[i] = brackets(x)
    if len(storage_all) == 1 and len(storage_b) == 1:
        return brackets(holder_f[1:-1])

    storage_b_score = ray.get([map_r.remote(i, lambda z: eval(z)) for i in storage_b])

    for i in range(len(storage_all)):
        if len(storage_all) == 0:
            break
        elif "(" in storage_all[i]:
            storage_all[i] = str(storage_b_score[0])
            storage_b_score.remove(storage_b_score[0])
    zero_division_error_checker = "".join(storage_all)
    # ZeroDivisionError verification
    if "/0" in zero_division_error_checker or zero_division_error_checker[0] == "0":
        return "error"
    elif zero_division_error_checker[0] == "0" and zero_division_error_checker[1] != ".":
        return "error"
    elif "0/" in zero_division_error_checker:
        for k, i in enumerate(zero_division_error_checker):
            if i == "/":
                if zero_division_error_checker[k - 1] == "0":
                    if not zero_division_error_checker[k - 2].isdigit():
                        if zero_division_error_checker[k - 2] == ".":
                            return zero_division_error_checker
                        else:
                            return "error"
    return "".join(storage_all)


# One function for validation
def brackets_validator(s: str) -> bool:
    c = 0
    flag = False
    for i in s:
        if i == "(":
            c += 1
        elif i == ")":
            c -= 1
        if c < 0:
            return flag
    if c == 0:
        return not flag
    return flag


@app.route('/evaluate', methods=['POST'])
def calculations():
    # Variables for validation
    x = ""
    counter_for_val = 0
    s_for_brackets = ""
    forbidden_letters = set(string.ascii_lowercase + string.ascii_uppercase)
    forbidden_characters = ";:,?'|!@#$%^&_][{}£§"
    mathematical_op_for_ver = "+-/*"
    math_arr = ["*", "/", "+", "-"]
    mat_loop = ['**', "//", "*/", "/*", "-/", "/0",
                "/+", "+/", "+*", "*+", "-*", "..", "++"]
    request_data = request.get_json()
    error_msg = jsonify(error='validation error')
    if 'expression' in request_data:
        holder = request_data['expression']
    else:
        return error_msg

    # Characters validation
    if holder[0] == "0":
        return error_msg
    for item in holder:
        if not item.isdigit():
            x += " "
        else:
            x += item
    characters_checker = x.split(" ")
    for item in characters_checker:
        if item.startswith("0") and len(item) > 1:
            return error_msg

    # Checks if mathematical operator in input
    for item in holder:
        if item in math_arr:
            counter_for_val += 1

    if counter_for_val == 0:
        return error_msg
    # Checks if mathematical operators are validated
    for item in mat_loop:
        if item in holder:
            return error_msg

    for item in mathematical_op_for_ver:
        if item == "-":
            if holder.endswith(item):
                return error_msg
        elif holder.endswith(item) or holder.startswith(item):
            return error_msg

    # Checks if brackets are validated
    if ")" in holder or "(" in holder:
        for item in holder:
            if item == ")" or item == "(":
                s_for_brackets += item
        t_for_v = brackets_validator(s_for_brackets)
        if not t_for_v:
            return error_msg
        for k, item in enumerate(holder):
            if k == 0 or k == len(holder) - 1:
                continue
            elif item == "(":
                if holder[k - 1] == "(":
                    continue
                else:
                    if holder[k - 1] in mathematical_op_for_ver:
                        continue
                    else:
                        return error_msg
            elif item == ")":
                if holder[k + 1] == ")":
                    continue
                else:
                    if holder[k + 1] in mathematical_op_for_ver:
                        continue
                    else:
                        return error_msg

    # Checks if letters are in input
    for i, item in enumerate(holder):
        if item in forbidden_letters:
            return error_msg
        elif item in forbidden_characters:
            return error_msg
        elif item == ".":
            try:
                int(holder[i - 1])
                int(holder[i + 1])
            except ValueError:
                return error_msg
    # Checks negative numbers
    if "*-" in holder or "/-" in holder:
        holder = holder.replace("*-", "_")
        holder = holder.replace("/-", "^")
    # Variables for calculations
    brackets_tier_3 = "()"
    mathematical_op_tier_2 = "/*^_"
    mathematical_op_tier_1 = "+-"
    output = 0
    # Switch between mathematical operations
    if brackets_tier_3[0] in holder or brackets_tier_3[1] in holder:
        part_1 = brackets(holder)
        if "error" in part_1:
            return error_msg
        if mathematical_op_tier_2[0] in part_1 or mathematical_op_tier_2[1] in part_1:
            part_2 = minus_plus_in_div_multi(part_1)
            output = part_2

            if mathematical_op_tier_1[0] in part_2 or mathematical_op_tier_1[1] in part_2:
                output_part = minus_plus_in_div_multi(part_2)
                output = plus_minus_cal(output_part)

        elif mathematical_op_tier_1[0] in part_1 or mathematical_op_tier_1[1] in part_1:
            output = plus_minus_cal(part_1)
    elif mathematical_op_tier_2[0] in holder or mathematical_op_tier_2[1] or "^" in holder or "_" in holder:
        if mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
            output_part = minus_plus_in_div_multi(holder)
            if "error" in output_part:
                return error_msg
            else:
                output = plus_minus_cal(output_part)
        else:
            output = div_multi_cal(holder)
    elif mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
        output = plus_minus_cal(holder)
    # Changes type of an output to int or float
    try:
        output = int(output)
    except ValueError:
        output = float(output)
    if type(output) == float:
        if output == int(output):
            output = int(output)

    return jsonify(result=output)


if __name__ == '__main__':
    app.run()

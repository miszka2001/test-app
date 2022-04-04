import string
import ray
from flask import Flask, jsonify, request

app = Flask(__name__)


# Functions for calculations
@ray.remote
def small_calculations(x):
    return eval(x)


@ray.remote
def map_r(array, f):
    return f(array)


map_func = lambda i: eval(i)


def plus_minus_cal(holder_f: str) -> str:
    all_characters = []
    selected_math_exp = []
    x = ""
    for k, item in enumerate(holder_f):
        if k == len(holder_f) - 1:
            x += item
            all_characters.append(x)
        if x.count('-') == 1 or x.count('+') == 1:
            if item.isdigit() or item == ".":
                x += item
            else:
                all_characters.append(x)
                all_characters.append(item)
                selected_math_exp.append(x)
                x = ""
        else:
            x += item
    if len(selected_math_exp) == 0:
        return str(eval(all_characters[0]))
    else:
        brackets_score_f = ray.get([map_r.remote(i, map_func) for i in selected_math_exp])
        for i in range(len(all_characters)):
            if len(all_characters[i]) > 1:
                if "+" in all_characters[i]:
                    all_characters[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
                elif "-" in all_characters[i]:
                    all_characters[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
            if len(brackets_score_f) == 0:
                break
            else:
                continue
        second_stage_of_calculation_f = ''.join(map(str, all_characters))
        return plus_minus_cal(second_stage_of_calculation_f)


def div_multi_cal(holder_f: str) -> str:
    all_characters = []
    selected_math_exp = []
    x = ""
    for k, item in enumerate(holder_f):
        if k == len(holder_f) - 1:
            x += item
            all_characters.append(x)
        if x.count('*') == 1 or x.count('/') == 1:
            if item.isdigit() or item == ".":
                x += item
            else:
                all_characters.append(x)
                all_characters.append(item)
                selected_math_exp.append(x)
                x = ""
        else:
            x += item

    if len(selected_math_exp) == 0:
        return str(round(eval(all_characters[0])))
    else:
        brackets_score_f = ray.get([map_r.remote(i, map_func) for i in selected_math_exp])
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
        if '*' in second_stage_of_calculation_f:
            return div_multi_cal(second_stage_of_calculation_f)
        elif '/' in second_stage_of_calculation_f:
            return div_multi_cal(second_stage_of_calculation_f)


def minus_plus_in_div_multi(holder_f: str) -> str:
    helper = []
    x = 0
    magazine = ""
    for i in range(len(holder_f)):
        if holder_f[i] == "+" or holder_f == '-':
            helper.append(magazine)
            helper.append(holder_f[i])
            magazine = ""
        else:
            magazine += holder_f[i]
    helper.append(magazine)
    for i in range(len(helper)):
        if "*" in helper[i] or "/" in helper[i]:
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

    storage_b_score = ray.get([map_r.remote(i, map_func) for i in storage_b])
    for i in range(len(storage_all)):
        if len(storage_all) == 0:
            break
        elif "(" in storage_all[i]:
            storage_all[i] = str(storage_b_score[0])
            storage_b_score.remove(storage_b_score[0])
    return "".join(storage_all)


def brackets_validator(s):
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
    counter_for_val = 0
    s_for_brackets = ""
    forbidden_letters = set(string.ascii_lowercase + string.ascii_uppercase)
    forbidden_characters = ";:,?'|!@#$%^&_][{}£§"
    mathematical_op_for_ver = "+-/*"
    math_arr = ["*", "/", "+", "-"]
    mat_loop = ['**', "//", "-+", "+-", "*/", "/*", "-/", "/-", "/+", "+/", "+*", "*+", "-*", "*-", ".."]
    request_data = request.get_json()
    error_msg = jsonify(error='validation error')
    if 'expression' in request_data:
        holder = request_data['expression']
    else:
        return error_msg

    for item in holder:
        if item in math_arr:
            counter_for_val += 1

    if counter_for_val == 0:
        return error_msg

    for item in mat_loop:
        if item in holder:
            return error_msg
        else:
            continue

    for item in mathematical_op_for_ver:
        if holder.endswith(item) or holder.startswith(item):
            return error_msg
        else:
            continue

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


    for i, item in enumerate(holder):
        if item in forbidden_letters:
            return error_msg
        elif item in forbidden_characters:
            return error_msg
        elif item == '.':
            try:
                int(holder[i - 1])
                int(holder[i + 1])
            except ValueError:
                return error_msg
    # Variables for calculations
    brackets_tier_3 = "()"
    mathematical_op_tier_2 = "/*"
    mathematical_op_tier_1 = "+-"
    output = 0

    if brackets_tier_3[0] in holder or brackets_tier_3[1] in holder:
        part_1 = brackets(holder)
        if mathematical_op_tier_2[0] in part_1 or mathematical_op_tier_2[1] in part_1:
            output = div_multi_cal(part_1)

            if mathematical_op_tier_1[0] in part_1 or mathematical_op_tier_1[1] in part_1:
                part_2 = minus_plus_in_div_multi(part_1)
                output = plus_minus_cal(part_2)

        elif mathematical_op_tier_1[0] in part_1 or mathematical_op_tier_1[1] in part_1:
            output = plus_minus_cal(part_1)
    elif mathematical_op_tier_2[0] in holder or mathematical_op_tier_2[1] in holder:
        if mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
            output_part = minus_plus_in_div_multi(holder)
            output = plus_minus_cal(output_part)

        elif mathematical_op_tier_2[0] in holder or mathematical_op_tier_2[1] in holder:
            output = div_multi_cal(holder)
    elif mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
        output = plus_minus_cal(holder)
    else:
        return jsonify(result=error_msg)

    return jsonify(result=output)


if __name__ == '__main__':
    app.run()

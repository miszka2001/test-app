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


def plus_minus_cal(holder_f) -> str:
    brackets_handler_f = []
    additional_helper_f = []
    x = ""
    for k, item in enumerate(holder_f):
        if k == len(holder_f) - 1:
            x += item
            brackets_handler_f.append(x)
        if x.count('-') == 1 or x.count('+') == 1:
            if item.isdigit():
                x += item
            else:
                brackets_handler_f.append(x)
                brackets_handler_f.append(item)
                additional_helper_f.append(x)
                x = ""
        else:
            x += item
    if len(additional_helper_f) == 0:
        return str(eval(brackets_handler_f[0]))
    else:
        brackets_score_f = ray.get([map_r.remote(i, map_func) for i in additional_helper_f])
        for i in range(len(brackets_handler_f)):
            if len(brackets_handler_f[i]) > 1:
                if "+" in brackets_handler_f[i]:
                    brackets_handler_f[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
                elif "-" in brackets_handler_f[i]:
                    brackets_handler_f[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
            if len(brackets_score_f) == 0:
                break
            else:
                continue
        second_stage_of_calculation_f = ''.join(map(str, brackets_handler_f))
        return plus_minus_cal(second_stage_of_calculation_f)


def div_multi_cal(holder_f):
    brackets_handler_f = []
    additional_helper_f = []
    x = ""
    for k, item in enumerate(holder_f):
        if k == len(holder_f) - 1:
            x += item
            brackets_handler_f.append(x)
        if x.count('*') == 1 or x.count('/') == 1:
            if item.isdigit():
                x += item
            else:
                brackets_handler_f.append(x)
                brackets_handler_f.append(item)
                additional_helper_f.append(x)
                x = ""
        else:
            x += item

    if len(additional_helper_f) == 0:
        return str(round(eval(brackets_handler_f[0])))
    else:
        brackets_score_f = ray.get([map_r.remote(i, map_func) for i in additional_helper_f])
        for i in range(len(brackets_handler_f)):
            if len(brackets_handler_f[i]) > 1:
                if "*" in brackets_handler_f[i]:
                    brackets_handler_f[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
                elif "/" in brackets_handler_f[i]:
                    brackets_handler_f[i] = brackets_score_f[0]
                    brackets_score_f.remove(brackets_score_f[0])
            if len(brackets_score_f) == 0:
                break
            else:
                continue
        second_stage_of_calculation_f = ''.join(map(str, brackets_handler_f))
        if '*' in second_stage_of_calculation_f:
            return div_multi_cal(second_stage_of_calculation_f)
        elif '/' in second_stage_of_calculation_f:
            return div_multi_cal(second_stage_of_calculation_f)


def minus_plus_in_div_multi(holder_f):
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


def brackets(holder_f):
    helper = ""
    x = 0
    storage_all = []
    storage_b = []
    for i in range(len(holder_f)):
        if x > i:
            continue
        if holder_f[i] == "(":
            helper += holder_f[i]
            x = i
            flag = True
            while flag:
                if ")" not in helper:
                    x += 1
                    helper += holder_f[x]
                else:
                    flag = False
            storage_all.append(helper)
            storage_b.append(helper)
            helper = ""
        else:
            print(holder_f[i])
            storage_all.append(holder_f[i])
    while ")" in storage_all:
        storage_all.remove(")")
    storage_b_score = ray.get([map_r.remote(i, map_func) for i in storage_b])
    for i in range(len(storage_all)):
        if len(storage_all) == 0:
            break
        elif "(" in storage_all[i]:
            storage_all[i] = str(storage_b_score[0])
            storage_b_score.remove(storage_b_score[0])
    return "".join(storage_all)


@app.route('/evaluate', methods=['POST'])
def calculations():
    # Variables for validation
    forbidden_letters = set(string.ascii_lowercase + string.ascii_uppercase)
    forbidden_characters = ";:,?'|!@#$%^&_][{}£§"
    request_data = request.get_json()
    error_msg = jsonify(error='validation error')
    if 'expression' in request_data:
        holder = request_data['expression']
    else:
        return error_msg

    if '**' in holder:
        return error_msg
    elif '//' in holder:
        return error_msg
    elif '..' in holder:
        return error_msg
    elif holder.endswith('.') or holder.startswith('.'):
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

            if mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
                part_2 = minus_plus_in_div_multi(part_1)
                output = plus_minus_cal(part_2)

        elif mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
            output = plus_minus_cal(part_1)
    elif mathematical_op_tier_2[0] in holder or mathematical_op_tier_2[1] in holder:
        if mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
            part_1 = minus_plus_in_div_multi(holder)
            output = plus_minus_cal(part_1)

        elif mathematical_op_tier_2[0] in holder or mathematical_op_tier_2[1] in holder:
            output = div_multi_cal(holder)
    elif mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
        output = plus_minus_cal(holder)

    return jsonify(result=output)


if __name__ == '__main__':
    app.run()

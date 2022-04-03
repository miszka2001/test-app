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
    pointer = int((len(holder) - 1) / 2)
    left_side_exp = ""
    right_side_exp = ""
    flag = True
    flag_2 = True
    output = 0
    x = 0
    y = 0

    if brackets_tier_3[0] in holder or brackets_tier_3[1] in holder:
        if mathematical_op_tier_2[0] in holder or mathematical_op_tier_2[1] in holder:
            if mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
                while holder[pointer] != '+' or holder[pointer] != '-':
                    pointer += 1
                    if holder[pointer] == "(":
                        pass
            else:
                pass
        elif mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1] in holder:
            while flag:
                print(holder[pointer])
                if holder[pointer] == '+' or holder[pointer] == "-":
                    x = pointer
                    y = pointer
                    while flag_2:
                        print('a')
                        x += 1
                        if holder[x] == ')':
                            pointer = x
                            flag_2 = False
                        elif holder[x] == "(":
                            pointer = y
                            flag = False
                            flag_2 = False
                elif pointer == len(holder) - 1:
                    flag = False
                else:
                    pointer += 1
            flag = True
            if holder[pointer] != '+' or holder[pointer] != '-':
                while flag:
                    if holder[pointer] == '+' or holder[pointer] == "-":
                        flag = False
                    elif pointer == 0:
                        flag = False
                    else:
                        pointer -= 1
            for i in range(0, pointer):
                left_side_exp += holder[i]
            for i in range(pointer + 1, len(holder)):
                right_side_exp += holder[i]
            storage = ray.get([small_calculations.remote(left_side_exp), small_calculations.remote(right_side_exp)])
            output = f"{storage[0]}{holder[pointer]}{storage[1]}"
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

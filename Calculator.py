import string
import ray
from flask import Flask, jsonify, request

app = Flask(__name__)


@ray.remote
def small_calculations(x):
    return eval(x)


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
    x = 0
    y = 0

    if brackets_tier_3[0] in holder or brackets_tier_3[1] in holder:
        print('gruppe_1')
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
            while flag:
                if holder[pointer] == '+' or holder[pointer] == "-":
                    flag = False
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
            while flag:
                if holder[pointer] == '*' or holder[pointer] == "/":
                    flag = False
                elif pointer == len(holder) - 1:
                    flag = False
                else:
                    pointer += 1
            flag = True
            if holder[pointer] != '*' or holder[pointer] != '/':
                while flag:
                    if holder[pointer] == '*' or holder[pointer] == "/":
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
    elif mathematical_op_tier_1[0] in holder or mathematical_op_tier_1[1]:
        while flag:
            if holder[pointer] == '+' or holder[pointer] == "-":
                flag = False
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

    output_1 = round((eval(output)))
    return jsonify(result=output_1)


if __name__ == '__main__':
    app.run()

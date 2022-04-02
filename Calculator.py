import string
import ray
from flask import Flask, jsonify, request

app = Flask(__name__)


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
    pointer = int((len(aaa) - 1) / 2)
    left_side_exp = ""
    right_side_exp = ""
    flag = True
    flag_2 = True
    holder = 0
    x = 0
    y = 0

    holder = round((eval(holder)))
    return jsonify(result=holder)


if __name__ == '__main__':
    app.run()

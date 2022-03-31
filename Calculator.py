import string
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/evaluate', methods=['POST'])
def calculations():
    forbidden_letters = set(string.ascii_lowercase + string.ascii_uppercase)
    forbidden_characters = ";:,?'|!@#$%^&_][{}£§"
    request_data = request.get_json()
    error_msg = jsonify(error='validation error')
    if 'expression' in request_data:
        output = request_data['expression']
    else:
        return error_msg

    if '**' in output:
        return error_msg
    elif '//' in output:
        return error_msg
    elif '..' in output:
        return error_msg
    elif output.endswith('.') or output.startswith('.'):
        return error_msg

    for i, item in enumerate(output):
        if item in forbidden_letters:
            return error_msg
        elif item in forbidden_characters:
            return error_msg
        elif item == '.':
            try:
                int(output[i - 1])
                int(output[i + 1])
            except ValueError:
                return error_msg

    output = round((eval(output)))
    return jsonify(result=output)


if __name__ == '__main__':
    app.run()

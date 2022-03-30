from flask import Flask, jsonify, request
import string

app = Flask(__name__)


@app.route('/evaluate', methods=['POST'])
def calculations():
    letters = set(string.ascii_lowercase + string.ascii_uppercase)
    forbidden_characters = ";:,?'|!@#$%^&_][{}£§."
    request_data = request.get_json()
    output = request_data['expression']
    error_msg = jsonify(error='validation error')
    if "**" in output:
        return error_msg
    elif "//" in output:
        return error_msg

    for item in output:
        if item in letters:
            return error_msg
        elif item in forbidden_characters:
            return error_msg

    output = round((eval(output)))
    return jsonify(result=output)


if __name__ == '__main__':
    app.run(port=5531)

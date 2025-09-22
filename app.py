from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/getcode', methods=['GET'])
def get_code():
    return jsonify({"code": "Hello, World!"})

@app.route('/plus/<int:num1>/<int:num2>', methods=['GET'])
def plus(num1, num2):
    result = num1 + num2
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

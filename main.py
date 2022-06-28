from typing import Tuple

from flask import Flask, request, jsonify
from ecdsa import VerifyingKey, SigningKey, NIST521p
from ecdsa.keys import BadSignatureError
import werkzeug

app = Flask(__name__)
CURVE = NIST521p


def generate_key_pair() -> Tuple[str, str]:
    private_key = SigningKey.generate(curve=CURVE)
    public_key = private_key.verifying_key
    # to_string() returns type byte, but hex() returns str
    return private_key.to_string().hex(), public_key.to_string().hex()


def get_public_key_from_string(public_key: str) -> VerifyingKey:
    return VerifyingKey.from_string(bytes.fromhex(public_key), curve=CURVE)


def get_private_key_from_string(private_key: str) -> SigningKey:
    return SigningKey.from_string(bytes.fromhex(private_key), curve=CURVE)


def generate_signature(data: str, private_key: str) -> str:
    return get_private_key_from_string(private_key).sign(data.encode()).hex()


def verify_signature(data: str, public_key: str, signature: str) -> bool:
    try:
        return get_public_key_from_string(public_key).verify(bytes.fromhex(signature), data.encode())
    except BadSignatureError:
        return False


@app.route("/sign_bitstream", methods=['POST'])
def sign_bitstream():
    print(request.values)
    current_file = request.files['file'].stream.read()
    signature = generate_signature(current_file, my_private_key)
    print(request.values.get('user_id'))
    response = {
        'message': 'successfully signed',
        'public_key': my_public_key,
        'signature': signature,
    }
    return jsonify(response), 201


@app.route("/check_bitstream", methods=['GET'])
def check_bitstream():
    current_file = request.files.get('file').stream.read()
    public_key = request.form['public_key']
    signature = request.form['signature']
    result = verify_signature(current_file, public_key, signature)
    response = {
        'message': 'checked signature',
        'result': result,
    }
    return jsonify(response), 200


@app.route("/sign", methods=['POST'])
def sign():
    print(request.values)
    try:
        sha256_hash = request.form["sha256Hash"]
        sha512_hash = request.form["sha512Hash"]
        user_id = request.form["user_id"]
        assert len(sha256_hash) == 64
        assert len(sha512_hash) == 128
    except (werkzeug.exceptions.BadRequestKeyError, AssertionError) as e:
        print(e)
        response = {
            'message': 'insufficient request',
        }
        return jsonify(response), 400
    collected_data = request.form["sha256Hash"] + request.form["sha512Hash"] + request.form["user_id"]
    signature = generate_signature(collected_data, my_private_key)
    response = {
        'message': 'successfully signed',
        'public_key': my_public_key,
        'signature': signature,
    }
    print(response)
    return jsonify(response), 201


@app.route("/check", methods=['POST'])
def check():
    print(request.values)
    collected_data = request.form["sha256Hash"] + request.form["sha512Hash"] + request.form["user_id"]
    public_key = request.form['publicKey']
    signature = request.form['signature']
    result = verify_signature(collected_data, public_key, signature)
    response = {
        'message': 'checked signature',
        'result': result,
    }
    return jsonify(response), 200


if __name__ == '__main__':
    my_private_key, my_public_key = generate_key_pair()
    app.run(host='192.168.188.40', port=1337, debug=True)

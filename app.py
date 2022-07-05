import os
import time

import werkzeug
from flask import Flask, request, jsonify, send_file

from blockchain import Blockchain
from crypto_helper import generate_signature, verify_signature

app = Flask(__name__)

private_key = os.environ["private_key"]
public_key = os.environ["public_key"]

blockchain = Blockchain(private_key, public_key)


@app.route("/", methods=['GET'])
def test():
    return "The ProofSnap backend is running!", 200


@app.route("/chain", methods=['GET'])
def chain():
    return send_file('blockchain.json'), 200


# @app.route("/sign_bitstream", methods=['POST'])
# def sign_bitstream():
#     print(request.values)
#     current_file = request.files['file'].stream.read()
#     signature = generate_signature(current_file, private_key)
#     response = {
#         'message': 'successfully signed',
#         'public_key': public_key,
#         'signature': signature,
#     }
#     return jsonify(response), 201
#
#
# @app.route("/check_bitstream", methods=['GET'])
# def check_bitstream():
#     current_file = request.files.get('file').stream.read()
#     public_key = request.form['public_key']
#     signature = request.form['signature']
#     result = verify_signature(current_file, public_key, signature)
#     response = {
#         'message': 'checked signature',
#         'result': result,
#     }
#     return jsonify(response), 200


@app.route("/sign", methods=['POST'])
def sign():
    print(request.values)
    try:
        sha256_hash = request.form["sha256Hash"]
        sha512_hash = request.form["sha512Hash"]
        # the length of the hashes must be correct
        assert len(sha256_hash) == 64
        assert len(sha512_hash) == 128
    except (werkzeug.exceptions.BadRequestKeyError, AssertionError) as e:
        print(e)
        response = {
            'message': 'insufficient request',
        }
        return jsonify(response), 400
    timestamp = time.time()
    image_data = request.form["sha256Hash"] + request.form["sha512Hash"] + str(timestamp)
    signature = generate_signature(image_data, private_key)
    # the signature for image_data can be verified itself
    blockchain.store_data({'image_data': image_data, 'signature': signature}, timestamp)
    # the number of the block, in which the data is stored, is not
    response = {
        'message': 'successfully signed',
        'public_key': public_key,
        'signature': signature,
        'timestamp': timestamp,
    }
    print(response)
    return jsonify(response), 201


@app.route("/check", methods=['POST'])
def check():
    print(request.values)
    response = {
        'message': 'checked signature',
        'result': False,
    }
    try:
        image_data = request.form["sha256Hash"] + request.form["sha512Hash"] + request.form["timestamp"]
        external_public_key = request.form['publicKey']
        signature = request.form['signature']
    except:
        return jsonify(response), 200

    # check signature itself
    signature_verified = verify_signature(image_data, external_public_key, signature)
    # if the signature cannot be verified in the first place, there is no need to search for it in the blockchain
    if not signature_verified:
        return jsonify(response), 200
    # return true if signature is correct and data is found in blockchain
    response['result'] = blockchain.contains(image_data, signature)
    return jsonify(response), 200


# only necessary when running the server locally
if __name__ == '__main__':
    app.run(host='192.168.188.40', port=1337, debug=True)

"""
Trusted server that should help SMC client to communicate.
You should not need to change this file.
"""

import collections
import multiprocessing
import sys
from multiprocessing import Queue
from typing import Dict, List, Optional, Tuple

from flask import Flask, request, Response, jsonify

from shared_counter import SharedCounter
from ttp import TrustedParamGenerator

app: Flask = Flask("Trusted Third Party Server")
store: Dict[str, Dict[Tuple[str, str], bytes]] = collections.defaultdict(dict)
ttp: TrustedParamGenerator = TrustedParamGenerator()

request_counter = SharedCounter()
response_counter = SharedCounter()


@app.route("/private/<sender_id>/<receiver_id>/<label>", methods=["POST"])
def send_private_message(sender_id: str, receiver_id: str, label: str):
    """
    The client send a private message to the server.
    """
    print(
        f"[ SEND     ] SENDER {sender_id} / LABEL {label} / RECEIVER {receiver_id}"
    )
    _set_value("private", (receiver_id, label), request.get_data())
    return Response(status=200)


@app.route("/private/<receiver_id>/<label>", methods=["GET"])
def retrieve_private_message(receiver_id: str, label: str):
    """
    The client retrieve a private message from the server.
    """
    res = _get_value("private", (receiver_id, label))
    if res is not None:
        print(f"[ RETRIEVE ] RECEIVER {receiver_id} / LABEL {label}")
        return res, 200

    return Response(status=404)


@app.route("/public/<sender_id>/<label>", methods=["POST"])
def publish_message(sender_id: str, label: str):
    """
    The client publish a public message on the server.
    """
    print(f"[ PUBLISH  ] SENDER {sender_id} / LABEL {label}")
    _set_value("public", (sender_id, label), request.get_data())
    return Response(status=200)


@app.route("/public/<receiver_id>/<sender_id>/<label>", methods=["GET"])
def retrieve_public_message(receiver_id: str, sender_id: str, label: str):
    """
    The client retrieve a public message from the server.
    """
    res = _get_value("public", (sender_id, label))
    if res is not None:
        print(
            f"[ RETRIEVE ] RECEIVER {receiver_id}. LABEL {label} / SENDER {sender_id}"
        )
        return res, 200
    return Response(status=404)


@app.route("/count/bytes/<comm_type>", methods=["GET"])
def retrieve_comm_cost_bytes_num(comm_type: str):
    if comm_type == 'request':
        target_counter = request_counter
    elif comm_type == 'response':
        target_counter = response_counter
    else:
        raise TypeError("Type error: only for request and response!")
    return str(target_counter.value), 200


@app.route("/shares/<client_id>/<op_id>", methods=["GET"])
def retrieve_share(client_id: str, op_id: str):
    """
    The client retrieve Beaver triplets generated by the server.
    """
    shares = ttp.retrieve_share(client_id, op_id)
    return jsonify([share.serialize() for share in shares]), 200


def _set_value(pool: str, channel: Tuple[str, str], data: bytes) -> None:
    """
    Push data to a channel in a given pool and send an event.
    """
    store[pool][channel] = data

    # 一但有请求存储数据，记录字节数
    request_counter.increment(len(data))


def _get_value(pool: str, channel: Tuple[str, str]) -> Optional[bytes]:
    """
    Subscribe to a channel in a given pool and get it once ready.
    """
    if channel not in store[pool]:
        return None

    # 一但有请求取数据，记录字节数
    response_counter.increment(len(store[pool][channel]))
    return store[pool][channel]


def run(host: str, port: int, participants: List[str]) -> None:
    """
    Register the participants, then run the server.
    """
    for participant in participants:
        ttp.add_participant(participant)
    app.run(host, port, debug=True, threaded=False, processes=1, use_reloader=False)


def main(args: List[str]) -> None:
    """
    Entrypoint of the program.
    """
    run("localhost", 5000, args)


if __name__ == "__main__":
    main(sys.argv[1:])

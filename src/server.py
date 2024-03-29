#!/bin/python

# import socket programming library
import base64
import json
import os
import socket
import struct
import threading
import common
import asyncio

from common import Event
from asyncio import StreamReader, StreamWriter

from typing import Dict

VALID_METHODS = ["CONNECT"]


class Client:
    username: str = ""
    hostname: str = ""
    speed: str = ""
    files: {} = {}

    def __init__(self, username: str, hostname: str, speed: str, files: Dict):
        self.username = username
        self.hostname = hostname
        self.speed = speed
        self.files = files


class Server:

    clients: [] = []
    files: [] = []

    def __init__(self):
        pass

    def run(self):
        asyncio.run(self.serve())

    async def handle_request(
        self, method: str, request, reader: StreamReader, writer: StreamWriter
    ):

        if method == "CONNECT":
            username = request["username"]
            hostname = request["hostname"]
            speed = request["speed"]
            files = request["files"]

            print("Accepted new client")
            self.clients.append(Client(username, hostname, speed, files))

            await common.send_json(writer, {"success": "connection successful"})

        if method == "LIST":
            await common.send_json(writer, self.clients)

        else:
            # invalid method
            await common.send_json(
                writer,
                {"error": f"invalid method {method}, expected one of {VALID_METHODS}"},
            )

    async def serve(self):
        server = await asyncio.start_server(self.handle_connect, "127.0.0.1", 12345)

        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def handle_connect(self, reader: StreamReader, writer: StreamWriter):
        # self.clients.append(Client(reader, writer))

        while True:
            request = await common.recv_json(reader)

            if request is None:
                print("a client has disconnected")
                break

            print("-> Received Request:")
            print(json.dumps(request, indent=4, sort_keys=True))

            if not request["method"]:
                print("Invalid Request: missing method field.")
                await common.send_json(
                    writer, {"error": "invalid request: missing method field"}
                )
            else:
                await self.handle_request(request["method"], request, reader, writer)


def filter_files(path):
    _, extension = os.path.splitext(path[0])

    if extension == ".py":
        return False
    else:
        return True


if __name__ == "__main__":

    try:
        Server().run()
    except KeyboardInterrupt:
        print()
        pass

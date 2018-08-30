# Filename: Server.py
# @author: liuwei
# Created on 2018-8-8 14:06
# -*- coding: utf-8 -*-
import socket
import sys
import threading

import time


def output(msg):
    print("[", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "]: Server ::", msg)


class Server:
    def __init__(self, port):
        self.listen_port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("0.0.0.0", int(self.listen_port)))
        self.server.listen()
        output("Server listen: localhost %s" % self.listen_port)
        self.client = None
        self.ssh = None
        self.intranet_version = None

    def __del__(self):
        self.server.shutdown(socket.SHUT_WR)
        self.server.close()

    def run(self):
        thread = threading.Thread(target=self.server_process)
        thread.setDaemon(True)
        thread.start()
        while True:
            if self.client is not None:
                try:
                    # self.client.send(b'Heartbeat')
                    time.sleep(30)
                except Exception as e:
                    print(e)

    def server_process(self):
        while True:
            client, addr = self.server.accept()
            response = client.recv(1024)
            output("Receive accept data: %s" % response)
            if response == b"#CLIENT":
                output("Accept intranet client connect: %s %s" % (client, addr))
                client.send("ACC".encode("utf-8"))
                self.client = client

                thread = threading.Thread(target=self.intranet_client_process)
                thread.setDaemon(True)
                thread.start()
            elif response == b"Heartbeat":
                continue
            else:
                output("Accept outside ssh connect: %s %s" % (client, addr))
                if self.client is None:
                    output("Client don't connect, please wait")
                    continue
                self.ssh = client

                output("Send connect ssh sign to client")
                self.client.send("#CONNECT".encode("utf-8"))
                output("Send outside ssh version information to intranet client: %s" % response)
                self.client.send(response)

                thread = threading.Thread(target=self.outside_ssh_process)
                thread.setDaemon(True)
                thread.start()

    def intranet_client_process(self):
        output("Start intranet client listen")
        while True:
            response = self.client.recv(1024)
            output("Receive data for intranet client: %d " % len(response))
            if response == b'':
                output("Shutdown outside ssh")
                self.client.close()
                self.client = None
                break
            elif response == b"Heartbeat":
                continue
            if self.intranet_version is None:
                self.intranet_version = response
            if self.ssh is None:
                output("Outside ssh don't connect, error")
            else:
                self.ssh.send(response)
                output("Send to outside ssh: %d" % len(response))

    def outside_ssh_process(self):
        output("Start outside ssh listen")
        while True:
            response = self.ssh.recv(1024)
            output("Receive data from outside ssh: %d" % len(response))
            if response == b'':
                output("Shutdown outside ssh")
                self.ssh.shutdown(socket.SHUT_WR)
                self.ssh.close()
                self.ssh = None
                self.client.send(b'#CLOSE')
                break
            self.client.send(response)
            output("Send to intranet client: %d" % len(response))

    def close(self):
        self.server.shutdown(socket.SHUT_WR)
        self.server.close()
        output("Server listen close")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        server = Server(sys.argv[1])
        server.run()
    else:
        output("Please input listen port!")

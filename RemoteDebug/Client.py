# Filename: Client.py
# @author: liuwei
# Created on 2018-8-8 14:06
# -*- coding: utf-8 -*-
import socket
import sys
import threading
import configparser

import time


def output(msg):
    print("[", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "]: Client ::", msg)


def read_config(config_path):
    conf = configparser.ConfigParser()
    conf.read(config_path)
    server_ip = conf.get("Client", "ServerIP")
    server_port = conf.get("Client", "ServerPort")
    connect_ip = conf.get("Client", "ConnectIP")
    connect_port = conf.get("Client", "ConnectPort")
    return server_ip, server_port, connect_ip, connect_port


class Client:
    def __init__(self, configPath="", serverIP="", serverPort="", connectIP="", connectPort=""):
        self.client = None
        self.ssh = None
        if configPath == "":
            self.serverIP = serverIP
            self.serverPort = serverPort
            self.connectIP = connectIP
            self.connectPort = connectPort
        else:
            self.serverIP, self.serverPort, self.connect_ip, self.connect_port = read_config(configPath)


    def __del__(self):
        self.client.shutdown(socket.SHUT_WR)
        self.client.close()
        if self.ssh is not None:
            self.ssh.shutdown(socket.SHUT_WR)
            self.ssh.close()

    def connect_server(self):
        output("Try connect server: %s %s" % (self.serverIP, self.serverPort))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.serverIP, int(self.serverPort)))
        except Exception as e:
            print(e)
            output("Connect server failed")
            self.client.close()
            self.client = None
            return False
        self.client.send("#CLIENT".encode("utf-8"))
        response = self.client.recv(1024)
        if response.decode("utf-8") == "ACC":
            output("Connect server successful")
            thread = threading.Thread(target=self.client_process)
            thread.setDaemon(True)
            thread.start()
            return True
        return False

    def run(self):
        while True:
            if self.client is not None:
                try:
                    time.sleep(30)
                except Exception as e:
                    print(e)
            else:
                output("Restart connect to server: %s %s" % (self.serverIP, self.serverPort))
                self.connect_server()
            time.sleep(10)

    def intranet_ssh_process(self):
        while True:
            response = self.ssh.recv(1024)
            output("Receive data from intranet ssh: %d" % len(response))
            if response == b'':
                output("Shutdown intranet ssh")
                self.ssh.close()
                self.ssh = None
                break
            self.client.send(response)
            output("Send to server: %d" % len(response))

    def client_process(self):
        while True:
            if self.client is None:
                break
            response = self.client.recv(1024)
            output("Receive data from server: %d" % len(response))
            if response == b'':
                output("Shutdown outside server")
                self.client.close()
                self.client = None
                break
            elif response == b"Heartbeat":
                continue
            elif response == b"#CONNECT":
                output("Start to connect intranet ssh")
                if self.ssh is None:
                    self.ssh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.ssh.connect((self.connect_ip, int(self.connect_port)))
                    thread = threading.Thread(target=self.intranet_ssh_process)
                    thread.setDaemon(True)
                    thread.start()
                continue
            elif response == b'#CLOSE':
                output("Receive close ssh sign, will close intranet ssh")
                if self.ssh is not None:
                    self.ssh.close()
                    self.ssh = None
                continue
            if self.ssh is None:
                output("Don't connect intranet ssh, error!")
                continue
            else:
                try:
                    self.ssh.send(response)
                    output("Send to intranet ssh: %d" % len(response))
                except Exception as e:
                    print(e)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
        client = Client(configPath=config_path)
        client.run()
    elif len(sys.argv) == 5:
        client = Client(serverIP=sys.argv[1], serverPort=sys.argv[2], connectIP=sys.argv[3], connectPort=sys.argv[4])
        client.run()
    else:
        print("Please input config path or connect information")
        print("Client configPath")
        print("Client serverIP serverPort connectIP connectPort")

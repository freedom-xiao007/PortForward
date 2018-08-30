import threading
import unittest

from Sensor.RemoteDebug.Client import Client
from Sensor.RemoteDebug.Server import Server


class MyTestCase(unittest.TestCase):
    def test_connet(self):
        server = Server("40006")
        threading.Thread(target=server.run).start()

        client = Client("C:\Code\Python\sensor\conf\\remoteDebug.cfg")
        threading.Thread(target=client.run).start()


if __name__ == '__main__':
    unittest.main()

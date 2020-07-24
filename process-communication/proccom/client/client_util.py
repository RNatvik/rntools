import time
import socket
import json
from threading import Thread


class Publisher:
    """
    This class is used to create a publisher. This publisher can only send messages on a single topic.
    The publisher object must be supplied with a method which is used to format data to a JSON object
    """

    def __init__(self, topic: str, identity: str, msg_func, host='127.0.0.1', port=5000):
        """
        Constructor for the Publisher class

        :param topic: The topic on which to publish
        :param identity: The identity of the publisher. Should be unique
        :param msg_func: The function with which to format the message to be sent
        :param host: The IP-address of the master node which will be connected to
        :param port: The port of the master node which will be connected to
        """
        self.topic = topic
        self.id = identity
        self.msg_func = msg_func
        self.seq = 0
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        """
        Connect to the master node

        :return: None
        """
        self.soc.connect((self.host, self.port))
        d = {'type': 'publisher', 'topic': [self.topic], 'id': 'test_client'}
        self.soc.sendall(json.dumps(d).encode('utf-8'))
        self.connected = True

    def stop(self):
        """
        Close the connection to master node.

        :return:
        """
        self.soc.close()
        self.connected = False

    def publish(self, *args):
        """
        Format and publish a message to the master node

        :param args: Arguments supplied to the formatting function
        :return: a copy of the message sent to the master node
        """
        msg = {}
        try:
            if self.connected:
                self.seq += 1
                msg['topic'] = self.topic
                msg['header'] = {'name': self.id, 'sequence': self.seq, 'time': time.time()}
                msg['data'] = self.msg_func(*args)
                self.soc.sendall(json.dumps(msg).encode('utf-8'))
        except ConnectionResetError:
            print(self, ':: Master has shut down. Stopping publisher')
            self.stop()
        return msg


class Subscriber:
    """
    This class is used to create a Subscriber connected to a master node. A subscriber can subscribe to several topics
    and implement handlers for each topic. The subscriber creates its own thread for handling messages.
    """

    def __init__(self, topic_handler: dict, identity: str, host='127.0.0.1', port=5000):
        """
        Constructor for the Subscriber class

        :param topic_handler: A dictionary mapping topics to handlers: {'topic': handler_func}
        :param identity: The subscriber's identity
        :param host: The IP-address of the master node which will be connected to
        :param port: The port of the master node which will be connected to
        """
        self.handler = topic_handler
        self.id = identity
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.connected = False
        self.thread = None
        self.shutdown = False

    def connect(self):
        """
        Connect to the master node and start handler thread

        :return: None
        """
        self.soc.connect((self.host, self.port))
        d = {'type': 'subscriber', 'topic': [topic for topic in self.handler.keys()], 'id': self.id}
        self.soc.sendall(json.dumps(d).encode('utf-8'))
        self.connected = True
        self.thread = Thread(target=self._run)
        self.thread.start()

    def stop(self):
        """
        Stop the subscriber and disconnect from master

        :return: None
        """
        self.shutdown = True

    def _run(self):
        """
        Subscriber loop method. Receives data from master. Checks for shutdown flag every second

        :return: None
        """
        self.soc.settimeout(1)
        while self.connected and not self.shutdown:
            try:
                data = self.soc.recv(1024)
                data_list = self._check_for_multiple(data)
                for item in data_list:
                    jdata = json.loads(item.decode('utf-8'))
                    func = self.handler[jdata['topic']]
                    handler_thread = Thread(target=func, args=[jdata])
                    handler_thread.start()
            except socket.timeout:
                pass
            except ConnectionResetError:
                print(self, ':: Master has shut down. Stopping subscriber')
                self.shutdown = True
        self.soc.close()
        self.connected = False

    def _check_for_multiple(self, input_data: bytes):
        """
        Check received data for multiple JSON objects / messages and separate them into a list.

        :param input_data: the received data as bytes
        :return: list of individual messages
        """
        separated_data = input_data.split(b'}{')
        n = len(separated_data)
        if n > 1:
            for i in range(1, n):
                separated_data[i - 1] = separated_data[i - 1] + b'}'
                separated_data[i] = b'{' + separated_data[i]
        return separated_data

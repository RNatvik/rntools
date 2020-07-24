import json
import socket
from threading import Lock, Event


class PublisherSocket:
    """
    This class is a socket handler for a Publisher client. It listens for incoming messages from the client and forwards
    these messages to subscriber clients subscribed to the topic.
    """

    def __init__(self, con: socket.socket, addr, topic: str, subscribers: dict, identifier: str, event, timeout=1):
        """
        Constructor for the PublisherSocket class.

        :param con: The socket connection to handle
        :param addr: The address of the client
        :param topic: The publisher topic
        :param subscribers: A complete list from the server containing all topic -> subscriber mappings.
        :param identifier: The publisher's identifier
        :param event: An Event object for notifying the server that the connection is dead.
        :param timeout: The timeout duration for socket receive function
        """
        self.con = con
        self.addr = addr
        self.topic = topic
        self.subscribers = subscribers[topic]  # List of subscribers for the publisher's topic
        self.id = identifier
        self.event_flag = event
        self.shutdown = False
        self.subscriber_lock = Lock()

        self.con.settimeout(timeout)

    def add_subscriber(self, subscriber):
        """
        Add a subscriber to this publisher

        :param subscriber: the new subscriber
        :return: None
        """
        with self.subscriber_lock:
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber):
        """
        Remove a subscriber from this publisher

        :param subscriber: the subscriber to remove
        :return: None
        """
        with self.subscriber_lock:
            if subscriber in self.subscribers:
                self.subscribers.remove(subscriber)

    def stop(self):
        """
        Set shutdown flag for this connection

        :return: None
        """
        self.shutdown = True

    def run(self):
        """
        Run loop for the connection. Listens for incoming messages and forwards them to subscribers.
        Sets the disconnect event flag at end of run.

        :return:
        """
        with self.con:
            while not self.shutdown:
                try:
                    data = self.con.recv(1024)
                    if not data:
                        self.shutdown = True
                        break
                    data_list = self._check_for_multiple(data)
                    for item in data_list:
                        jdata = json.loads(item)
                        self._forward_msg(jdata)
                except socket.timeout as e:
                    pass
                except ConnectionResetError as e:
                    print(self, ':: Connection was forcibly closed by remote')
                    self.shutdown = True
                except json.JSONDecodeError:
                    print(f'{self} :: Exception caught when attempting to load the following as JSON:\n{data}')
        self.event_flag.set()

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

    def _forward_msg(self, json_obj):
        """
        Forward message to subscribers

        :param json_obj: the message to forward
        :return: None
        """
        with self.subscriber_lock:
            for subscriber in self.subscribers:
                subscriber.add_msg(json_obj)


class SubscriberSocket:
    """
    This class is a socket handler for a Subscriber client. It waits for incoming messages from publishers and forwards
    these messages to the client.
    """

    def __init__(self, con: socket.socket, addr, topics: list, identifier: str, event, timeout=1):
        """
        Constructor for the SubscriberSocket

        :param con: The socket connection to handle
        :param addr: The address of the client
        :param topics: The subscribed topics
        :param identifier: The subscriber's identifier
        :param event: An Event object for notifying the server that the connection is dead.
        :param timeout: The timeout duration for socket receive function
        """
        self.con = con
        self.addr = addr
        self.topics = topics  # List of topics this subscriber subscribes to
        self.id = identifier
        self.event_flag = event

        self.shutdown = False
        self.inbox = {key: [] for key in self.topics}
        self.inbox_lock = Lock()
        self.inbox_event = Event()
        self.con.settimeout(timeout)

    def run(self):
        """
        Run loop for the subscriber socket. Sets the disconnect event flag at end of run.

        :return: None
        """
        with self.con:
            while not self.shutdown:
                event = self.inbox_event.wait(timeout=1)
                if event:
                    self._forward_msgs()
        self.event_flag.set()

    def stop(self):
        """
        Set the shutdown flag to true

        :return: None
        """
        self.shutdown = True
        self.inbox_event.clear()

    def add_msg(self, msg):
        """
        Add a message to this subscriber socket's inbox and notify about new message

        :param msg: the message to add
        :return: None
        """
        topic = msg['topic']
        with self.inbox_lock:
            self.inbox[topic].append(msg)
            self._notify()

    def _forward_msgs(self):
        """
        Forward messages in inbox to the client.

        :return: None
        """
        if not self.shutdown:
            with self.inbox_lock:
                for key in self.topics:
                    for msg in self.inbox[key]:
                        try:
                            self.con.sendall(json.dumps(msg).encode('utf-8'))
                        except ConnectionResetError:
                            print(self, 'attempted to send to dead subscriber. (ConnectionResetError)')
                            self.shutdown = True
                        except ConnectionAbortedError:
                            print(self, 'receiver has closed connection. (ConnectionAbortedError)')
                            self.shutdown = True
                self.inbox = {key: [] for key in self.topics}
                self.inbox_event.clear()

    def _notify(self):
        """
        Notify about new message in inbox.

        :return: None
        """
        self.inbox_event.set()

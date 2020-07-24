from proccom.master.server_util import PublisherSocket, SubscriberSocket
from threading import Thread, Lock, Event
import json
import socket


class Server:
    """
    This class represents the Master node server. This class assigns handler threads for each connected client node.
    The server must be started before any publisher or subscriber can connect and transmit messages. The server monitors
    the connected client threads and removes clients which have disconnected. Only one publisher can publish on a unique
    topic
    """

    def __init__(self, host, port):
        """
        Constructor for the Server class.

        :param host: The IP-address with which to bind the TCP server socket.
        :param port: The Port to which the server will be bound
        """
        self.addr = (host, port)
        self.shutdown = False
        self.publishers = {}  # Maps string to Publisher obj
        self.subscribers = {}  # Maps string to list of Subscriber objs
        self.factory = {'publisher': self._create_publisher, 'subscriber': self._create_subscriber}
        self.threads = []
        self.lock = Lock()
        self.disconnect_event = Event()
        self.monitor_thread = Thread(target=self._monitor, name='monitor_thread', daemon=False)

    def stop(self):
        """
        Sets the shutdown flag for the server to true.

        :return: None
        """
        self.shutdown = True

    def start(self):
        """
        Start the server and the server's client monitor thread

        :return: None
        """
        self.shutdown = False
        self.monitor_thread.start()
        self._run()

    def _run(self):
        """
        Listen for new connections, assign Publisher or Subscriber according to client.

        :return: None
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind(self.addr)
            s.listen()
            while not self.shutdown:

                # Receive new connection
                try:
                    con, addr = s.accept()
                    data = con.recv(1024)
                    if not data:
                        pass  # TODO: implement handling for this?
                    error = False
                    error_msg = ''
                    with self.lock:
                        try:
                            jdata = json.loads(data.decode(
                                'utf-8'))  # Expected to be {'type': publisher/subscriber, 'topic': [...], 'id': ...}
                            connection_type = jdata['type']
                            topics = jdata['topic']
                            identifier = jdata['id']
                            func = self.factory[connection_type]
                            client = func(con, addr, topics, identifier)
                            if client is None:
                                error = True
                                error_msg = 'could not create publisher or subscriber'
                        except json.JSONDecodeError:
                            error = True
                            error_msg = f'Server error: cannot decode JSON from entry message\n Received data: {data}'
                        except KeyError:
                            error = True
                            error_msg = f'Server error: got key error when extracting data from entry message\n j-obj: {data}'
                        finally:
                            if error:
                                print(error_msg)

                            else:
                                self.debug()
                except socket.timeout:
                    pass
        print('server stop')

    def _create_publisher(self, con, addr, topics, identifier):
        """
        Creates a Publisher node connection handler and associated thread. Only one publisher can publish on a given
        topic. First registered publisher is prioritized.

        :param con: the connection socket
        :param addr: the connection address
        :param topics: the topic to publish on
        :param identifier: the identifier for the publisher node
        :return: the created publisher object if topic available. Else returns None
        """

        topic_available = True
        publisher = None
        topic = topics[0]  # Gather number 0. A publisher can only publish on 1 topic (parameter is list)
        if topic in self.publishers.keys():
            if self.publishers[topic] is not None:
                topic_available = False

        if topic_available:
            if topic not in self.subscribers.keys():
                self.subscribers[topic] = []
            publisher = PublisherSocket(con, addr, topic, self.subscribers, identifier, self.disconnect_event)
            self.publishers[topic] = publisher
            thread = Thread(target=publisher.run, name=f'{identifier}::publisher_thread', daemon=True)
            self.threads.append(thread)
            thread.start()

        return publisher

    def _create_subscriber(self, con, addr, topics, identifier):
        """
        Creates a Subscriber node connection handler and associated thread. The subscriber is added to the dictionary
        mapping topics to subscribers and is also added to the subscriber list of previously registered publisher nodes.

        :param con: the connection socket
        :param addr: the connection address
        :param topics: the topic to subscribe to
        :param identifier: the identifier for the subscriber node
        :return: The subscriber object
        """
        subscriber = SubscriberSocket(con, addr, topics, identifier, self.disconnect_event)
        for topic in topics:
            if topic in self.subscribers.keys():
                self.subscribers[topic].append(subscriber)
            else:
                self.subscribers[topic] = [subscriber]

            if topic in self.publishers.keys():
                publisher = self.publishers[topic]
                if publisher is not None:
                    publisher.add_subscriber(subscriber)

        thread = Thread(target=subscriber.run, name=f'{identifier}::subscriber_tread', daemon=True)
        self.threads.append(thread)
        thread.start()
        return subscriber

    def _monitor(self):
        """
        Monitor for connection closed events. Run cleanup procedure when event is triggered

        :return: None
        """
        while not self.shutdown:
            event = self.disconnect_event.wait(1)
            if event:
                self.disconnect_event.clear()
                self._remove_dead_nodes()
        print('monitor stop')

    def _remove_dead_nodes(self):
        """
        Finds and removes dead client threads from the server

        :return: None
        """
        with self.lock:
            dead_threads = []
            for thread in self.threads:
                if not thread.is_alive():
                    dead_threads.append(thread)
                    identity, variant = thread.getName().split('::')
                    if 'publisher' in variant:
                        for key in self.publishers.keys():
                            if self.publishers[key] is not None:
                                if self.publishers[key].id == identity:
                                    self.publishers[key] = None
                    elif 'subscriber' in variant:
                        dead_subscriber = None
                        for key in self.subscribers.keys():
                            for subscriber in self.subscribers[key]:
                                if subscriber.id == identity:
                                    dead_subscriber = subscriber
                                    break
                        dead_subscriber.stop()
                        topics = dead_subscriber.topics
                        for topic in topics:
                            self.subscribers[topic].remove(dead_subscriber)
                        for publisher in self.publishers.values():
                            if publisher is not None:
                                publisher.remove_subscriber(dead_subscriber)
            for dt in dead_threads:
                self.threads.remove(dt)
        self.debug()

    def debug(self):
        """
        Method for displaying information for debugging the server

        :return: None
        """
        print('registered publishers:', self.publishers)
        print('registered subscribers:', self.subscribers)
        print('active threads', self.threads, '\n')


def main():
    server = Server('127.0.0.1', 5000)
    server.start()


if __name__ == '__main__':
    main()

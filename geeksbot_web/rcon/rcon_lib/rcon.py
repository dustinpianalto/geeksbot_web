import logging
import itertools
import struct
import socket
import time

# Packet types
SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0

__all__ = ['RCONPacket', 'RCONConnection']

rcon_log = logging.getLogger('rcon_lib')


class RCONPacket:
    def __init__(self, packet_id: int = 0, packet_type: int = -1, body: str = ''):
        self.packet_id = packet_id
        self.packet_type = packet_type
        self.body = body

    def __str__(self):
        """Return the body of the packet"""
        return self.body

    def size(self):
        """Return the size of the packet"""
        return len(self.body) + 10

    def pack(self):
        """Return the packed packet"""
        return struct.pack(f'<3i{len(self.body) + 2}s',
                           self.size(),
                           self.packet_id,
                           self.packet_type,
                           bytearray(self.body, 'utf-8'))


class RCONConnection:
    """Connection to an RCON server"""

    def __init__(self, host: str, port: int, password: str = '', single_packet: bool = False):
        """Create a New RCON Connection

        Parameters:
            host (str): The hostname or IP address of the server to connect to
            port (int): The port to connect to on the server
            password (str): The password to authenticate with the server
            single_packet (bool): True for servers who don't give 0 length SERVERDATA_RESPONSE_VALUE requests
        """

        self.host = socket.gethostbyname(host)
        self.port = port
        self.password = password
        self.single_packet = single_packet
        self.packet_id = itertools.count(1)
        self.socket: socket.socket = None
        self.authenticated = False

    def connect(self):
        """Returns -1 if connection times out
        Returns 1 if connection and auth are successful
        Returns 0 if auth fails"""
        try:
            rcon_log.debug(f'Connecting to {self.host}:{self.port}...')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except TimeoutError as e:
            rcon_log.error(f'Timeout error: {e}')
            return -1
        else:
            rcon_log.debug('Connected. Attempting to Authenticate...')
            auth_packet = RCONPacket(next(self.packet_id), SERVERDATA_AUTH, self.password)
            self.send_packet(auth_packet)
            response = self.read()
            if response.packet_type == SERVERDATA_AUTH_RESPONSE and response.packet_id != -1:
                rcon_log.debug(f'Authorized {response.packet_type}:{response.packet_id}:{response.body}')
                self.authenticated = True
                return 1
            else:
                rcon_log.debug(f'Not Authorized {response.packet_type}:{response.packet_id}:{response.body}')
                self.authenticated = False
                return 0

    def send_packet(self, packet):
        if packet.size() > 4096:
            rcon_log.error('Packet Size is larger than 4096 bytes. Cannot send packet.')
            raise RuntimeWarning('Packet Size is larger than 4096 bytes. Cannot send packet.')
        if self.socket is None:
            self.connect()
        rcon_log.debug(f'Sending Packet {packet.packet_id}: {packet.pack() if packet.packet_type is not SERVERDATA_AUTH else "Censored for Password Security."}')
        self.socket.send(packet.pack())
        rcon_log.debug(f'Packet {packet.packet_id} Sent.')

    def read(self, request: RCONPacket = None, multi_packet=False) -> RCONPacket:
        rcon_log.debug(f'Waiting to receive response to packet {request.packet_id if request else None}')
        response = RCONPacket()
        try:
            if request:
                while response.packet_id != request.packet_id and response.packet_id < request.packet_id:
                    if multi_packet:
                        time.sleep(.01)
                        response = self._receive_multi_packet()
                        rcon_log.debug(f'Received Multi-Packet response to packet {request.packet_id}:\n'
                                       f'{response.packet_type}:{response.packet_id}:{response.body}')
                    else:
                        response = self.receive_packet()
                        rcon_log.debug(f'Received Single-Packet response to packet {request.packet_id}:\n'
                                       f'{response.packet_type}:{response.packet_id}:{response.body}')
            else:
                response = self.receive_packet()
                rcon_log.debug(f'Received Single-Packet response:\n'
                               f'{response.packet_type}:{response.packet_id}:{response.body}')
        except struct.error as e:
            rcon_log.error(f'Struct Error: {e}')
            response = RCONPacket(body='Error receiving data from the server. '
                                       'Please try again in a little bit.')
        except AttributeError as e:
            rcon_log.error(f'Attribute Error: {e}')
            response = RCONPacket(body='Error receiving data from the server. '
                                       'Please try again in a little bit.')
        return response

    def receive_packet(self):
        header = self.socket.recv(struct.calcsize('<3i'))
        (packet_size, packet_id, packet_type) = struct.unpack('<3i', header)
        body = self.socket.recv(packet_size - 8)
        return RCONPacket(packet_id, packet_type, body.decode('ascii'))

    def _receive_multi_packet(self):
        header = self.socket.recv(struct.calcsize('<3i'))
        (packet_size, packet_id, packet_type) = struct.unpack('<3i', header)
        body = self._read_all(packet_size)
        return RCONPacket(packet_id, packet_type, body.decode('ascii'))

    def _read_all(self, chunk_size):
        fragments = []
        while True:
            part = self.socket.recv(chunk_size)
            fragments.append(part)
            if len(part) < chunk_size:
                break
        return b''.join(fragments)

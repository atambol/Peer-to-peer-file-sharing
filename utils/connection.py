import socket
import records
from commons import *


# Create a connection object from client to server
def connect2server(hostname, port):
    Logging.debug("Entering utils.connect2server")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, port)

    try:
        sock.connect(server_address)
    except socket.error as err:
        Logging.error("Connect to server (%s, %s) failed with error %s" % (hostname, port, err))

    Logging.info("Connected to server (%s, %s)" % server_address)
    Logging.debug("Exiting utils.connect2server")
    return sock


# Send a request to server
def send_request(peer_ip, peer_port, command, data):
    Logging.debug("Entering utils.send_request")
    sock = connect2server(peer_ip, peer_port)

    # Encode the request
    request = records.P2PRequest(command, data)

    # Send request to peer
    try:
        Logging.info("Sending request \n%s" % request.display())
        sock.sendall(request.encode())
    except socket.error as err:
        sock.close()
        Logging.error("send_request failed with error %s" % err)
    Logging.debug("Exiting utils.send_request")
    return sock


# Get a response from the server
def accept_response(sock):
    Logging.debug("Entering utils.accept_response")

    # Receive response from peer
    try:
        msg_str = sock.recv(1024)
    except socket.error as err:
        Logging.error("accept_response failed with error %s" % err)

    # Decode the response
    response = records.P2PResponse.decode(msg_str)
    Logging.info("Received response \n%s" % response.display())
    Logging.info("Response code interpretation : %s" % response.status_message())
    sock.close()
    Logging.debug("Exiting utils.accept_response")
    return response


# Open a socket to listen for clients
def listen4clients(server_address):
    Logging.debug("Entering utils.listen4clients")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(server_address)
        sock.listen(1)
        Logging.info("Server listening on (%s, %s)" % server_address)
    except socket.error as err:
        raise Exception("listen4clients failed with error \n%s\n Possibly the port is busy." % err)
    Logging.debug("Exiting utils.listen4clients")
    return sock


# Accept request messages from a client
def accept_request(sock):
    Logging.debug("Entering utils.accept_request")
    try:
        connection, client_address = sock.accept()
        Logging.info("Received connection request from (%s, %s)" % client_address)
        raw_msg = connection.recv(1024)
    except socket.error as err:
        raise Exception("accept_request failed with error %s" % err)
    request = records.P2PRequest.decode(raw_msg)
    Logging.info("Received message \n%s" % request.display())
    Logging.debug("Exiting utils.accept_request")
    return connection, request


# Respond to a client
def send_response(connection, response):
    Logging.debug("Entering utils.send_response")
    Logging.info("Responding with message \n%s" % response.display())
    try:
        connection.sendall(response.encode())
        connection.close()
    except socket.error as err:
        raise Exception("respond_to_connection failed with error %s" % err)
    Logging.debug("Exiting utils.send_response")


# Accept rfc
def accept_rfc(sock, filename):
    Logging.debug("Entering utils.accept_rfc")
    f = open(filename, "wb")
    raw_msg = sock.recv(1024)
    while raw_msg:
        response = records.P2PResponse.decode(raw_msg)
        print "******************received %s" % response.display()
        f.write(response.data)
        raw_msg = sock.recv(1024)
    f.close()
    sock.close()
    Logging.debug("Exiting utils.accept_rfc")
    return


# Send rfc
def send_rfc(connection, filename):
    Logging.debug("Entering utils.send_rfc")
    f = open(filename, "rb")
    msg = f.read(1024)
    while msg:
        response = records.P2PResponse("200", msg)
        print "******************sending %s" % response.display()
        connection.send(response.encode())
        msg = f.read(1024)
    connection.shutdown(socket.SHUT_WR)
    f.close()
    Logging.debug("Exiting utils.send_rfc")
    return


# Get local ip address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
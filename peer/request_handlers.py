import pickle
from commands import *
import records


# Register a client with the server
def register_request(server_ip, server_port, params):
    utils.Logging.debug("Entering peer.register_request")
    sock = utils.send_request(server_ip, server_port, "Register", params)
    response = utils.accept_response(sock)
    if response.status == "200":
        data = response.data["cookie"]
    else:
        data = response.data["message"]
    utils.Logging.debug("Exiting peer.register_request")
    return response.status, data


# De-registeration a client from the server
def leave_request(server_ip, server_port, params):
    utils.Logging.debug("Entering peer.leave_request")
    sock = utils.send_request(server_ip, server_port, "Leave", params)
    response = utils.accept_response(sock)
    utils.Logging.debug("Exiting peer.leave_request")
    return response.status, response.data["message"]


# Query for peers
def peer_query_request(server_ip, server_port, params):
    utils.Logging.debug("Entering peer.peer_query_request")
    sock = utils.send_request(server_ip, server_port, "PQuery", params)
    response = utils.accept_response(sock)
    if response.status == "200":
        data = response.data["peers"]
    else:
        data = response.data["message"]
    utils.Logging.debug("Exiting peer.peer_query_request")
    return response.status, data


# Send keep alive signal
def keep_alive_request(server_ip, server_port, params):
    utils.Logging.debug("Entering peer.keep_alive_request")
    sock = utils.send_request(server_ip, server_port, "KeepAlive", params)
    response = utils.accept_response(sock)
    utils.Logging.debug("Exiting peer.keep_alive_request")
    return response.status, response.data["message"]


# Handle get rfc, client side
def get_rfc_from_peers(peer_info, rfc_number):
    utils.Logging.debug("Entering peer.get_rfc_from_peers")
    rfc_path = None
    utils.Logging.info("Displaying local rfc list before querying any peers :%s\n"
                       % records.display_rfc_list(peer_info.rfc_index_head))

    # Query all peers for rfc
    for peer in peer_info.peers:

        # Query a peer for its rfc index head
        peer_rfc_index_head = get_rfc_index_from_peer(peer["hostname"], peer["port"])
        if peer_rfc_index_head:
            utils.Logging.info("Displaying rfc list from (%s, %s) :%s\n"
                               % (peer["hostname"], peer["port"], records.display_rfc_list(peer_rfc_index_head)))
            peer_info.rfc_index_head = records.merge(peer_info.rfc_index_head, peer_rfc_index_head)
            utils.Logging.info("Displaying rfc list on merge :%s\n"
                               % records.display_rfc_list(peer_info.rfc_index_head))

            # Check if the local rfc indexed combined with peer rfc index contains the rfc required
            rfc = peer_info.rfc_index_head.find(rfc_number)
            if rfc:
                # Download the rfc and update the local index
                utils.Logging.info("RFC found on (%s, %s)" % (peer["hostname"], peer["port"]))
                rfc_path = get_rfc_from_peer(peer["hostname"], peer["port"], rfc_number)
                update_rfc_metadata(rfc.number, rfc.title)
    utils.Logging.debug("Exiting peer.get_rfc_from_peers")
    return rfc_path


# Handle an rfc index query request, server side
def handle_rfcs_query(rfc_index_head):
    utils.Logging.debug("Entering peer.handle_rfcs_query")
    node_list = records.encode_rfc_list(rfc_index_head)
    utils.Logging.debug("Exiting peer.handle_rfcs_query")
    return {"rfcs": node_list}


# Handle a get rfc request, server side
def handle_get_rfc(rfc_file):
    f = open(rfc_file, "rb")
    data = f.read(1024)
    while data:
        yield data
    f.close()




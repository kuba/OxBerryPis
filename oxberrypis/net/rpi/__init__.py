"""Network communcation happening at RaspberryPi."""
import zmq

from ..proto.rpi_pb2 import StockEvent


visualisation_uri = "tcp://visualmachine:portnum"

context = zmq.Context()

def get_to_visualisation(context):
    to_visualisation = context.socket(zmq.PUSH)
    to_visualisation.connect(visualisation_uri)
    return to_visualisation


# TODO: set up sockets from the parser
# orderbooks in map called orderbooks


def make_price_message(timestamp_s, timestamp_ns, stock_id, pi_id, matching_engines):
    """Makes the message to send to visualisation."""
    event = StockEvent()
    event.stock_id = stock_id
    event.timestamp_s = timestamp_s
    event.timestamp_ns = timestamp_ns
    event.pi_id = pi_id

    matching_engine = matching_engines[stock_id]

    top_sell_price, top_buy_price = matching_engine.get_best_orders()

    if top_buy_price is not None:
        event.top_buy_price = top_buy_price
    if top_sell_price is not None:
        event.top_sell_price = top_sell_price

    return event


def run(from_parser,to_visualisation):
    """Run The loop (no termination yet!)"""
    while true :
        msg = StockMessage()
        [id,contents]= from_parser.recv_multipart();
        msg.parseFromString()
        stock_id = handle_message(msg)
        visual_msg = make_price_message(msg.packet_time,msg.packet_time_ns,stock_id)
        if message.type == StockMessage.TRADE:
            visual_msg.last_trade_price = message.trade.price
        to_visualisation.send(msg.serialize_to_string())

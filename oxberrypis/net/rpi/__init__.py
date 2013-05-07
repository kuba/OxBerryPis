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


def make_price_message(timestamp, stock_id, pi_id, orderbooks):
    event = StockEvent()
    event.stock_id = stock_id
    event.timestamp = timestamp
    event.pi_id = pi_id

    top_buy_price = orderbooks[stock_id].get_buy_head_order()
    top_sell_price = orderbooks[stock_id].get_sell_head_order()

    if top_buy_price is not None:
        event.top_buy_price = top_buy_price
    if top_sell_price is not None:
        event.top_sell_price = top_sell_price

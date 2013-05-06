"""Network communcation happening at RaspberryPi."""
import zmq

from ..orderbook.order import Order
from .proto.rpi_pb2 import StockMessage


pi_id = 0 #TODO: get unique identifier

visualisation_uri = "tcp://visualmachine:portnum"

context = zmq.context()


to_visualisation = context.socket(zmq.PUSH)
to_visualisation.conect(visualisation_uri)


# TODO: set up sockets from the parser
# orderbooks in map called order_books


def make_price_message(timestamp,stock_id):
    event = StockEvent()
    event.stock_id = stock_id
    event.timestamp = timestamp
    event.pi_id = pi_id
    top_buy_price = order_books[stock_id].get_buy_head_order()
    top_sell_price = order_books[stock_id].get_sell_head_order()
    if top_buy_price is not None:
        event.top_buy_price = top_buy_price
    if top_sell_price is not None:
        event.top_sell_price = top_sell_price

def handle_from_parser(from_parser):
    """Handle network communcation from the parser."""
    msg = StockMessage()
    msg.parseFromString(from_parser.recv())
    handle_message(msg)

def handle_message(message):
    """Handles a stock message from the parser."""
    if message.type == StockMessage.ADD:
        add_msg = message.add

        stock_id = add_msg.symbol_index
        order_id = add_msg.order_id
        limit_price = add_msg.price
        num_shares = add_msg.volume

        if add_msg.side == Side.BUY:
            side = Order.BUY
        else:
            side = Order.SELL

        orderbooks[stock_id].add_order(
            order_id,
            limit_price,
            num_shares,
            side,
        )
    elif message.type == StockMessage.MODIFY:
        modify_msg = message.modify

        stock_id = modify_msg.symbol_index
        order_id = modify_msg.order_id
        limit_price = modify_msg.price
        num_shares = modify_msg.volume

        if modify_msg.side == Side.BUY:
            side = Order.BUY
        else:
            side = Order.SELL

        orderbooks[stock_id].update_order(
            order_id,
            limit_price,
            num_shares,
            side,
        )
    elif message.type == StockMessage.DELETE:
        delete_msg = message.delete

        stock_id = delete_msg.symbol_index
        order_id = delete_msg.order_id

        if delete_msg.side == Side.BUY:
            side = Order.BUY
        else:
            side = Order.SELL

        orderbooks[stock_id].remove_order(order_id)

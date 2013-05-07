"""Network communcation happening at RaspberryPi."""
import zmq

from ..orderbook.order import Order
from .proto.rpi_pb2 import StockMessage
from ..errors import OxBerryPisException

pi_id = 0 #TODO: get unique identifier

visualisation_uri = "tcp://visualmachine:portnum"

context = zmq.context()


to_visualisation = context.socket(zmq.PUSH)
to_visualisation.conect(visualisation_uri)


# TODO: set up sockets from the parser
# orderbooks in map called order_books


def make_price_message(timestamp_s,timestamp_ns,stock_id):
    """Makes the message to send to visulsiation"""
    event = StockEvent()
    event.stock_id = stock_id
    event.timestamp_s = timestamp_s
    event.timestamp_ms = timestamp_ms
    event.pi_id = pi_id
    top_buy_price = order_books[stock_id].get_buy_head_order()
    top_sell_price = order_books[stock_id].get_sell_head_order()
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
        msg.parseFromString())
        stock_id = handle_message(msg)
        visual_msg = make_price_message(msg.packet_time,msg.packet_time_ns,stock_id)
        if message.type == StockMessage.TRADE:
            visual_msg.last_trade_price = message.trade.price
        to_visualisation.send(msg.serialize_to_string())


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
        return stock_id
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
        return stock_id
    elif message.type == StockMessage.DELETE:
        delete_msg = message.delete

        stock_id = delete_msg.symbol_index
        order_id = delete_msg.order_id

        if delete_msg.side == Side.BUY:
            side = Order.BUY
        else:
            side = Order.SELL

        orderbooks[stock_id].remove_order(order_id)
        return stock_id
    elif message.type == StockMessage.EXECUTE:
        exec_msg = message.execution

        stock_id = exec_msg.symbol_index
        order_id = exec_msg.order_id

        limit_price = exec_msg.price
        num_shares = exec_msg.volume

        if exec_msg.reason_code == OBExecution.FILLED:
            orderbooks[stock_id].remove_order(order_id)
        elif exec_msg.reason_code == OBExecution.PARTIAL :
            orderbooks[stock_id].update_decrese_order(
                order_id,
                limit_price,
                num_shares,
                side
            )
        # otherwise do nothing (this type of message may be useless)
        return stock_id
    elif message.type == StockMessage.TRADE
        trade_msg = message.trade

        stock_id = trade_msg.symbol_index    
        return stock_id
    else:
        raise OxBerryPisExecption("Invalid Message Type")
            

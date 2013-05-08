"""Handlers for stock messages."""
import zmq

from ...orderbook.order import Order

from ..proto.stock_pb2 import StockMessage
from ..proto.rpi_pb2 import StockEvent


class StockMessagesToOrderbook(object):
    """Stock messages handler."""

    def __init__(self, matching_engines):
        self.matching_engines = matching_engines

    def handle_stock_message(self, message):
        """Update appropriate order book based on a stock ``message``."""
        if message.type == StockMessage.ADD:
            add_msg = message.add

            stock_id = add_msg.symbol_index
            order_id = add_msg.order_id
            limit_price = add_msg.price
            num_shares = add_msg.volume

            if add_msg.side == add_msg.BUY:
                side = Order.BUY
            else:
                side = Order.SELL

            self.matching_engines[stock_id].add_order(
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

            if modify_msg.side == modify_msg.BUY:
                side = Order.BUY
            else:
                side = Order.SELL

            self.matching_engines[stock_id].update_order(
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

            if delete_msg.side == delete_msg.BUY:
                side = Order.BUY
            else:
                side = Order.SELL

            self.matching_engines[stock_id].remove_order(order_id)

            return stock_id
        elif message.type == StockMessage.EXECUTE:
            exec_msg = message.execution

            stock_id = exec_msg.symbol_index
            order_id = exec_msg.order_id

            limit_price = exec_msg.price
            num_shares = exec_msg.volume

            matching_engine = self.matching_engines[stock_id]
            if exec_msg.reason_code == exec_msg.FILLED:
                self.matching_engine.remove_order(order_id)
            elif exec_msg.reason_code == exec_msg.PARTIAL:
                self.matching_engine.decrease_order_amount_by(
                    order_id,
                    num_shares,
                )
            else:
                #  otherwise do nothing (this type of message may be useless)
                pass

            return stock_id
        elif message.type == StockMessage.TRADE:
            trade_msg = message.trade

            stock_id = trade_msg.symbol_index
            return stock_id
        else:
            raise OxBerryPisExecption("Invalid Message Type")


class ToVisualisation(object):
    """Send stock messages to visualisation"""

    def __init__(self, matching_engines, visualisation_uri, context):
        self.matching_engines = matching_engines

        self.to_visualisation = context.socket(zmq.PUSH)
        self.to_visualisation.connect(visualisation_uri)

        self.last_top_buy = {}
        self.last_top_sell = {}

    def make_price_message(self, stock_msg, stock_id, channel_id):
        """Makes the message to send to visualisation."""
        matching_engine = self.matching_engines[stock_id]

        top_sell_order, top_buy_order = matching_engine.get_best_orders()

        if top_buy_order is not None:
            top_buy_price = top_buy_order.price
        else:
            top_buy_price = None

        if top_sell_order is not None:
            top_sell_price = top_sell_order.price
        else:
            top_sell_price = None

        if (stock_msg.type != StockMessage.TRADE and
            stock_id in self.last_top_buy and
            stock_id in self.last_top_sell and
            self.last_top_buy[stock_id] == top_buy_price and
            self.last_top_sell[stock_id] == top_sell_price):
            return None

        self.last_top_buy[stock_id] = top_buy_price
        self.last_top_sell[stock_id] = top_sell_price

        stock_event = StockEvent()
        stock_event.stock_id = stock_id
        stock_event.timestamp_s = stock_msg.packet_time
        stock_event.timestamp_ns = stock_msg.packet_time_ns
        stock_event.channel_id = channel_id

        if top_buy_price is not None:
            stock_event.top_buy_price = top_buy_price
        if top_sell_price is not None:
            stock_event.top_sell_price = top_sell_price
        if stock_msg.type == StockMessage.TRADE:
            stock_event.last_trade_price = stock_msg.trade.price

        return stock_event

    def handle_send_visual(self, stock_id, channel_id, stock_msg):
        """Handle sending a single stock event to visualisation"""
        stock_event = self.make_price_message(stock_msg, stock_id, channel_id)
        if stock_event is not None:
            serialized_stock_event = stock_event.SerializeToString()
            self.to_visualisation.send(serialized_stock_event)

import stockExchange
import zmq


pi_id = 0 #TODO: get unique identifier

visualisation_uri = ""

context = zmq.context()


to_visualisation = context.socket(zmq.PUSH)
to_visualisation.conect(visualisation_uri)


# TODO: set up sockets from the parser
# orderbooks in map called order_books


def sendNewPrice(timestamp,stock_id):
    event = StockEvent()
    event.stock_id = stock_id
    event.timestamp = timestamp
    event.pi_id = pi_id
    top_buy_price = order_books[stock_id].get_buy_head_order()
    top_sell_price = order_books[stock_id].get_sell_head_order()
    if (top_buy_price is not None):
        event.top_buy_price = top_buy_price
    if (top_sell_price is not None):
        event.top_sell_price = top_sell_price
    to_visualisation.sent(event.SerializeToString())


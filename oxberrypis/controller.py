import stockExchange
import zmq


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
    if (top_buy_price is not None):
        event.top_buy_price = top_buy_price
    if (top_sell_price is not None):
        event.top_sell_price = top_sell_price
    

msg = StockEvent()
msg.parseFromString(from_parser.recv())

def handle_message(message):
    if(message.message_type == MessageType.ADD_MESSAGE):
        stock_id = message.stock_id
        order_id = message.order_id
        limit_price = message.price
        num_shares = message.volume
        if (message.side = Side.BUY):
            orderbooks[stock_id].add_order(order_id,limit_price,num_shares,"buy")
        else:
            orderbooks[stock_id].add_order(order_id,limit_price,num_shares,"sell")
    elif(message.message_type == MessageType.MODIFY_MESSAGE):
        stock_id = message.stock_id
        order_id = message.order_id
        limit_price = message.price
        num_shares = message.volume
        if (message.side = Side.BUY):
            orderbooks[stock_id].update_order(order_id,limit_price,num_shares,"buy")
        else:
            orderbooks[stock_id].update_order(order_id,limit_price,num_shares,"sell")
    elif(message.message_type == MessageType.DELETE_MESSAGE):
        stock_id = message.stock_id
        order_id = message.order_id
        if (message.side = Side.BUY):
            orderbooks[stock_id].remove_order(order_id)
        else:
            orderbooks[stock_id].remove_order(order_id)
    

            
        

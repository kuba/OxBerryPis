import zmq

from oxberrypis.net.proto.rpi_pb2 import StockEvent

context = zmq.Context()
sink = context.socket(zmq.PULL)
sink.bind('tcp://*:1236')

while True:
    data = sink.recv()
    stock_event = StockEvent()
    stock_event.ParseFromString(data)
    print stock_event

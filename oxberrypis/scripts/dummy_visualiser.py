"""Dummy visualiser."""
import zmq

from oxberrypis.net.proto.controller_pb2 import SetupVisualisation
from oxberrypis.net.proto.rpi_pb2 import StockEvent


def main():
    context = zmq.Context()

    vissync_uri = 'tcp://127.0.0.1:1234'
    visual_uri = 'tcp://*:1237'

    vissync = context.socket(zmq.REQ)
    vissync.connect(vissync_uri)

    visual = context.socket(zmq.PULL)
    visual.bind(visual_uri)

    # Sync with Initializer
    vissync.send('')
    setup_vis_parsed = vissync.recv()
    vissync.send('')

    setup_vis = SetupVisualisation()
    setup_vis.ParseFromString(setup_vis_parsed)
    print setup_vis

    while True:
        break
        data = visual.recv()
        stock_event = StockEvent()
        stock_event.ParseFromString(data)
        print stock_event


if __name__ == '__main__':
    main()

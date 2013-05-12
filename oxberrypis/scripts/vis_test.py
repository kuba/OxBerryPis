"""Dummy visualiser."""
import sys

import zmq

from oxberrypis.net.proto.controller_pb2 import SetupVisualisation
from oxberrypis.net.proto.rpi_pb2 import StockEvent


def main():
    if len(sys.argv) != 3:
        exit("USAGE: {} vissync_uri visual_uri".format(sys.argv[0]))

    vissync_uri = sys.argv[1]
    visual_uri = sys.argv[2]

    context = zmq.Context()

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
        data = visual.recv()
        stock_event = StockEvent()
        stock_event.ParseFromString(data)
        print stock_event

if __name__ == '__main__':
    main()

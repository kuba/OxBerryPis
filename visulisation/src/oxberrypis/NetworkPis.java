package oxberrypis;

import org.zeromq.ZMQ;
import org.zeromq.ZMQ.Context;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;
import oxberrypis.net.proto.setup.VisInit.SetupVisualisation;

import com.google.protobuf.InvalidProtocolBufferException;

public class NetworkPis {
	Context context = ZMQ.context(1);
	ZMQ.Socket receiver = context.socket(ZMQ.PULL);

	private final String PARSER_ADDRESS = "tcp://parser:3143";

	public NetworkPis() {
		receiver.bind("tcp://*:3142");
	}

	/**
	 * get the next raw message
	 * 
	 * @return
	 */
	public StockEvent getMsg() {
		try {
			StockEvent t = StockEvent.parseFrom(receiver.recv(0));
			return t;
		} catch (InvalidProtocolBufferException e) {
			throw new Error("Invalid Message Recieved"); // this should never
															// happen so fail
															// fast

		}

	}

	/**
	 * get the init message
	 * 
	 * @return
	 */
	public SetupVisualisation getInit() {
		// TODO:
		ZMQ.Socket fromParser = context.socket(ZMQ.REQ);
		fromParser.connect(PARSER_ADDRESS);
		fromParser.send("INIT");
		try {
			return SetupVisualisation.parseFrom(fromParser.recv(0));
		} catch (InvalidProtocolBufferException e) {
			throw new Error("Invalid Message Recieved"); // this should never
															// happen so fail
															// fast
		}
	}
}

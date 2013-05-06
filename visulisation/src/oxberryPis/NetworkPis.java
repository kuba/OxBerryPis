package oxberryPis;

import org.zeromq.ZMQ;
import org.zeromq.ZMQ.Context;
import oxberryPis.VisProt.StockEvent;
import com.google.protobuf.InvalidProtocolBufferException;

public class NetworkPis {
	Context context = ZMQ.context(1);
	ZMQ.Socket receiver = context.socket(ZMQ.PULL);

	public NetworkPis() {
		receiver.bind("tcp://*:3142");
	}

	public StockEvent getMsg() {
		try {
			StockEvent t = StockEvent.parseFrom(receiver.recv(0));
			return t;
		} catch (InvalidProtocolBufferException e) {
			throw new Error("Invalid Message Recieved");

		}

	}
	public VisProt.SetupVisualisation getInit() {
		// TODO: this.getLength();
		return null;
	}
}

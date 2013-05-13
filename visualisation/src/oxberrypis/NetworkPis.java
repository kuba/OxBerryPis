package oxberrypis;

import org.zeromq.ZMQ;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;
import oxberrypis.net.proto.controller.Controller.SetupVisualisation;

import com.google.protobuf.InvalidProtocolBufferException;

/**
 * Class around ZMQ.
 * 
 * The constructor creates the context.
 * 
 * @author alex
 * 
 */
public class NetworkPis {
	private ZMQ.Socket initSync;
	private ZMQ.Socket fromRPis;

	public NetworkPis(ZMQ.Context context, String initSyncURI, String fromRPisURI) {
		initSync = context.socket(ZMQ.REQ);
		initSync.connect(initSyncURI);
		
		fromRPis = context.socket(ZMQ.PULL);
		fromRPis.bind(fromRPisURI);
	}

	/**
	 * Get the next raw message from the RPis.
	 * 
	 * @return
	 */
	public StockEvent getNextStockEvent() {
		StockEvent stockEvent;
		
		byte[] data = fromRPis.recv(0);
		
		try {
			stockEvent = StockEvent.parseFrom(data);
		} catch (InvalidProtocolBufferException e) {
			// this should never happen so fail fast
			throw new Error("Invalid Message Recieved");
		}
		
		return stockEvent;
	}

	/**
	 * Get the initialisation message from the Initializer.
	 * 
	 * @return
	 */
	public SetupVisualisation getInit() {
		SetupVisualisation setupVisualisation;
		
		initSync.send("");
		byte[] reply = initSync.recv(0);
		
		try {
			setupVisualisation = SetupVisualisation.parseFrom(reply);
		} catch (InvalidProtocolBufferException e) {
			// this should never happen so fail fast
			throw new Error("Invalid Message Recieved");
		}
		
		return setupVisualisation;
	}
}
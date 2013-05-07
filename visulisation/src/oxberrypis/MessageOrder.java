package oxberrypis;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import oxberrypis.net.proto.rpi.Rpi.StockEvent;
import oxberrypis.net.proto.setup.VisInit.SetupVisualisation;

public class MessageOrder {
	private NetworkPis network;
	private Map<Integer, Integer> idToQueue;
	private Map<Integer, String> idToName;
	private List<Queue<StockEvent>> queueList;
	private int denomPower;
	private Map<Integer, Integer> lastSeqNum;

	public MessageOrder() {
		network = new NetworkPis();
		idToQueue = new HashMap<Integer, Integer>();
		idToName = new HashMap<Integer, String>();
		queueList = new ArrayList<Queue<StockEvent>>();
		init();
	}

	public int getDenomPower() {
		return denomPower;
	}

	public String getName(int stockId) {
		return idToName.get(new Integer(stockId));
	}

	private void init() {
		SetupVisualisation m = network.getInit(); // Get the initialisation
													// method from parser
		denomPower = m.getDenomPower();
		List<List<Integer>> pis = new ArrayList<List<Integer>>();
		List<Integer> streamIds = new ArrayList<Integer>();
		// Cheating Map<(List(Pi),Stream),Int> that is which pis go to which
		// queue. These two must be same length, this way we we don't have to
		// define extra types
		// with hash and equals implementaions
		for (SetupVisualisation.SymbolDefn definition : m.getSymbolList()) { // Iterating
																				// over
																				// stocks
			int symbolId = definition.getSymbolId();
			int streamId = definition.getStreamId();
			idToName.put(symbolId, definition.getSymbolName()); // Map ids to
																// names
			boolean foundMatch = false;
			List<Integer> pisOrder = definition.getPiIdsList();
			Collections.sort(pisOrder); // Sort pi orders to get canonical
										// representation
			for (int i = 0; i < pis.size(); i++) { // Iterate over things in the
													// "map"
				boolean foundMismatch = false;
				for (int j = 0; j < pis.get(i).size(); j++) {
					if (pisOrder.get(j) != pis.get(i).get(j)) { // If the pis
																// are
																// different,
																// break out
						foundMismatch = true;
						break;
					}
				}
				if (streamId != streamIds.get(i))
					foundMismatch = true; // If streams are different, ignore
				if (!foundMismatch) {
					foundMatch = true;
					idToQueue.put(symbolId, i); // If they match, add it to the
												// global map
					lastSeqNum.put(symbolId, 0);
				}
			}
			if (!foundMatch) { // Add a new set of pis and stockId
				idToQueue.put(symbolId, pis.size());
				pis.add(pisOrder);
				streamIds.add(streamId);
			}
		}
		for (int i = 0; i < pis.size(); i++) { // Create all the queues
			queueList.add(new LinkedList<StockEvent>());
		}
	}

	private void addMessage(StockEvent message) { // Find the queue and add the
													// message, update sequence
													// number
		int queueId = idToQueue.get(message.getStockId());
		if (lastSeqNum.get(message.getStockId()) < message.getSeqNum()) {
			queueList.get(queueId).add(message);
			lastSeqNum.put(message.getStockId(), message.getSeqNum());
		}
	}

	/**
	 * Get the next message to process
	 */
	public StockEvent getMessage() {
		while (anyEmptyQueue()) {
			addMessage(network.getMsg());
		}
		int bestTime = queueList.get(0).peek().getTimestamp();
		Queue<StockEvent> bestQueue = queueList.get(0);
		for (Queue<StockEvent> q : queueList) {
			if (q.peek().getTimestamp() < bestTime)
				bestQueue = q;
		}
		return bestQueue.remove();
	}

	private boolean anyEmptyQueue() {
		for (Queue<StockEvent> q : queueList) {
			if (q.isEmpty())
				return true;
		}
		return false;
	}
}

package oxberrypis;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;
import oxberrypis.net.proto.controller.Controller.SetupVisualisation;
import oxberrypis.net.proto.controller.Controller.SetupVisualisation.SymbolMapping;
import oxberrypis.net.proto.controller.Controller.SetupVisualisation.SymbolRange;

/**
 * Stock data provider with ordered stock events.
 * 
 * Returns the messages in roughly order so the stocks stay in sync.
 * 
 * @author alex
 * 
 */
public class OrderedStockEvents implements StockDataProvider {
	private final NetworkPis network;

	// maps per stock (may make a type and condense)
	private Map<Integer, Integer> idToQueue;
	private Map<Integer, Integer> idToRange;
	private Map<Integer, String> idToName;
	private Map<Integer, Integer> denomPowers;
	private Map<Integer, Integer> lastSeqNum;

	private List<Queue<StockEvent>> queueList = new ArrayList<Queue<StockEvent>>();
	private List<Integer> ranges = new ArrayList<Integer>();
	private List<Integer> channels = new ArrayList<Integer>();

	/**
	 * Create the class and initialise the network
	 */
	public OrderedStockEvents(NetworkPis network) {
		this.network = network;
	}

	/**
	 * Gets the log to base 10 of the demander for this stockId
	 * 
	 * @param stockId
	 * @return logarithm of the denominator
	 */
	public int getDenomPower(int stockId) {
		return denomPowers.get(stockId);
	}

	/**
	 * Gets the name of the stock
	 * 
	 * @param stockId
	 * @return
	 */
	public String getName(int stockId) {
		return idToName.get(stockId);
	}

	boolean hasInit = false;

	/**
	 * initialise the class. Must be done on same thread as 
	 * receives the message
	 * 
	 * @param message
	 */
	public synchronized void init() {
		// create the maps
		idToQueue = new HashMap<Integer, Integer>();
		idToName = new HashMap<Integer, String>();
		idToRange = new HashMap<Integer, Integer>();
		denomPowers = new HashMap<Integer, Integer>();
		lastSeqNum = new HashMap<Integer, Integer>();
		
		// set up the mappings to pis
		SetupVisualisation setupVisualisation = network.getInit();
		List<SymbolRange> ranges = setupVisualisation.getRangeList();
		
		int current_range_id = 0;
		for (SymbolRange range: ranges) {
			List<SymbolMapping> mappings = range.getMappingList();
			
			for (SymbolMapping mapping: mappings) {
				int symbolIndex = mapping.getSymbolIndex();
				idToRange.put(symbolIndex, current_range_id);
				denomPowers.put(symbolIndex, mapping.getPriceScaleCode());
				idToName.put(symbolIndex, mapping.getSymbol());
				idToQueue.put(symbolIndex, -1);
				lastSeqNum.put(symbolIndex, -1);
			}
			
			current_range_id++;
		}
		
		hasInit = true;
		
		notify();
	}

	/**
	 * Waits for initialisation
	 * @throws InterruptedException
	 */
	public synchronized void waitInit() throws InterruptedException {
		while (!hasInit)
			wait();
	}

	/**
	 *  Find the queue and add the message, update sequence number
	 *  
	 * @param message
	 */
	private void addMessage(StockEvent message) {
		int stockId = message.getStockId();
		int queueId = idToQueue.get(stockId);

		if (queueId == -1) {
			queueId = findQueue(message);
			idToQueue.put(stockId, queueId);
		}
		
		int seqNum = message.getSeqNum();
		if (lastSeqNum.get(stockId) < seqNum) {
			queueList.get(queueId).add(message);
			lastSeqNum.put(stockId, seqNum);
		}
	}

	private int findQueue(StockEvent message) {
		int channelId = message.getChannelId();
		int range = idToRange.get(message.getStockId());
		
		for (int i = 0; i < queueList.size(); i++) {
			if (ranges.get(i) == range && channels.get(i) == channelId) {
				return i;
			}
		}
		
		queueList.add(new LinkedList<StockEvent>());
		ranges.add(range);
		channels.add(channelId);
		return queueList.size() - 1;
	}

	/**
	 * Get the next message to process
	 */
	public StockEvent getNextStockEvent() {
		while (!queuesReady()) {
			addMessage(network.getNextStockEvent());
		}
		
		long bestTime = getTime(queueList.get(0).peek());
		Queue<StockEvent> bestQueue = queueList.get(0);
		for (Queue<StockEvent> q : queueList) {
			if (getTime(q.peek()) < bestTime)

				bestQueue = q;
		}
		return bestQueue.remove();
	}

	private long getTime(StockEvent s) {
		return ((long) (s.getTimestampS()) * 1000000000)
				+ (long) s.getTimestampNs();
	}

	private boolean queuesReady() {
		if (queueList.size() < 4) {
			// make sure we have received a decent number of different sources
			return false;
		}
		
		for (Queue<StockEvent> q : queueList) {
			// TODO: breaks when one channel finishes; add timeouts
			if (q.isEmpty()) {
				return false;
			}
		}
		
		return true;
	}
}
package oxberrypis;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;
import oxberrypis.net.proto.vis_init.VisInit.SetupVisualisation;
import oxberrypis.net.proto.vis_init.VisInit.SetupVisualisation.Mapping;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 * Returns the messages in roughply order so the stocks stay in sync. Also set
 * up other data to do with the stocks
 * 
 * @author alex
 * 
 */
public class MessageOrder {
	private NetworkPis network;

	// maps per stock (may make a type and condense)
	private Map<Integer, Integer> idToQueue;
	private Map<Integer, Integer> idToRegion;
	private Map<Integer, String> idToName;
	private Map<Integer, Integer> denomPowers;
	private Map<Integer, Integer> lastSeqNum;

	private List<Queue<StockEvent>> queueList = new ArrayList<Queue<StockEvent>>();
	private List<Integer> regions;
	private List<Integer> streams;
	
	private final String ARCAFILE = "";

	private final String bind_uri;
	private final String parser_uri;

	/**
	 * Create the class and initialise the network
	 */
	public MessageOrder(String bind_uri, String parser_uri) {
		this.bind_uri = bind_uri;
		this.parser_uri = parser_uri;

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
	 * recieves the message
	 * 
	 * @param message
	 */
	public synchronized void init() {
		// create the maps
		idToQueue = new HashMap<Integer, Integer>();
		idToName = new HashMap<Integer, String>();
		idToRegion = new HashMap<Integer, Integer>();
		List<Integer> stocks = readArcaStocksFile();
		
		network = new NetworkPis(bind_uri);
		SetupVisualisation message = network.getInit(parser_uri);
		List<Mapping> mappings = message.getMappingsList();
		// set up the mappings to pis

		int i = 0;
		for (Mapping m : mappings) {
			List<Integer> mappingStocks = stocks.subList(m.getSymbolMapStart(),
					m.getSymbolMapEnd());
			for (int stock : mappingStocks) {
				idToRegion.put(stock, i);
			}
			i++;
		}
		hasInit = true;
		notify();
	}

	/**
	 * Waits for initialisation
	 * @throws InterruptedException
	 */
	public synchronized void waitInit() throws InterruptedException {
		while (!hasInit) {
			wait();
		}
	}

	/**
	 * Read the ARCA tocks file, setting up all the maps and returning the list
	 * of all stockIds
	 * 
	 * @return
	 */
	private List<Integer> readArcaStocksFile() {
		List<Integer> stocks = new ArrayList<Integer>();
		// Taken from
		// http://www.mkyong.com/java/how-to-read-file-from-java-bufferedreader-example/
		BufferedReader br = null;
		try {

			String sCurrentLine;

			br = new BufferedReader(new FileReader(ARCAFILE));

			while ((sCurrentLine = br.readLine()) != null) {
				String[] parts = sCurrentLine.split("\\|");
				int sId = Integer.parseInt(parts[2]);
				denomPowers.put(sId, Integer.parseInt(parts[7]));
				idToName.put(sId, parts[0]);
				idToQueue.put(sId, -1);
				stocks.add(sId);
			}

		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				if (br != null)
					br.close();
			} catch (IOException ex) {
				ex.printStackTrace();
			}
		}
		return stocks;
	}

	private void addMessage(StockEvent message) { // Find the queue and add the
													// message, update sequence
													// number
		int queueId = idToQueue.get(message.getStockId());

		if (queueId == -1) {
			queueId = findQueue(message);
			idToQueue.put(message.getStockId(), queueId);
		}

		if (lastSeqNum.get(message.getStockId()) < message.getSeqNum()) {
			queueList.get(queueId).add(message);
			lastSeqNum.put(message.getStockId(), message.getSeqNum());
		}
	}

	private int findQueue(StockEvent message) {
		int streamId = message.getChannelId();
		int region = idToRegion.get(message.getStockId());
		for (int i = 0; i < queueList.size(); i++) {
			if (regions.get(i) == region && streams.get(i) == streamId) {
				return i;
			}
		}
		queueList.add(new LinkedList<StockEvent>());
		regions.add(region);
		streams.add(streamId);
		return queueList.size() - 1;

	}

	/**
	 * Get the next message to process
	 */
	public StockEvent getMessage() {
		while (queuesReady()) {
			addMessage(network.getMsg());
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
			// make sure we have recieved a decent number of fifferent sources
			return false;
		}
		for (Queue<StockEvent> q : queueList) {
			if (q.isEmpty())
				return true;
		}
		return false;
	}
}

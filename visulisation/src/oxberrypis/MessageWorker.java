package oxberrypis;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.swing.SwingWorker;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;

class MessageWorker extends SwingWorker<Void, StockEvent> {

	private Map<Integer, Stock> data;
	private Map<Integer, StockView> viewMap;
	private String bind_uri;
	private String parser_uri;

	/**
	 * A worker that waits for messages and updates the controls
	 * 
	 * @param data
	 *            the data to update
	 * @param messageOrder
	 *            message provider
	 * @param viewMap
	 *            controls to update on UI thread
	 */
	MessageWorker(Map<Integer, Stock> data, Map<Integer, StockView> viewMap,
			String bind_uri, String parser_uri) {
		this.data = data;
		this.viewMap = viewMap;
		this.bind_uri = bind_uri;
		this.parser_uri = parser_uri;
	}

	MessageOrder messageOrder = new MessageOrder(bind_uri, parser_uri);

	@Override
	public Void doInBackground() throws Exception {
		messageOrder.init();
		while (true) {
			StockEvent message = messageOrder.getMessage();
			this.publish(message);
		}
	}

	@Override
	protected void process(List<StockEvent> stockEvents) {

		try {
			messageOrder.waitInit();

			Set<Integer> stockIds = new HashSet<Integer>();
			for (StockEvent message : stockEvents) {
				int stockId = message.getStockId();
				if (!data.containsKey(stockId)) {
					Stock s = new Stock(messageOrder.getName(stockId), 1); // TODO:
																			// Change
																			// 1
																			// to
																			// message.getDenomPower()
					data.put(stockId, s);
					viewMap.put(stockId, new StockView(s));
				}
				if (message.hasTradePrice())
					data.get(stockId)
							.update(message.getTradePrice(),
									message.getTopBuyPrice(),
									message.getTopSellPrice());
				else
					data.get(stockId).update(message.getTopBuyPrice(),
							message.getTopSellPrice());
			}

			for (int stockId : stockIds) {
				this.viewMap.get(stockId).change();
			}
		} catch (InterruptedException ignore) {
			// exit if we are cancelles
		}

	}
}
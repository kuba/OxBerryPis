package oxberrypis;

import java.util.List;
import java.util.Map;

import javax.swing.SwingWorker;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;

class MessageWorker extends SwingWorker<Void, Integer> {

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

	@Override
	public Void doInBackground() throws Exception {
		MessageOrder messageOrder = new MessageOrder(bind_uri, parser_uri);
		while (true) {
			StockEvent message = messageOrder.getMessage();
			if (this.data.containsKey(message.getStockId())) {
				if (message.hasTradePrice())
					this.data.get(message.getStockId()).update(
							message.getTradePrice(), message.getTopBuyPrice(),
							message.getTopSellPrice());
				else
					this.data.get(message.getStockId())
							.update(message.getTopBuyPrice(),
									message.getTopSellPrice());
			} else {
				throw new Error("Unknown stock");
			}
			setProgress(message.getStockId());
		}
	}

	@Override
	protected void process(List<Integer> stockIds) {
		for (int stockId : stockIds) {
			this.viewMap.get(stockId).change();
		}

	}
}
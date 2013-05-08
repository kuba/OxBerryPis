package oxberrypis;

import java.util.List;
import java.util.Map;

import javax.swing.SwingWorker;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;

class MessageWorker extends SwingWorker<Void, Integer> {

	private Map<Integer, Stock> data;
	private MessageOrder messageOrder;
	private Map<Integer, StockView> viewMap;

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
	MessageWorker(Map<Integer, Stock> data, MessageOrder messageOrder,
			Map<Integer, StockView> viewMap) {
		this.data = data;
		this.messageOrder = messageOrder;
		this.viewMap = viewMap;
	}

	@Override
	public Void doInBackground() throws Exception {
		while (true) {
			StockEvent message = this.messageOrder.getMessage();
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
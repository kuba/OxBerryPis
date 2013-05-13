package oxberrypis;

import java.util.List;
import java.util.Map;

import javax.swing.JPanel;
import javax.swing.SwingWorker;

import org.zeromq.ZMQ;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;

/**
 * A worker that waits for stock events and updates the controls.
 *
 */
class MessageWorker extends SwingWorker<Void, StockEvent> {

	private Map<Integer, Stock> data;
	private Map<Integer, StockView> viewMap;
	
	private JPanel stocksPanel;
	
	private NetworkPis network;
	private StockDataProvider stockDataProvider;
	
	/**
	 * Create the worker.
	 * 
	 * @param context		ZMQ context.
	 * @param initSyncURI	ZMQ URI for synchronisation with the Initializer.
	 * @param fromRPisURI	ZMQ URI RaspberryPis connect to.
	 * @param data
	 * @param viewMap
	 * @param stocksPanel	Panel
	 */
	MessageWorker(ZMQ.Context context,
			String initSyncURI,
			String fromRPisURI,
			Map<Integer, Stock> data,
			Map<Integer, StockView> viewMap,
			JPanel stocksPanel) {
		this.data = data;
		this.viewMap = viewMap;

		network = new NetworkPis(context, initSyncURI, fromRPisURI);
		
		this.stocksPanel = stocksPanel;
	}

	@Override
	public Void doInBackground() throws Exception {
		//stockDataProvider = new OrderedStockEvents(
		stockDataProvider = new UnorderedStockEvents(
			network
		);
		
		while (!isCancelled()) {
			StockEvent stockEvent = stockDataProvider.getNextStockEvent();
			publish(stockEvent);
		}
		
		return null;
	}

	@Override
	protected void process(List<StockEvent> stockEvents) {
		for (StockEvent stockEvent : stockEvents) {
			int stockId = stockEvent.getStockId();

			if (!data.containsKey(stockId)) {
				Stock stock = new Stock(
					stockDataProvider.getName(stockId),
					stockDataProvider.getDenomPower(stockId)
				);
				data.put(stockId, stock);

				StockView stockView = new StockView(stock);	
				viewMap.put(stockId, stockView);
				
				stocksPanel.add(stockView);
				stocksPanel.repaint();
				stocksPanel.invalidate();
				stocksPanel.repaint();
			}
	
			Stock stock = data.get(stockId);
			StockView stockView = viewMap.get(stockId);

			if (stockEvent.hasTradePrice())
				stock.update(
					stockEvent.getTradePrice(),
					stockEvent.getTopBuyPrice(),
					stockEvent.getTopSellPrice()
				);
			else
				stock.update(
					stockEvent.getTopBuyPrice(),
					stockEvent.getTopSellPrice()
				);

			stockView.change();
		}
	}
}
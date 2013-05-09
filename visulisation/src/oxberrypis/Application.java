package oxberrypis;

import java.awt.Dimension;
import java.awt.GridLayout;
import java.util.HashMap;
import java.util.Map;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.SwingWorker;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;

public class Application extends JFrame {
	private static final long serialVersionUID = 1L;
	Map<Integer, Stock> data;
	MessageOrder messageOrder;
	Map<Integer, StockView> viewMap;

	public Application() {
		this.setTitle("Oxberry Pis");
		data = new HashMap<Integer, Stock>();
		viewMap = new HashMap<Integer, StockView>();
		JPanel panel = new JPanel();
		// for (int i : messageOrder.getStockList()) {
		// viewMap.put(i, new StockView(new Stock(messageOrder.getName(i))));
		// }
		// messageOrder = new MessageOrder();
		// for(StockView s : viewMap.values()) {
		// add(s);
		// }
		GridLayout grid = new GridLayout(0, 12, 40, 25);
		panel.setLayout(grid);
		for (int i = 0; i < 82; i++) {
			Stock s = new Stock("HSBC", 4);
			s.update(i * 10, i * 11, i + 10);
			viewMap.put(i, new StockView(s));
			panel.add(viewMap.get(i));
		}
		JScrollPane pane = new JScrollPane(panel,
				JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
				JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
		pane.setViewportView(panel);
		pane.getVerticalScrollBar().setUnitIncrement(75);
		add(pane);
		pack();
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setPreferredSize(new Dimension(1024, 768));
		setVisible(true);
		setExtendedState(getExtendedState() | JFrame.MAXIMIZED_BOTH);
	}

	public void newMessage() { // Puts stock into map if not already present,
								// otherwise updates
		StockEvent message = messageOrder.getMessage();
		int stockId = message.getStockId();
		if (!data.containsKey(stockId)) {
			Stock s = new Stock(messageOrder.getName(stockId), 1); // TODO:
																	// Change 1
																	// to
																	// message.getDenomPower()
			data.put(stockId, s);
			viewMap.put(stockId, new StockView(s));
		}
		if (message.hasTradePrice())
			data.get(stockId).update(message.getTradePrice(),
					message.getTopBuyPrice(), message.getTopSellPrice());
		else
			data.get(stockId).update(message.getTopBuyPrice(),
					message.getTopSellPrice());
	}

	public void startReceivingMessages(String bind_uri, String parser_uri) {
		SwingWorker<Void, StockEvent> a = new MessageWorker(data, viewMap, bind_uri, parser_uri);
		a.execute();
	}

	public static void main(String[] args) {
		@SuppressWarnings("unused")
		Application a = new Application();
	}
}
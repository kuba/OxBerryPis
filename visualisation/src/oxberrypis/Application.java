package oxberrypis;

import java.awt.Dimension;
import java.awt.GridLayout;
import java.util.HashMap;
import java.util.Map;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.SwingWorker;

import org.zeromq.ZMQ;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;


public class Application extends JFrame {
	private static final long serialVersionUID = 1L;
	
	public static final String TITLE = "OxBerryPis";

	private SwingWorker<Void, StockEvent> messageWorker;

	public Application(ZMQ.Context context,
			String initSyncURI,
			String fromRPisURI) {
		JPanel stocksPanel = createStocksPanel();
		
		Map<Integer, Stock> data = new HashMap<Integer, Stock>();
		Map<Integer, StockView> viewMap = new HashMap<Integer, StockView>();

		messageWorker = new MessageWorker(
			context,
			initSyncURI,
			fromRPisURI,
			data,
			viewMap,
			stocksPanel
		);
		
//		messageOrder = new MessageOrder();
//		for (int i : messageOrder.getStockList()) {
//			viewMap.put(i, new StockView(new Stock(messageOrder.getName(i))));
//			}
//			messageOrder = new MessageOrder();
//			for(StockView s : viewMap.values()) {
//			add(s);
//		}
		
		createUI(stocksPanel);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	}
	
	private JPanel createStocksPanel() {
		// Stocks panel and its layout
		JPanel panel = new JPanel();
		GridLayout grid = new GridLayout(0,10,40,25);
		panel.setLayout(grid);
		return panel;
	}
	
	private void createUI(JPanel panel) {
		setTitle(TITLE);
		
		// Main scrollable pane
		JScrollPane pane = new JScrollPane(panel,
				JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
				JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
		pane.setViewportView(panel);
		pane.getVerticalScrollBar().setUnitIncrement(75);
		add(pane);
		
		setPreferredSize(new Dimension(1024, 768));
		setVisible(true);
		setExtendedState(getExtendedState() | JFrame.MAXIMIZED_BOTH);
		
		pack();
	}

	/**
	 * Start receiving messages in a separate thread, and updating the
	 * UI in the Swing thread.
	 * 
	 */
	private void startReceivingMessages() {
		messageWorker.execute();
	}
	
	public void run() {
		startReceivingMessages();
	}

	public static void main(String[] args) {
		ZMQ.Context context = ZMQ.context(1);
		String initSyncURI = "tcp://127.0.0.1:1234";
		String fromRPisURI = "tcp://127.0.0.1:1237";
		
		Application app = new Application(context, initSyncURI, fromRPisURI);
		app.run();
	}
}
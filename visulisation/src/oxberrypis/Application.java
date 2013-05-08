package oxberrypis;

import java.awt.Dimension;
import java.awt.GridLayout;
import java.util.HashMap;
import java.util.Map;

import javax.swing.JFrame;
import javax.swing.SwingWorker;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;

public class Application extends JFrame{
	private static final long serialVersionUID = 1L;
	Map<Integer,Stock> data;
	MessageOrder messageOrder;
	Map<Integer,StockView> viewMap;
	public Application() {
		data = new HashMap<Integer,Stock>();
		messageOrder = new MessageOrder();
		viewMap = new HashMap<Integer,StockView>();
		for (int i : messageOrder.getStockList()) {
			Stock s = new Stock(messageOrder.getName(i));
			data.put(i, s);
			viewMap.put(i, new StockView(s));
		}
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		GridLayout grid = new GridLayout(4,10, 20, 20); //TODO: Fix these numbers
		this.setLayout(grid);
		for(StockView s : viewMap.values()) {
			add(s);
		}
//		for(int i = 0; i< 60; i++) { A test for the layout
//			Stock s = new Stock(i+"");
//			s.update(i*10, i*11, i+10);
//			viewMap.put(i, new StockView(s));
//			this.add(viewMap.get(i));
//		}
		this.pack();
		this.setVisible(true);
		this.setPreferredSize(new Dimension(1024,768));
	}
	
	public void newMessage() {
		StockEvent message = messageOrder.getMessage();
		if(data.containsKey(message.getStockId())) {
			if(message.hasTradePrice())	data.get(message.getStockId()).update(message.getTradePrice(),message.getTopBuyPrice(),message.getTopSellPrice());
			else data.get(message.getStockId()).update(message.getTopBuyPrice(),message.getTopSellPrice());
		}
		else {
			throw new Error("Unknown stock");
		}
	
	}
	
	public void receiveMessage() {
		SwingWorker<Integer,Void> a = new SwingWorker<Integer,Void>() {

			@Override
			public Integer doInBackground() throws Exception {
				StockEvent message = messageOrder.getMessage();
				if(data.containsKey(message.getStockId())) {
					if(message.hasTradePrice())	data.get(message.getStockId()).update(message.getTradePrice(),message.getTopBuyPrice(),message.getTopSellPrice());
					else data.get(message.getStockId()).update(message.getTopBuyPrice(),message.getTopSellPrice());
				}
				else {
					throw new Error("Unknown stock");
				}
				return message.getStockId();
			}
			
			public void done() {
				try {
					Integer stockId = get();
					viewMap.get(stockId).change();
					Application.this.receiveMessage();
				}
				catch (InterruptedException ignore){}
				catch (java.util.concurrent.ExecutionException e) {
					throw new Error("Error getting message");
				}
				
			}
		};
		a.execute();
	}
	
	public static void main(String[] args) {
		Application a = new Application();
	}
}
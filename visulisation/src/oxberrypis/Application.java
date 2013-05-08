package oxberrypis;

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
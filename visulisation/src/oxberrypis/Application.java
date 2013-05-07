package oxberrypis;

import java.util.HashMap;
import java.util.Queue;

import javax.swing.DefaultListModel;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JSplitPane;
import javax.swing.JTextField;
import oxberrypis.net.proto.rpi.Rpi.StockEvent;

public class Application extends JFrame {
	HashMap<String, Integer> data;
	Object[] keyArray;
	Object[] valueArray;
	JList keyList;
	JTextField priceField;
	JSplitPane p;
	DefaultListModel keyListModel;
	// Queue<VisProt.StockEvent> q1;
	private static final long serialVersionUID = 1L;

	public Application() {
		data = new HashMap<String, Integer>();
		keyArray = data.keySet().toArray();
		keyListModel = new DefaultListModel();
		keyList = new JList(keyListModel);
		for (int i = 0; i < keyArray.length; i++)
			keyListModel.add(i, keyArray[i]);
		valueArray = new Object[500];
		for (int i = 0; i < keyArray.length; i++)
			valueArray[i] = data.get(keyArray[i]);
		priceField = new JTextField(20);
		priceField.setEditable(false);
		keyList.addListSelectionListener(new PriceSelectionListener(keyList,
				valueArray, priceField));
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		p = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, keyList, priceField);
		add(p);
		this.setVisible(true);
		this.setLocation(200, 200);
		this.setSize(600, 200);
		StockEvent k = StockEvent.newBuilder().setStockId(1234).setTimestamp(3)
				.setSeqNum(1).setPiId(1).setTradePrice(new Integer(2)).build();
		useMessage(k);
		StockEvent p = StockEvent.newBuilder().setStockId(1234).setTimestamp(3)
				.setSeqNum(3).setPiId(1).setTradePrice(new Integer(9)).build();
		useMessage(p);
		StockEvent a = StockEvent.newBuilder().setStockId(1).setTimestamp(3)
				.setSeqNum(1).setPiId(1).setTradePrice(new Integer(3)).build();
		useMessage(a);
	}

	public void useMessage(StockEvent message) {
		// TODO: Map id to name, instead of just using ID as here.
		String name = "" + message.getStockId();
		Integer price = message.getTradePrice();
		data.put(name, price);
		if (keyListModel.contains(name)) {
			valueArray[keyListModel.indexOf(name)] = price;
		} else {
			keyListModel.add(keyListModel.size(), name);
			valueArray[keyListModel.size() - 1] = price;
		}
		repaint();
	}

	// Returns earliest StockEvent from sequence of queues. Returns null if all
	// queues are empty
	public StockEvent chooseEarliest(Queue<StockEvent>[] seq) {
		int n = seq.length;
		int j = 0;
		for (int i = 0; i < n; i++) {
			if (!seq[i].isEmpty()) {
				j = Math.min(j, seq[i].peek().getTimestamp());
			}
		}
		return seq[j].poll();
	}

	@SuppressWarnings("unused")
	public static void main(String[] args) {
		Application a = new Application();
	}
}

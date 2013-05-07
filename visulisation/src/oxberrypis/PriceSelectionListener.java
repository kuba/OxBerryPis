package oxberrypis;

import javax.swing.JList;
import javax.swing.JTextField;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

public class PriceSelectionListener implements ListSelectionListener{
	JList list;
	JTextField priceField;
	Object[] valueArray;
	public PriceSelectionListener(JList list, Object[] valueArray, JTextField priceField) {
		this.list = list;
		this.valueArray = valueArray;
		this.priceField = priceField;
	}
	public void valueChanged(ListSelectionEvent e) {
		 if (e.getValueIsAdjusting() == false) {
		        if (list.getSelectedIndex() != -1) {
		        	priceField.setText(valueArray[list.getSelectedIndex()].toString());
		        }
		    }
	}

}

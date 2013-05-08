package oxberrypis;

import java.awt.Dimension;

import javax.swing.BoxLayout;
import javax.swing.JFormattedTextField;
import javax.swing.JPanel;

public class StockView extends JPanel {
	private static final long serialVersionUID = 1L;
	private Stock stock;
	private JFormattedTextField[] ftf;
	private String[] des;
	private JPanel[] borderPanels;
	public StockView(Stock stock) {
		this.stock = stock;
		ftf = new JFormattedTextField[4];
		borderPanels = new JPanel[ftf.length];
		des = new String[ftf.length];
	    des[0] = "Name";
	    des[1] = "Last Trade Price";
	    des[2] = "Median";
	    des[3] = "Difference";
	    for (int i = 0; i<ftf.length; i++) {
	    	ftf[i] = getRight(i);
	    }
	    setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));
	    for (int j = 0; j < ftf.length; j += 1) {
	      JPanel borderPanel = new JPanel(new java.awt.BorderLayout());
	      borderPanels[j] = borderPanel;
	      ftf[j].setEditable(false);
	      borderPanel.setBorder(new javax.swing.border.TitledBorder(des[j]));
	      borderPanel.add(ftf[j], java.awt.BorderLayout.CENTER);
	      add(borderPanel);
	    }
	    setPreferredSize(new Dimension(120,300)); //TODO: Sort out sizing
	}
	
	public void change() {
		for (int j = 0; j<ftf.length; j+=1) {
			borderPanels[j].remove(ftf[j]);
			ftf[j] = getRight(j);
			ftf[j].setEditable(false);
			borderPanels[j].add(ftf[j], java.awt.BorderLayout.CENTER);
		}
		repaint();
	}
	
	public JFormattedTextField getRight(int j) {
		if(j==0) return new JFormattedTextField(stock.getStockName());
		else if(j==1) return new JFormattedTextField(stock.getLastTradePrice());
		else if(j==2) return new JFormattedTextField((stock.getTopBuyPrice()+stock.getTopSellPrice())/2);
		else return new JFormattedTextField(stock.getTopSellPrice()-stock.getTopBuyPrice());
	}
}

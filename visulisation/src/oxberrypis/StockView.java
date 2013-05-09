package oxberrypis;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;

import javax.swing.BoxLayout;
import javax.swing.JFormattedTextField;
import javax.swing.JLabel;
import javax.swing.JPanel;

/**
 * The cell of a stock in the visualisation, showing name, last trade price, average trade price, sell/buy difference
 * and coloured according to change in trade price
 */
public class StockView extends JPanel {
	private static final long serialVersionUID = 1L;
	private Stock stock;
	private JFormattedTextField[] ftf;
	private String[] des;
	private JPanel[] borderPanels;
	
	/**
	 * Creates a panel describing the stock's last trade price, average trade price, sell/buy difference, and presents 
	 * it with a changing colour according to the change in last trade price
	 * @param stock
	 */
	public StockView(Stock stock) {
		this.stock = stock;
		ftf = new JFormattedTextField[3];
		borderPanels = new JPanel[ftf.length];
		des = new String[ftf.length];
	    des[0] = "Last Trade Price";
	    des[1] = "Average Trade Price";
	    des[2] = "Sell/Buy Difference";
	    for (int i = 0; i<ftf.length; i++) {
	    	ftf[i] = new JFormattedTextField(getRight(i));
	    }
	    setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));
	    JLabel nameLabel = new JLabel(stock.getStockName());
	    nameLabel.setFont(new Font("Arial", Font.BOLD, 24));
	    nameLabel.setAlignmentX(JLabel.CENTER_ALIGNMENT);
	    add(nameLabel);
	    for (int j = 0; j < ftf.length; j += 1) {
	      JPanel borderPanel = new JPanel(new java.awt.BorderLayout());
	      borderPanels[j] = borderPanel;
	      ftf[j].setEditable(false);
	      borderPanel.setBorder(new javax.swing.border.TitledBorder(des[j]));
	      borderPanel.add(ftf[j], java.awt.BorderLayout.CENTER);
	      add(borderPanel);
	    }
	    setOpaque(true);
	    setBackground(colorChoice());
	    setPreferredSize(new Dimension(120,200));
	}
	
	/**
	 * Chooses the correct colour according to the price change
	 * @return Red, green or yellow appropriately
	 */
	public Color colorChoice() {
		if(stock.getChange()==-1) return new Color(252,68,39);
		if(stock.getChange()==0) return new Color(239,222,72);
		else return new Color(85,220,64);
	}
	
	/**
	 * Updates all fields according to if the stock has changed anything, and repaints the panel
	 */
	public void change() {
		for (int j = 0; j<ftf.length; j+=1) {
			ftf[j].setText(getRight(j));
		}
		setBackground(colorChoice());
		repaint();
	}
	
	/**
	 * Return the jth field value
	 * @param j = 0, 1 or 2 for the three fields
	 * @return a new field with the correct data
	 */
	public String getRight(int j) {
		double k = Math.pow(10,stock.getDenomPower());
		if(j==0) return "$"+(stock.getLastTradePrice()/k);
		else if(j==1) return "$"+((stock.getTopBuyPrice()+stock.getTopSellPrice())/(2*k));
		else return "$"+((stock.getTopSellPrice()-stock.getTopBuyPrice())/k);
	}
}

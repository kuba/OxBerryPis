package oxberrypis;

/**
 * A single Stock.
 * 
 * Contains name, last trade price, top buy/sell prices.
 * 
 */
public class Stock {
	private String stockName;
	
	private int lastTradePrice;
	private int topBuyPrice;
	private int topSellPrice;
	
	private int denomPower;
	
	private boolean hasLastTradePrice;
	private boolean hasTopBuyPrice;
	private boolean hasTopSellPrice;
	
	public enum Change {
		UP,
		DOWN,
		NO_CHANGE,
	}
	
	private Change change;
	
	public Stock(String stockName, int denomPower) {
		this.stockName = stockName;
		this.denomPower = denomPower;
		this.change = Change.NO_CHANGE;
		
		this.hasLastTradePrice = false;
		this.hasTopBuyPrice = false;
		this.hasTopSellPrice = false;
	}
	
	/**
	 * Update if either of these are given in a message.
	 * 
	 * @param newTopBuyPrice
	 * @param newTopSellPrice
	 */
	public void update(Integer newTopBuyPrice, Integer newTopSellPrice) { 
		if (newTopBuyPrice != null) {
			topBuyPrice = newTopBuyPrice;
			hasTopBuyPrice = true;
		}
		else {
			hasTopBuyPrice = false;
		}
		
		if (newTopSellPrice != null) {
			topSellPrice = newTopSellPrice;
			hasTopSellPrice = true;
		}
		else {
			hasTopSellPrice = false;
		}
	}
	
	/**
	 * Update if last trade price is given.
	 * 
	 * @param newLastTradePrice
	 * @param newTopBuyPrice
	 * @param newTopSellPrice
	 */
	public void update(int newLastTradePrice, Integer newTopBuyPrice, Integer newTopSellPrice) {
		if (!hasLastTradePrice || lastTradePrice == newLastTradePrice)
			change = Change.NO_CHANGE;
		else if (lastTradePrice < newLastTradePrice)
			change = Change.UP;
		else
			change = Change.DOWN;
		
		lastTradePrice = newLastTradePrice;
		hasLastTradePrice = true;
		
		update(newTopBuyPrice, newTopSellPrice);
	}
	
	public String getStockName() {
		return stockName;
	}
	
	public int getLastTradePrice() {
		return lastTradePrice;
	}
	
	public int getTopBuyPrice() {
		return topBuyPrice;
	}
	
	public int getTopSellPrice() {
		return topSellPrice;
	}
	
	public Change getChange() {
		return change;
	}
	
	public int getDenomPower() {
		return denomPower;
	}
	
	public boolean hasLastTradePrice() {
		return hasLastTradePrice;
	}
	
	public boolean hasTopBuyPrice() {
		return hasTopBuyPrice;
	}
	
	public boolean hasTopSellPrice() {
		return hasTopSellPrice;
	}
}
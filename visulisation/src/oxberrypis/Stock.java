package oxberrypis;

public class Stock {
	private String stockName;
	private int last_Trade_Price;
	private int top_Buy_Price;
	private int top_Sell_Price;
	private int denomPower;
	private boolean hasLastTradePrice;
	private boolean hasTopBuyPrice;
	private boolean hasTopSellPrice;
	private int change; // -1 means down, 0 no change, 1 up
	
	public Stock(String stockName, int denomPower) {
		this.stockName = stockName;
		this.denomPower = denomPower;
		this.change = 0;
		this.hasLastTradePrice=false;
		this.hasTopBuyPrice=false;
		this.hasTopSellPrice=false;
	}
	
	public void update(Integer top_Buy_Price, Integer top_Sell_Price) { 
		if(top_Buy_Price!=null) {
			this.top_Buy_Price = top_Buy_Price;
			this.hasTopBuyPrice = true;
		}
		else {
			this.hasTopBuyPrice = false;
		}
		if(top_Sell_Price!=null) {
			this.top_Sell_Price = top_Sell_Price;
			this.hasTopSellPrice = true;
		}
		else {
			this.hasTopSellPrice = false;
		}
	}
	
	public void update(int last_Trade_Price, Integer top_Buy_Price, Integer top_Sell_Price) {
		if(!hasLastTradePrice || this.last_Trade_Price==last_Trade_Price) change = 0;
		else if(this.last_Trade_Price<last_Trade_Price) change = 1; 
		else change = 1;
		this.last_Trade_Price = last_Trade_Price;
		this.hasLastTradePrice = true;
		update(top_Buy_Price, top_Sell_Price);
	}
	
	public String getStockName() {
		return stockName;
	}
	
	public int getLastTradePrice() {
		return last_Trade_Price;
	}
	
	public int getTopBuyPrice() {
		return top_Buy_Price;
	}
	
	public int getTopSellPrice() {
		return top_Sell_Price;
	}
	
	public int getChange() {
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

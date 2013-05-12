package oxberrypis;

import oxberrypis.net.proto.rpi.Rpi.StockEvent;


public interface StockDataProvider {
	
	/**
	 * Get stock name.
	 * 
	 * @param stockId	Stock id (SymbolIndex).
	 * @return			Name of the stock.
	 */
	public String getName(int stockId);
	
	/**
	 * Get denominator power.
	 * 
	 * @param stockId	Stock id (SymbolIndex).
	 * @return			Stock's denominator power.
	 */
	public int getDenomPower(int stockId);
	
	/**
	 * Receive next stock event.
	 * 
	 * @return	Next stock event available.
	 */
	public StockEvent getNextStockEvent();
	
}
package oxberrypis;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import oxberrypis.net.proto.controller.Controller.SetupVisualisation;
import oxberrypis.net.proto.controller.Controller.SetupVisualisation.SymbolMapping;
import oxberrypis.net.proto.controller.Controller.SetupVisualisation.SymbolRange;
import oxberrypis.net.proto.rpi.Rpi.StockEvent;

/**
 * Stock data provider with stock events yielded in order they are received.
 * 
 * @author Jakub Warmuz
 *
 */
public class UnorderedStockEvents implements StockDataProvider {
	
	private NetworkPis network;
	
	private Map<Integer, String> stockNames = new HashMap<Integer, String>();
	private Map<Integer, Integer> denomPowers = new HashMap<Integer, Integer>();
	
	public UnorderedStockEvents(NetworkPis network) {
		this.network = network;
		
		SetupVisualisation setupVisualisation = network.getInit();
		List<SymbolRange> ranges = setupVisualisation.getRangeList();
		
		for (SymbolRange range: ranges) {
			List<SymbolMapping> mappings = range.getMappingList();
			
			for (SymbolMapping mapping: mappings) {
				int stockId = mapping.getSymbolIndex();
				stockNames.put(stockId, mapping.getSymbol());
				denomPowers.put(stockId, mapping.getPriceScaleCode());
			}
		}
	}

	@Override
	public String getName(int stockId) {
		return stockNames.get(stockId);
	}

	@Override
	public int getDenomPower(int stockId) {
		return denomPowers.get(stockId);
	}

	@Override
	public StockEvent getNextStockEvent() {
		return network.getNextStockEvent();
	}

}

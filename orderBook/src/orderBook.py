
# represents a single order
class Order:
  def __init__(self, orderId, shares, limit,nextElem,prevElem):
    self.orderId = orderId
    self.shares = shares
    self.limit = limit
    self.nextElem = nextElem
    self.prevElem = prevElem
  # remove the order from the list
  def remove(self):
    if ((self.prevElem is None) and (self.nextElem is None)):
      # we are the last element so remove the limit as well. Uncomment the follwing if
      # we don't remove the limit
      #self.limit.headorder = None
      #self.limit.tailorder = None
      self.limit.remove()
    elif (self.prevElem is None):
      # just remove us (we must be at the head of the queue)
      self.limit.headorder = self.nextElem
      self.nextElem.prevElem = None
    elif (self.nextElem is None):
      # we are at the tail
      self.limit.tailOrder = self.prevElem
      self.prevElem.nextElem = None
    else:
      # we are in the morderIddle so 
      self.prevElem.nextElem = self.prevElem
      self.nextElem.prevElem = self.nextElem

 
      
# represents a limit price
class Limit:
  def __init__(self, price, book, headOrder, tailOrder, nextElem, prevElem):
    self.price = price
    self.headOrder = headOrder
    self.tailOrder = tailOrder
    self.nextElem = nextElem
    self.prevElem = prevElem
    self.book = book
  def remove(self):
    # remove ourselves (we are in a stack with a dummy header
    self.prevElem.nextElem = self.nextElem
    if ((self.nextElem is not None)) :
      self.nextElem.prevElem = self.prevElem

    #find ourselves in the map and remove
    if (self.price in self.book.sellLimits):
      del self.book.sellLimits[self.price] 
    elif (self.price in self.book.buyLimits):
      del self.book.buyLimits[self.price] 

  def add(self,orderId,price,amount):
    # add an order at the tail
    x = self.tailOrder 
    o = Order(orderId,amount,self,None,x)
    if (x is None):
      self.headOrder = o
    else :
      x.nextElem = o
    self.tailOrder = o
    return o

# represents a book of limits for a single share price
class limitBook:
  def __init__(self):
    self.buyLimits = {}
    self.sellLimits = {}
    self.buyOrders = {}
    self.sellOrders = {}
    self.buyFront = Limit(0,None,None,None,None,None)  # dummy headers
    self.sellFront = Limit(0,None,None,None,None,None)
  # add a sell order 
  def addBuy(self,price,amount,orderId):
    self.addOrder(self.buyLimits,self.buyFront,self.buyOrders,price,amount,orderId)
  # add a buy order
  def addSell(self,price,amount,orderId):
    self.addOrder(self.sellLimits,self.sellFront,self.sellOrders,price,amount,orderId)

  def execute(self):
    buy = self.buyFront.nextElem
    sell = self.sellFront.nextElem
    lastsell = 0
    amount = 0
    while(buy != None and sell != None and buy.price >= sell.price):
       lastsell = sell.price
       buyOrder = buy.headOrder
       sellOrder = sell.headOrder
       if (buyOrder.shares == sellOrder.shares):                                
          amount += buyOrder.shares
          self.removeOrder(buyOrder.orderId)
          self.removeOrder(sellOrder.orderId)
          
       elif (buyOrder.shares < sellOrder.shares):
          amount += buyOrder.shares
          sellOrder.shares -= buyOrder.shares
          self.removeOrder(buyOrder.orderId)
       else:
          amount += sellOrder.shares
          buyOrder.shares -=sellOrder.shares
          self.removeOrder(sellOrder.orderId)
       buy = self.buyFront.nextElem
       sell = self.sellFront.nextElem
    return (lastsell,amount)

  # remove an order (of any type as the messages can't tell which type it is)
  def removeOrder(self,orderId):
    if (orderId in self.buyOrders):
      self.buyOrders[orderId].remove()
      del  self.buyOrders[orderId]

    elif (orderId in self.sellOrders):
      self.sellOrders[orderId].remove()
      del  self.sellOrders[orderId]
    else :
      raise Exception('No Such Order:' + str(orderId))
  # add an order (paramterised by specifics)
  def addOrder(self,limits,front,orders,price,amount,orderId):
    if (price in limits) :  
    #if the limit exists get it from the map
      limit = limits[price]
    else:
    # otherwise find a postion and create a new limit
      a = self.searchListFrom(front,price)
      limit = Limit(price,self,None,None,a.nextElem,a)
      a.nextElem = limit
      if ( limit.nextElem is not None):
        limit.nextElem.prevElem = limit

    o  = limit.add(orderId,price,amount)
    orders[orderId] = o
  # simple search
  def searchListFrom(self,y,price):
    x = y
    while (x.nextElem is not None  and  x.nextElem.price < price):
      x = x.nextElem
    return x


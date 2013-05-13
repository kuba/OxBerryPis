Group report
============

.. image:: ../network.png
   :alt: Network diagram.


Network
-------

We used `Protocol Buffers
<https://developers.google.com/protocol-buffers/>`_ to serialize data.
They were very easy and allowed us to define messages and serialize it
easily and cross language barriers. They generated source files in the
given language. This meant that we had an interface consistent with the
language and with type safety.

Using `ZMQ <http://www.zeromq.org/>`_ helped as it meant it was easier
to define channels and connect them than to use something like native
sockets. It did cause a few problems with synchronisation as the socket
type we used would start sending data before any of the RaspberryPis
were connected. This meant that packets were lost. We fixed by sending
messages back telling the parser when to start to send data.

The connection between the RaspberryPis and the parser had top be
ordered at the parser end due differences in speed between RaspberryPis
and different parsers.  This was complicated. In the end we went for a
design which was not perfect at ordering. As the visualisation is viewed
by people differences in time between stocks on the order of a second
should not be noticed and so we decided that was better.


Order Book
----------

The :py:mod:`order book <oxberrypis.orderbook>` is the main processing
code that runs on Raspberry Pis.  The order book module consists of two
books classes one for demand and one for supply. :py:class:`The book
<oxberrypis.orderbook.book.OrderBook>` keeps all the orders and allows
changing them as well as querying for orders either by id or for the
currently best order. Order book keeps a set of limit books for each
limit price that is present. This seems natural since there will be lots
of orders for a single price and some update orders can move order to
the end of queue for the price. Each limit book the keeps orders at this
price in first come first serve basis.

The whole book class is very modular and it can be connected with any
collection for limit books as well as for structures. We choose to pick
:py:mod:`Finacci heap <oxberrypis.orderbook.fibonacci_heap>` to store
limit prices and :py:mod:`Doubly linked list
<oxberrypis.orderbook.linked_list>` for individual orders for a single
limit price. For limit prices we need to very efficiently add element
and query for smallest element, also reasonably fast remove any element.
Fibonacci heap allows the first two in O(1) and the second two in O(log
N). For orders at a single limit price, the operations are the same,
except we only add elements at the beginning or the end, doubly linked
lists are perfect for this allowing all operations in O(1).

The :py:class:`matching engine class
<oxberrypis.orderbook.matching_engine.MatchingEngine>` is the class that
implements trading logic. It implements the rules of which order has a
priority, in which cases changing the order loses its position in queue,
what will be the price when there is larger interval of agreement.
Matching engine is also a public interface for other modules to use.


Visualisation
-------------

.. image:: ../visualisation.png
   :width: 50%
   :alt: Visualisation screenshot.

The visualisation section was implemented in Java, meaning that we made
use of the `Protocol Buffers
<https://developers.google.com/protocol-buffers/>`_ to switch from the
Python code to the Java. The only one that was used for visualisation
was ``StockEvent``, which provided a stock id, information on what
channel it came from, sequence number which allowed to detect duplicates
(produced due to the high availability model we used), along with
optionally the last trade price, top buy price and top sell price.

A stock was given its own class, containing the stock name, last trade
price, top buy price and top sell price. The stock name was obtained
from a map sent from the parser, taking stock id to stock name. Each
time a ``StockEvent`` came through, if the stock was already in the map,
it was updated, otherwise it was added to the map.

The actual visual part of the project was written using Java Swing. A
scrollable grid of each stock is shown, along with its last trade price,
the average of its top buy and top sell prices, and the difference
between the top buy and top sell prices. Each time a new trade price
comes in, it is compared with the previous one and the cell of the stock
changes colour depending on if the price went up, down or stayed the
same.

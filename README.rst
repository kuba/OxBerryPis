About
=====

"Project A: Resilient and Rapid Raspberries" is Group Design Practical
set by the `Department of Computer Science at the University of Oxford
<http://www.cs.ox.ac.uk>`_ in the academic year 2012/2013. OxBerryPis
is an implementation of the practical maintained by 4 university
students (Group 8).

Design Brief
------------

In today's world of high frequency trading, understanding the rapidly
changing quotes from a myriad of trading algorithms is a colossal data
processing problem. With tens of thousands of updated per second in a
single market, and limited space and power constraints, it is important
to be able to maximise throughput and resiliency with the hardware
available. Given a day of actual stock exchange data, your challenge is
to create a cluster to process and aggregate the data. Doing this with
real hardware is more fun - we can't give you our data centre, but we
can suppy you with a Raspberry Pi cluster.

Project details
---------------

The idea of the project is that, given a day of stock exchange data, we
must parse it to retrieve the useful information, consisting of buying,
selling, and various trade orders. This will then be sent to the cluster
of Raspberry Pis that we have, which will maintain a data structure
called the Order Book, which will keep track of the various offers to
buy and sell for different prices, how many of each stock are being
sold, and allowing the trades to occur according to the data given,
maintaining the order book and keeping it up to date. From this, certain
data will be sent back to the computer, which will then implement some
visualisation so as to show various things about each product, such as
last trade price, various medians, and so on. An optional suggestion
from GResearch was to implement high availability in the cluster, so as
to allow the pis to redistribute the work if one or more were to fail,
without data loss.

Team members
============

* Hynek Jemelik
* Josh Peaker
* Alexander Eyers-Taylor
* Jakub Warmuz

Development
===========

Please follow the guidelines from `PEP8
<http://www.python.org/dev/peps/pep-0008>`_ (4 spaces for indentation!).
If still in doubt, apply the coding style from the master branch.
Remember to include appropriate tests.

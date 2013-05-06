"""Fibonacci Heap implementation.

Fibonacci heaps are especially desirable when the number of
`extract_min` and `delete` operations is small relative to the
number of other operations performed.

"""


class FibonacciHeapNode(object):
    """Fibonacci heap node."""
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.refresh()

    def refresh(self):
        self.degree = 0
        self.parent = None
        self.child = None
        self.left = self
        self.right = self
        self.mark = False


class FibonacciHeap(object):
    """Fibonacci heap."""

    def __init__(self):
        self.minimum = None
        self.n = 0

    def is_empty(self):
        """Check if the heap is empty."""
        return self.n == 0

    def insert(self, node):
        """Insert a node into the heap."""
        node.refresh()

        if self.minimum is None:
            self.minimum = node
        else:
            w = self.minimum.left
            y = self.minimum
            node.left = w
            node.right = y
            w.right = node
            y.left = node
            if node.key < self.minimum.key:
                self.minimum = node

        self.n = self.n + 1

    def extract(self):
        """Extract minimum node from the heap."""
        node = self.minimum
        if node is not None:
            if node.child is not None:
                self._add_list(node.child, node)
            node.left.right = node.right
            node.right.left = node.left
            if node == node.right:
                self.minimum = None
            else:
                self.minimum = node.right
                self._consolidate()
            self.n = self.n - 1
            node.refresh()
        return node

    def decrease_key(self, node, new_key):
        """Decrease node's key."""
        assert(new_key <= node.key)
        if new_key == node.key:
            return
        node.key = new_key
        y = node.parent
        if y is not None and node.key < y.key:
            self._cut(self, node, y)
            self._cascading_cut(self, y)
        if node.key < self.minimum.key:
            self.minimum = node

    def _cut(self, x, y):
        # remove x from the child list of y, decrementing y.degree.
        x.left.right = x.right
        x.right.left = x.left
        y.degree = y.degree - 1
        y.child = x.right
        if x == x.right:
            y.child = None
        # add x to the root list of self
        x.parent = None
        x.mark = False
        x.left = self.minimum.left
        x.right = self.minimum
        x.left.right = x
        x.right.left = x
        #self._add_list(x, self.minimum)

    def _cascading_cut(self, y):
        z = y.parent
        if z is not None:
            if y.mark == False:
                y.mark = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)

    def _add_list(self, y, x):
        """Add list y to x."""
        if y is None or x is None:
            return
        z = y
        while z.right != y:
            z.parent = x.parent
            z = z.right
        z.parent = x.parent
        y.left = x.left
        x.left.right = y
        z.right = x
        x.left = z

    def _union(self, H2):
        H = FibonacciHeap()
        if self.minimum is not None and H2.minimum is None:
            H.minimum = self.minimum
            H.n = self.n
        elif self.minimum is None and H2.minimum is not None:
            H.minimum = H2.minimum
            H.n = H2.n
        elif self.minimum is not None and H2.minimum is not None:
            self._add_list(H2.minimum, self.minimum)
            if self.minimum.key <= H2.minimum.key:
                H.minimum = self.minimum
            else:
                H.minimum = H2.minimum
            H.n = self.n + H2.n
        return H

    def __add__(self, other):
        return self._union(other)

    def _torange(self, a, b, step=1):
        return xrange(a, b+1, step)

    def _consolidate(self):
        max_degree = self._max_degree(self.n)
        A = []
        for i in self._torange(0, max_degree):
            A.append(None)
        root_list = []
        x = self.minimum
        x.left.right = None
        while x is not None:
            next_x = x.right
            x.left = x
            x.right = x
            root_list.append(x)
            x = next_x
        for x in root_list:
            d = x.degree
            #print "index=", d, "max_degree=", max_degree, "self.n=",self.n
            while A[d] is not None:
                y = A[d]
                if y.key < x.key:
                    x,y = y,x
                self._link(y, x)
                A[d] = None
                d = d + 1
            A[d] = x
        self.minimum = None
        for x in A:
            if x is not None:
                x.left = x
                x.right = x
                x.parent = None
                if self.minimum is None:
                    self.minimum = x
                else:
                    self._add_list(x, self.minimum)
                    if x.key < self.minimum.key:
                        self.minimum = x

    def _max_degree(self, n):
        """floor(lg(n))"""
        lg = 0
        while n/2 > 0:
            lg = lg + 1
            n = n / 2
        return lg

    def _link(self, y, x):
        y.left.right = y.right
        y.right.left = y.left
        y.parent = x
        if x.child is not None:
            x.child.left.right = y
            y.left = x.child.left
            y.right = x.child
            x.child.left = y
        else:
            x.child = y
            y.left = y
            y.right = y
        x.degree = x.degree + 1
        y.mark = False

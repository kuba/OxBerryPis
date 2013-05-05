"""Linked lists implementation.

Created on Apr 28, 2013

.. codeauthor:: Hynek Jemelik

"""


class LinkedListNode(object):
    def __init__(self, data):
        self.prev = None
        self.next = None
        self.data = data


class LinkedList(object):
    def __init__(self):
        self.first = None
        self.last = None
        self.size = 0

    def is_empty(self):
        return self.size <= 0

    def append_node(self, node):
        prev_node = self.last
        if prev_node is not None:
            prev_node.next = node
        node.prev = prev_node
        if self.first is None:
            self.first = node
        self.last = node
        self.size += 1

    def append_value(self, data):
        node = LinkedListNode(data)
        self.append_node(node)
        return node

    def remove_node(self, node):
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None:
            prev_node.next = next_node
        if next_node is not None:
            next_node.prev = prev_node
        if self.first is node:
            self.first = next_node
        if self.last is node:
            self.last = prev_node
        self.size -= 1

    def get_first_value(self):
        return self.first.data

    def extract_first_value(self):
        node = self.first
        self.remove_node(node)
        return node.data

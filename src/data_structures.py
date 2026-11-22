"""
data_structures.py - Part 2: Elementary data structures, built from scratch

Contents
--------
DynamicArray      - resizable array: access, insert, delete
Matrix            - 2-D matrix stored row-major in one flat array
ArrayStack        - stack (LIFO) on an array
ArrayQueue        - queue (FIFO) on a circular array
SinglyLinkedList  - singly linked list: insert, delete, search, traverse
LinkedStack       - stack on linked nodes (for the array-vs-list comparison)
LinkedQueue       - queue on linked nodes (for the array-vs-list comparison)
RootedTree        - rooted tree using linked nodes
                    (left-child, right-sibling representation) [optional part]

"From scratch" rule
-------------------
Python's built-in list already does everything a dynamic array does, so to
show how an array really works, the classes below only use a Python list as a
FIXED block of memory: it is created once with a set size ([None] * capacity)
and is only ever read or written by index. Growing the array means allocating
a new, bigger block and copying - exactly what happens in C or Java.
"""


# ---------------------------------------------------------------------------
# Low-level helper: a fixed-size block of memory
# ---------------------------------------------------------------------------

def _new_block(capacity):
    """Return a fixed-size block of `capacity` empty slots."""
    return [None] * capacity


# ---------------------------------------------------------------------------
# Arrays
# ---------------------------------------------------------------------------

class DynamicArray:
    """
    A resizable array.

    Operation            Time
    -------------------  ---------------------------------------------
    get(i) / set(i, x)   O(1)  - direct index into the block
    append(x)            O(1) amortized (O(n) on the rare resize)
    insert(i, x)         O(n - i)  - later elements shift right
    delete(i)            O(n - i)  - later elements shift left
    find(x)              O(n)

    The capacity doubles when full and halves when only 1/4 full, so the
    total cost of any sequence of m appends/deletes is O(m) (amortized O(1)).
    """

    def __init__(self, capacity=4):
        self._capacity = max(1, capacity)
        self._data = _new_block(self._capacity)
        self._size = 0

    def __len__(self):
        return self._size

    def _check_index(self, i):
        if not 0 <= i < self._size:
            raise IndexError(f"index {i} out of range for size {self._size}")

    def _resize(self, new_capacity):
        new_data = _new_block(new_capacity)
        for i in range(self._size):          # copy every element: O(n)
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    def get(self, i):
        """Access the element at index i. O(1)."""
        self._check_index(i)
        return self._data[i]

    def set(self, i, value):
        """Overwrite the element at index i. O(1)."""
        self._check_index(i)
        self._data[i] = value

    def append(self, value):
        """Add to the end. Amortized O(1)."""
        if self._size == self._capacity:
            self._resize(2 * self._capacity)
        self._data[self._size] = value
        self._size += 1

    def insert(self, i, value):
        """Insert value at index i (0 <= i <= size), shifting later items right. O(n)."""
        if not 0 <= i <= self._size:
            raise IndexError(f"insert index {i} out of range for size {self._size}")
        if self._size == self._capacity:
            self._resize(2 * self._capacity)
        for j in range(self._size, i, -1):   # shift right, starting from the end
            self._data[j] = self._data[j - 1]
        self._data[i] = value
        self._size += 1

    def delete(self, i):
        """Remove and return the element at index i, shifting later items left. O(n)."""
        self._check_index(i)
        value = self._data[i]
        for j in range(i, self._size - 1):   # shift left
            self._data[j] = self._data[j + 1]
        self._data[self._size - 1] = None    # clear the old last slot
        self._size -= 1
        if 0 < self._size <= self._capacity // 4 and self._capacity > 4:
            self._resize(self._capacity // 2)
        return value

    def find(self, value):
        """Return the first index holding value, or -1. O(n)."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1

    def to_list(self):
        return [self._data[i] for i in range(self._size)]

    def __repr__(self):
        return f"DynamicArray({self.to_list()})"


class Matrix:
    """
    A rows x cols matrix stored in ONE flat block in row-major order:
    element (r, c) lives at position r * cols + c. This is how C and NumPy
    lay out 2-D arrays, and it keeps access O(1).

    Operation                       Time
    ------------------------------  -------------------
    get(r, c) / set(r, c, x)        O(1)
    insert_row / delete_row         O(rows * cols)  (block is rebuilt)
    insert_column / delete_column   O(rows * cols)
    add(other)                      O(rows * cols)
    multiply(other)                 O(rows * cols * other.cols)
    transpose()                     O(rows * cols)
    """

    def __init__(self, rows, cols, fill=0):
        if rows < 0 or cols < 0:
            raise ValueError("rows and cols must be non-negative")
        self.rows = rows
        self.cols = cols
        self._data = _new_block(rows * cols)
        for i in range(rows * cols):
            self._data[i] = fill

    @classmethod
    def from_lists(cls, rows_list):
        """Build a Matrix from a list of equal-length lists."""
        r = len(rows_list)
        c = len(rows_list[0]) if r else 0
        m = cls(r, c)
        for i in range(r):
            if len(rows_list[i]) != c:
                raise ValueError("all rows must have the same length")
            for j in range(c):
                m.set(i, j, rows_list[i][j])
        return m

    def _check(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError(f"({r}, {c}) out of range for {self.rows}x{self.cols} matrix")

    def get(self, r, c):
        self._check(r, c)
        return self._data[r * self.cols + c]

    def set(self, r, c, value):
        self._check(r, c)
        self._data[r * self.cols + c] = value

    def insert_row(self, index, row_values):
        """Insert a new row before `index` (0..rows)."""
        if not 0 <= index <= self.rows:
            raise IndexError("row index out of range")
        if len(row_values) != self.cols:
            raise ValueError(f"row must have {self.cols} values")
        new_data = _new_block((self.rows + 1) * self.cols)
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if r < index:
                    new_data[r * self.cols + c] = self._data[r * self.cols + c]
                elif r == index:
                    new_data[r * self.cols + c] = row_values[c]
                else:
                    new_data[r * self.cols + c] = self._data[(r - 1) * self.cols + c]
        self._data = new_data
        self.rows += 1

    def delete_row(self, index):
        """Remove the row at `index` and return its values."""
        if not 0 <= index < self.rows:
            raise IndexError("row index out of range")
        removed = [self._data[index * self.cols + c] for c in range(self.cols)]
        new_data = _new_block((self.rows - 1) * self.cols)
        k = 0
        for r in range(self.rows):
            if r == index:
                continue
            for c in range(self.cols):
                new_data[k] = self._data[r * self.cols + c]
                k += 1
        self._data = new_data
        self.rows -= 1
        return removed

    def insert_column(self, index, col_values):
        """Insert a new column before `index` (0..cols)."""
        if not 0 <= index <= self.cols:
            raise IndexError("column index out of range")
        if len(col_values) != self.rows:
            raise ValueError(f"column must have {self.rows} values")
        new_cols = self.cols + 1
        new_data = _new_block(self.rows * new_cols)
        for r in range(self.rows):
            for c in range(new_cols):
                if c < index:
                    new_data[r * new_cols + c] = self._data[r * self.cols + c]
                elif c == index:
                    new_data[r * new_cols + c] = col_values[r]
                else:
                    new_data[r * new_cols + c] = self._data[r * self.cols + c - 1]
        self._data = new_data
        self.cols = new_cols

    def delete_column(self, index):
        """Remove the column at `index` and return its values."""
        if not 0 <= index < self.cols:
            raise IndexError("column index out of range")
        removed = [self._data[r * self.cols + index] for r in range(self.rows)]
        new_cols = self.cols - 1
        new_data = _new_block(self.rows * new_cols)
        k = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if c != index:
                    new_data[k] = self._data[r * self.cols + c]
                    k += 1
        self._data = new_data
        self.cols = new_cols
        return removed

    def add(self, other):
        if (self.rows, self.cols) != (other.rows, other.cols):
            raise ValueError("matrices must have the same shape to add")
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows * self.cols):
            result._data[i] = self._data[i] + other._data[i]
        return result

    def multiply(self, other):
        if self.cols != other.rows:
            raise ValueError("left matrix columns must equal right matrix rows")
        result = Matrix(self.rows, other.cols)
        for i in range(self.rows):
            for j in range(other.cols):
                total = 0
                for k in range(self.cols):
                    total += self.get(i, k) * other.get(k, j)
                result.set(i, j, total)
        return result

    def transpose(self):
        result = Matrix(self.cols, self.rows)
        for r in range(self.rows):
            for c in range(self.cols):
                result.set(c, r, self.get(r, c))
        return result

    def to_lists(self):
        return [[self.get(r, c) for c in range(self.cols)] for r in range(self.rows)]

    def __repr__(self):
        return f"Matrix({self.to_lists()})"


# ---------------------------------------------------------------------------
# Stacks and queues on arrays
# ---------------------------------------------------------------------------

class ArrayStack:
    """
    Last-in, first-out stack on an array. The top of the stack is the last
    used slot, so push and pop never shift anything.

    push   O(1) amortized (doubling resize)
    pop    O(1) amortized
    peek   O(1)
    """

    def __init__(self, capacity=4):
        self._capacity = max(1, capacity)
        self._data = _new_block(self._capacity)
        self._top = 0                       # number of items = index of next free slot

    def __len__(self):
        return self._top

    def is_empty(self):
        return self._top == 0

    def _resize(self, new_capacity):
        new_data = _new_block(new_capacity)
        for i in range(self._top):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    def push(self, value):
        if self._top == self._capacity:
            self._resize(2 * self._capacity)
        self._data[self._top] = value
        self._top += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")   # stack underflow
        self._top -= 1
        value = self._data[self._top]
        self._data[self._top] = None
        if 0 < self._top <= self._capacity // 4 and self._capacity > 4:
            self._resize(self._capacity // 2)
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[self._top - 1]


class ArrayQueue:
    """
    First-in, first-out queue on a CIRCULAR array. `head` is the index of
    the front item; the back is at (head + size) % capacity. Both ends move
    forward and wrap around, so dequeue never shifts elements.
    (A naive array queue that removes from index 0 would cost O(n) per
    dequeue because every element shifts left.)

    enqueue  O(1) amortized
    dequeue  O(1) amortized
    peek     O(1)
    """

    def __init__(self, capacity=4):
        self._capacity = max(1, capacity)
        self._data = _new_block(self._capacity)
        self._head = 0
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        new_data = _new_block(new_capacity)
        for i in range(self._size):                     # unwrap into order
            new_data[i] = self._data[(self._head + i) % self._capacity]
        self._data = new_data
        self._capacity = new_capacity
        self._head = 0

    def enqueue(self, value):
        if self._size == self._capacity:
            self._resize(2 * self._capacity)
        tail = (self._head + self._size) % self._capacity
        self._data[tail] = value
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")  # queue underflow
        value = self._data[self._head]
        self._data[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        if 0 < self._size <= self._capacity // 4 and self._capacity > 4:
            self._resize(self._capacity // 2)
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._data[self._head]


# ---------------------------------------------------------------------------
# Linked lists
# ---------------------------------------------------------------------------

class Node:
    """One linked-list node: a value plus a pointer to the next node."""
    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class SinglyLinkedList:
    """
    Singly linked list with head and tail pointers.

    insert_front(x)       O(1)
    insert_back(x)        O(1)   (thanks to the tail pointer)
    insert_after(node,x)  O(1)   (when you already hold the node)
    insert_at(i, x)       O(i)   (must walk to position i)
    delete_front()        O(1)
    delete_value(x)       O(n)   (search, then unlink)
    delete_at(i)          O(i)
    search(x) / get(i)    O(n)
    traverse()            O(n)
    """

    def __init__(self, values=None):
        self.head = None
        self.tail = None
        self._size = 0
        for v in values or []:
            self.insert_back(v)

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    # --- insertion -------------------------------------------------------
    def insert_front(self, value):
        node = Node(value, self.head)
        self.head = node
        if self.tail is None:            # list was empty
            self.tail = node
        self._size += 1
        return node

    def insert_back(self, value):
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1
        return node

    def insert_after(self, node, value):
        """Insert value right after an existing node. O(1)."""
        if node is None:
            raise ValueError("node must not be None")
        new_node = Node(value, node.next)
        node.next = new_node
        if node is self.tail:
            self.tail = new_node
        self._size += 1
        return new_node

    def insert_at(self, index, value):
        """Insert so that value ends up at position `index` (0..size)."""
        if not 0 <= index <= self._size:
            raise IndexError("insert index out of range")
        if index == 0:
            return self.insert_front(value)
        if index == self._size:
            return self.insert_back(value)
        return self.insert_after(self._node_at(index - 1), value)

    # --- deletion --------------------------------------------------------
    def delete_front(self):
        if self.head is None:
            raise IndexError("delete from empty list")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return value

    def delete_value(self, value):
        """Remove the first node holding value. Returns True if found."""
        previous, current = None, self.head
        while current is not None and current.value != value:
            previous, current = current, current.next
        if current is None:
            return False
        self._unlink(previous, current)
        return True

    def delete_at(self, index):
        """Remove and return the value at position index."""
        if not 0 <= index < self._size:
            raise IndexError("delete index out of range")
        if index == 0:
            return self.delete_front()
        previous = self._node_at(index - 1)
        current = previous.next
        self._unlink(previous, current)
        return current.value

    def _unlink(self, previous, current):
        if previous is None:
            self.head = current.next
        else:
            previous.next = current.next
        if current is self.tail:
            self.tail = previous
        self._size -= 1

    # --- access ----------------------------------------------------------
    def _node_at(self, index):
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def get(self, index):
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        return self._node_at(index).value

    def search(self, value):
        """Return the index of the first node with value, or -1."""
        for i, v in enumerate(self.traverse()):
            if v == value:
                return i
        return -1

    def traverse(self):
        """Yield each value from head to tail."""
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def reverse(self):
        """Reverse the list in place. O(n) time, O(1) extra space."""
        previous, current = None, self.head
        self.tail = self.head
        while current is not None:
            nxt = current.next
            current.next = previous
            previous, current = current, nxt
        self.head = previous

    def to_list(self):
        return list(self.traverse())

    def __iter__(self):
        return self.traverse()

    def __repr__(self):
        return " -> ".join(map(str, self.traverse())) or "(empty)"


class LinkedStack:
    """Stack on linked nodes: push/pop at the head, each O(1) worst case."""

    def __init__(self):
        self._list = SinglyLinkedList()

    def __len__(self):
        return len(self._list)

    def is_empty(self):
        return self._list.is_empty()

    def push(self, value):
        self._list.insert_front(value)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._list.delete_front()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._list.head.value


class LinkedQueue:
    """Queue on linked nodes: enqueue at the tail, dequeue at the head, O(1)."""

    def __init__(self):
        self._list = SinglyLinkedList()

    def __len__(self):
        return len(self._list)

    def is_empty(self):
        return self._list.is_empty()

    def enqueue(self, value):
        self._list.insert_back(value)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._list.delete_front()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._list.head.value


# ---------------------------------------------------------------------------
# Optional: rooted tree using linked nodes (left-child, right-sibling)
# ---------------------------------------------------------------------------

class TreeNode:
    """
    A tree node with three pointers:
      parent         - the node above
      left_child     - the FIRST child
      right_sibling  - the next child of the same parent
    With only these fixed pointers, a node can have any number of children
    while using O(1) space per node.
    """
    __slots__ = ("key", "parent", "left_child", "right_sibling")

    def __init__(self, key):
        self.key = key
        self.parent = None
        self.left_child = None
        self.right_sibling = None


class RootedTree:
    """
    Rooted tree with an unlimited number of children per node.

    add_child(parent, key)   O(1)  (new child becomes the first child)
    children(node)           O(number of children)
    preorder()               O(n)
    depth(node)              O(depth)
    height()                 O(n)
    find(key)                O(n)
    """

    def __init__(self, root_key):
        self.root = TreeNode(root_key)
        self._size = 1

    def __len__(self):
        return self._size

    def add_child(self, parent, key):
        child = TreeNode(key)
        child.parent = parent
        child.right_sibling = parent.left_child   # link in front of existing children
        parent.left_child = child
        self._size += 1
        return child

    def children(self, node):
        """Return children in the order they are linked (newest first)."""
        result = []
        child = node.left_child
        while child is not None:
            result.append(child)
            child = child.right_sibling
        return result

    def preorder(self, node=None):
        """Yield keys in preorder (node, then its subtrees). Iterative, uses a stack."""
        stack = ArrayStack()
        stack.push(node or self.root)
        while not stack.is_empty():
            current = stack.pop()
            yield current.key
            # push children in reverse so the first child is visited first
            for child in reversed(self.children(current)):
                stack.push(child)

    def find(self, key):
        stack = ArrayStack()
        stack.push(self.root)
        while not stack.is_empty():
            current = stack.pop()
            if current.key == key:
                return current
            for child in self.children(current):
                stack.push(child)
        return None

    def depth(self, node):
        d = 0
        while node.parent is not None:
            node = node.parent
            d += 1
        return d

    def height(self, node=None):
        """Number of edges on the longest root-to-leaf path (BFS with ArrayQueue)."""
        queue = ArrayQueue()
        queue.enqueue((node or self.root, 0))
        best = 0
        while not queue.is_empty():
            current, level = queue.dequeue()
            best = max(best, level)
            for child in self.children(current):
                queue.enqueue((child, level + 1))
        return best


if __name__ == "__main__":
    # Small demo you can run with:  python3 src/data_structures.py
    arr = DynamicArray()
    for x in [10, 20, 30]:
        arr.append(x)
    arr.insert(1, 15)
    arr.delete(0)
    print("DynamicArray:", arr)

    m = Matrix.from_lists([[1, 2], [3, 4]])
    m.insert_row(2, [5, 6])
    print("Matrix after insert_row:", m)
    print("Transpose:", m.transpose())

    s = ArrayStack()
    for x in "abc":
        s.push(x)
    print("Stack pops:", s.pop(), s.pop(), s.pop())

    q = ArrayQueue()
    for x in "abc":
        q.enqueue(x)
    print("Queue dequeues:", q.dequeue(), q.dequeue(), q.dequeue())

    ll = SinglyLinkedList([1, 2, 3])
    ll.insert_front(0)
    ll.insert_at(2, 99)
    ll.delete_value(2)
    print("Linked list:", ll)
    ll.reverse()
    print("Reversed:   ", ll)

    t = RootedTree("CEO")
    cto = t.add_child(t.root, "CTO")
    t.add_child(t.root, "CFO")
    t.add_child(cto, "Engineer")
    print("Tree preorder:", list(t.preorder()), "height:", t.height())

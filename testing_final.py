#!/usr/bin/env python3
"""
testing_final.py - manual visual verification of ALL pkstruct data structures.

Usage:
    python testing_final.py

Each section builds, manipulates, and inspects one data structure so you can
read the output and verify correctness by eye.  Edge cases (empty, single
element, duplicates, errors) are exercised where meaningful.
"""

from pkstruct import (
    SinglyLinkedList,
    DoublyLinkedList,
    CircularLinkedList,
    ArrayStack,
    LinkedStack,
    LinkedQueue,
    CircularQueue,
    PriorityQueue,
    LinkedDeque,
    BinarySearchTree,
    AVLTree,
    RedBlackTree,
    BTree,
    BPlusTree,
    SegmentTree,
    FenwickTree,
    IntervalTree,
    # Shared exceptions
    PkstructError,
    ValidationError,
    IndexOutOfRangeError,
    ValueNotFoundError,
    EmptyStructureError,
    SerializationError,
    ConcurrencyError,
    InvalidRangeError,
    QueueFullError,
    # Tree exceptions
    TreeError,
    KeyNotFoundError,
    DuplicateKeyError,
    EmptyTreeError,
    InvalidOrderError,
    InvalidOperationError,
    TreeBalanceError,
    TreeSerializationError,
    InvalidIntervalError,
    IndexOutOfBoundsError,
)

SEP = "=" * 72
DASH = "-" * 72

# ---------------------------------------------------------------------------
# Section: SinglyLinkedList
# ---------------------------------------------------------------------------

def test_singly_linked_list():
    print(f"\n{SEP}")
    print("  SinglyLinkedList")
    print(f"{DASH}")

    # Construction
    sll = SinglyLinkedList()
    print(f"  new SLL:        {sll!r}")
    print(f"  is_empty:       {sll.is_empty()}")
    print(f"  len:            {len(sll)}")

    # insert with position
    sll.insert(10, position=0)
    sll.insert(20, position=1)
    sll.insert(5, position=0)
    print(f"  after inserts:  {sll!r}")

    # insert before / after
    sll.insert(value=15, before=20)
    sll.insert(value=25, after=20)
    print(f"  before/after:   {sll!r}")

    # from_list
    sll2 = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
    print(f"  from_list:      {sll2!r}")
    print(f"  to_list:        {sll2.to_list()}")

    # accessors
    print(f"  get(0):         {sll2.get(0)}")
    print(f"  get(0, from_end=True): {sll2.get(0, from_end=True)}")
    print(f"  get(1, from_end=True): {sll2.get(1, from_end=True)}")
    try:
        sll2.get(99)
    except IndexOutOfRangeError as e:
        print(f"  get(99) error:  {e}")

    # __getitem__
    print(f"  [1]:            {sll2[1]}")

    # __setitem__
    sll2[2] = 99
    print(f"  after [2]=99:   {sll2!r}")
    sll2[2] = 3

    # __contains__
    print(f"  3 in list:      {3 in sll2}")
    print(f"  999 in list:    {999 in sll2}")

    # count / index
    sll2.insert(3)
    print(f"  count(3):       {sll2.count(3)}")
    print(f"  index(4):       {sll2.index(4)}")
    try:
        sll2.index(999)
    except ValueNotFoundError as e:
        print(f"  index(999) err: {e}")

    # replace
    rep = sll2.replace(42, old_value=3, replace_all=True)
    print(f"  replace 3->42:  {rep} replaced, list: {sll2!r}")
    sll2 = SinglyLinkedList.from_list([1, 2, 3, 4, 5])

    # delete
    val = sll2.delete(value=3)
    print(f"  delete(3):      removed {val}, list: {sll2!r}")
    sll3 = SinglyLinkedList.from_list([10, 20, 30, 40, 50])
    deleted = sll3.delete(rng=(1, 3))
    print(f"  delete range:   removed {deleted}, list: {sll3!r}")

    # reverse
    sll4 = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
    sll4.reverse()
    print(f"  reverse:        {sll4!r}")
    sll4.reverse(start=1, end=3)
    print(f"  reverse(1,3):   {sll4!r}")

    # rotate
    sll5 = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
    sll5.rotate(shift=2)
    print(f"  rotate(2):      {sll5!r}")
    sll5.rotate(shift=2, start=0, end=2, direction=True)
    print(f"  rotate partial: {sll5!r}")

    # swap
    sll6 = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
    sll6.swap(pos1=0, pos2=4)
    print(f"  swap(0,4):      {sll6!r}")
    sll7 = SinglyLinkedList.from_list([1, 2, 3, 4, 5, 6])
    sll7.swap(pairwise=True)
    print(f"  swap pairwise:  {sll7!r}")

    # sort
    sll8 = SinglyLinkedList.from_list([3, 1, 4, 1, 5, 9, 2, 6])
    sll8.sort()
    print(f"  sort:           {sll8!r}")
    sll8.sort(reverse=True)
    print(f"  sort rev:       {sll8!r}")
    sll9 = SinglyLinkedList.from_list(["cat", "banana", "apple", "dog"])
    sll9.sort(key=len)
    print(f"  sort by len:    {sll9!r}")

    # partition
    sll10 = SinglyLinkedList.from_list([1, 2, 3, 4, 5, 6])
    sll10.partition(lambda x: x % 2 == 0)
    print(f"  partition(evens): {sll10!r}")

    # palindrome
    pal = SinglyLinkedList.from_list([1, 2, 3, 2, 1])
    print(f"  palindrome:     {pal.palindrome()}")
    nopal = SinglyLinkedList.from_list([1, 2, 3])
    print(f"  not palindrome: {nopal.palindrome()}")

    # detect_cycle
    print(f"  detect_cycle:   {sll10.detect_cycle()} (no cycle)")

    # reorder
    ro = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
    ro.reorder(mode="odd_even")
    print(f"  reorder odd/even: {ro!r}")

    # segregate_even_odd
    seo = SinglyLinkedList.from_list([1, 2, 3, 4, 5, 6])
    seo.segregate_even_odd()
    print(f"  segregate e/o:  {seo!r}")

    # extend / merge
    a = SinglyLinkedList.from_list([1, 2])
    b = SinglyLinkedList.from_list([3, 4])
    a.extend([10, 11])
    print(f"  extend:         {a!r}")
    a.merge(b)
    print(f"  merge:          {a!r}")

    # copy
    c = a.copy()
    print(f"  copy:           {c!r}")

    # intersection_node
    common = SinglyLinkedList.from_list([1, 2, 3])
    # No actual intersection in independent lists:
    print(f"  intersection:   {common.intersection_node(SinglyLinkedList.from_list([4, 5, 6]))}")

    # serialization
    json_str = sll5.to_json()
    restored = SinglyLinkedList.from_json(json_str)
    print(f"  JSON:           {json_str}")
    print(f"  from_json:      {restored!r}")
    print(f"  roundtrip OK:   {sll5.to_list() == restored.to_list()}")

    # visualize
    print(f"  visualize:\n{sll5.visualize()}")

    # debug
    dbg = sll5.debug()
    print(f"  debug keys:     {list(dbg.keys())}")

    # head / tail
    print(f"  head:           {sll5.head}")
    print(f"  tail:           {sll5.tail}")

    # __eq__
    eq1 = SinglyLinkedList.from_list([1, 2, 3])
    eq2 = SinglyLinkedList.from_list([1, 2, 3])
    print(f"  eq:             {eq1 == eq2}")
    print(f"  ne:             {eq1 == SinglyLinkedList()}")

    # Edge cases
    empty = SinglyLinkedList()
    print(f"  empty repr:     {empty!r}")
    print(f"  empty len:      {len(empty)}")
    print(f"  empty bool:     {bool(empty)}")
    print(f"  empty list:     {empty.to_list()}")
    empty.insert(1)
    print(f"  insert(1):      {empty!r}")

# ---------------------------------------------------------------------------
# Section: DoublyLinkedList
# ---------------------------------------------------------------------------

def test_doubly_linked_list():
    print(f"\n{SEP}")
    print("  DoublyLinkedList")
    print(f"{DASH}")

    dll = DoublyLinkedList()
    print(f"  new:            {dll!r}")

    dll = DoublyLinkedList.from_list([1, 2, 3, 4, 5])
    print(f"  from_list:      {dll!r}")
    print(f"  to_list:        {dll.to_list()}")

    dll.reverse()
    print(f"  reverse:        {dll!r}")

    dll.reverse(start=1, end=3)
    print(f"  reverse(1,3):   {dll!r}")

    json_str = dll.to_json()
    restored = DoublyLinkedList.from_json(json_str)
    print(f"  JSON roundtrip: {restored!r}")
    print(f"  roundtrip OK:   {dll.to_list() == restored.to_list()}")

    dll2 = DoublyLinkedList.from_list([1, 2, 3, 4, 5])
    dll2.insert(99, before=3)
    print(f"  insert before:  {dll2!r}")
    dll2.insert(88, after=99)
    print(f"  insert after:   {dll2!r}")

    # Edge: single element
    single = DoublyLinkedList.from_list([42])
    single.reverse()
    print(f"  single reverse: {single!r}")

    # visualize
    print(f"  visualize:\n{dll.visualize()}")

    # debug
    print(f"  debug keys:     {list(dll.debug().keys())}")

# ---------------------------------------------------------------------------
# Section: CircularLinkedList
# ---------------------------------------------------------------------------

def test_circular_linked_list():
    print(f"\n{SEP}")
    print("  CircularLinkedList")
    print(f"{DASH}")

    cll = CircularLinkedList()
    print(f"  new:            {cll!r}")

    cll = CircularLinkedList.from_list([1, 2, 3, 4, 5])
    print(f"  from_list:      {cll!r}")
    print(f"  to_list:        {cll.to_list()}")

    # rotate_head
    cll.rotate_head(steps=2)
    print(f"  rotate_head(2): {cll!r}")
    cll.rotate_head(steps=1, direction=False)
    print(f"  rotate_head(back): {cll!r}")

    # rotate (inherited)
    cll2 = CircularLinkedList.from_list([1, 2, 3, 4, 5])
    cll2.rotate(shift=3)
    print(f"  rotate(3):      {cll2!r}")

    # josephus (dangerous with 5, step 2)
    cll3 = CircularLinkedList.from_list([1, 2, 3, 4, 5])
    survivor = cll3.josephus(step=2)
    print(f"  josephus(2):    survivor={survivor}")

    # detect_cycle
    print(f"  detect_cycle:   {cll.detect_cycle()} (circular = True)")

    # Edge: single element
    single = CircularLinkedList.from_list([42])
    single.rotate_head(1)
    print(f"  single head:    {single!r}")

    jos_single = CircularLinkedList.from_list([1])
    print(f"  josephus(single): {jos_single.josephus(1)}")

    # visualize
    print(f"  visualize:\n{cll.visualize()}")

# ---------------------------------------------------------------------------
# Section: Stacks (ArrayStack + LinkedStack)
# ---------------------------------------------------------------------------

def test_stacks():
    print(f"\n{SEP}")
    print("  ArrayStack")
    print(f"{DASH}")

    s = ArrayStack()
    print(f"  new:            {s!r}")
    print(f"  is_empty:       {s.is_empty()}")

    s.push(10)
    s.push(20)
    s.push(30)
    print(f"  after 3 pushes: {s!r}")
    print(f"  peek:           {s.peek()}")
    print(f"  pop:            {s.pop()}")
    print(f"  after pop:      {s!r}")
    print(f"  len:            {len(s)}")
    print(f"  bool(nonempty): {bool(s)}")

    s2 = ArrayStack([1, 2, 3])
    print(f"  from list:      {s2!r}")
    print(f"  to_list:        {s2.to_list()}")
    print(f"  iter:           {list(s2)}")

    c = s2.copy()
    print(f"  copy:           {c!r}")
    print(f"  eq:             {s2 == c}")

    s2.clear()
    print(f"  after clear:    {s2!r}")
    print(f"  is_empty:       {s2.is_empty()}")

    # Edge: pop from empty
    try:
        ArrayStack().pop()
    except EmptyStructureError as e:
        print(f"  empty pop:      {e}")

    try:
        ArrayStack().peek()
    except EmptyStructureError as e:
        print(f"  empty peek:     {e}")

    # LinkedStack
    print(f"\n  LinkedStack")
    print(f"{DASH}")
    ls = LinkedStack()
    ls.push(1)
    ls.push(2)
    ls.push(3)
    print(f"  linked:         {ls!r}")
    print(f"  pop:            {ls.pop()}")
    print(f"  peek:           {ls.peek()}")
    print(f"  len:            {len(ls)}")
    print(f"  iter:           {list(ls)}")

    ls2 = LinkedStack(["a", "b", "c"])
    print(f"  from list:      {ls2!r}")
    c2 = ls2.copy()
    print(f"  copy:           {c2!r}")
    print(f"  eq:             {ls2 == c2}")
    ls2.clear()
    print(f"  cleared:        {ls2!r}")

    try:
        LinkedStack().pop()
    except EmptyStructureError as e:
        print(f"  empty pop:      {e}")

# ---------------------------------------------------------------------------
# Section: Queues (LinkedQueue + CircularQueue)
# ---------------------------------------------------------------------------

def test_queues():
    print(f"\n{SEP}")
    print("  LinkedQueue")
    print(f"{DASH}")

    q = LinkedQueue()
    print(f"  new:            {q!r}")
    q.enqueue(10)
    q.enqueue(20)
    q.enqueue(30)
    print(f"  after 3 enqs:   {q!r}")
    print(f"  front:          {q.front()}")
    print(f"  rear:           {q.rear()}")
    print(f"  dequeue:        {q.dequeue()}")
    print(f"  after dq:       {q!r}")
    print(f"  len:            {len(q)}")
    print(f"  bool:           {bool(q)}")
    print(f"  to_list:        {q.to_list()}")
    print(f"  iter:           {list(q)}")

    q2 = LinkedQueue([1, 2, 3])
    print(f"  from list:      {q2!r}")
    c = q2.copy()
    print(f"  copy:           {c!r}")
    print(f"  eq:             {q2 == c}")
    q2.clear()
    print(f"  cleared:        {q2!r}")
    print(f"  is_empty:       {q2.is_empty()}")

    try:
        LinkedQueue().dequeue()
    except EmptyStructureError as e:
        print(f"  empty dq:       {e}")

    # CircularQueue
    print(f"\n  CircularQueue (capacity 3)")
    print(f"{DASH}")
    cq = CircularQueue(capacity=3)
    print(f"  new:            {cq!r}")
    print(f"  is_empty:       {cq.is_empty()}")
    print(f"  is_full:        {cq.is_full()}")
    print(f"  capacity:       {cq.capacity()}")

    cq.enqueue(1)
    cq.enqueue(2)
    cq.enqueue(3)
    print(f"  after 3 enqs:   {cq!r}")
    print(f"  is_full:        {cq.is_full()}")
    print(f"  front:          {cq.front()}")
    print(f"  rear:           {cq.rear()}")

    try:
        cq.enqueue(4)
    except QueueFullError as e:
        print(f"  full enq err:   {e}")

    print(f"  dequeue:        {cq.dequeue()}")
    print(f"  after dq:       {cq!r}")
    cq.enqueue(4)
    print(f"  enq(4) (wrap):  {cq!r}")
    print(f"  to_list:        {cq.to_list()}")

    cq2 = CircularQueue(capacity=5, items=[1, 2, 3])
    print(f"  from items:     {cq2!r}")
    cq2.clear()
    print(f"  cleared:        {cq2!r}")

    cqc = cq.copy()
    print(f"  copy:           {cqc!r}")
    print(f"  eq:             {cq == cqc}")

    print(f"  size:           {cq.size()}")
    print(f"  len:            {len(cq)}")
    print(f"  bool:           {bool(cq)}")
    print(f"  iter:           {list(cq)}")

    try:
        CircularQueue(capacity=3).dequeue()
    except EmptyStructureError as e:
        print(f"  empty dq:       {e}")

# ---------------------------------------------------------------------------
# Section: PriorityQueue
# ---------------------------------------------------------------------------

def test_priority_queue():
    print(f"\n{SEP}")
    print("  PriorityQueue")
    print(f"{DASH}")

    pq = PriorityQueue()
    print(f"  new:            {pq!r}")

    pq.enqueue(5)
    pq.enqueue(1)
    pq.enqueue(3)
    pq.enqueue(2)
    pq.enqueue(4)
    print(f"  after 5 enqs:   {pq!r}")

    print(f"  front (min):    {pq.front()}")
    print(f"  rear (max):     {pq.rear()}")

    ordered = []
    while not pq.is_empty():
        ordered.append(pq.dequeue())
    print(f"  dequeue all:    {ordered}")

    pq2 = PriorityQueue([3, 1, 4, 1, 5])
    print(f"  from list:      {pq2!r}")
    print(f"  len:            {len(pq2)}")
    print(f"  bool:           {bool(pq2)}")
    print(f"  to_list:        {pq2.to_list()}")
    print(f"  iter:           {list(pq2)}")

    c = pq2.copy()
    print(f"  copy:           {c!r}")
    print(f"  eq:             {pq2 == c}")

    pq2.clear()
    print(f"  cleared:        {pq2!r}")
    print(f"  is_empty:       {pq2.is_empty()}")

    try:
        PriorityQueue().dequeue()
    except EmptyStructureError as e:
        print(f"  empty dq:       {e}")

# ---------------------------------------------------------------------------
# Section: LinkedDeque
# ---------------------------------------------------------------------------

def test_linked_deque():
    print(f"\n{SEP}")
    print("  LinkedDeque")
    print(f"{DASH}")

    d = LinkedDeque()
    print(f"  new:            {d!r}")

    d.append(10)    # default side="right"
    d.append(20)
    d.append(30)
    d.append(5, side="left")
    d.append(0, side="left")
    print(f"  after 5 appends: {d!r}")
    print(f"  to_list:        {d.to_list()}")

    print(f"  pop(right):     {d.pop()}")
    print(f"  pop(left):      {d.pop(side='left')}")
    print(f"  after 2 pops:   {d!r}")
    print(f"  peek(left):     {d.peek()}")
    print(f"  peek(right):    {d.peek(side='right')}")

    d.rotate(steps=2)
    print(f"  rotate(2):      {d!r}")

    d.reverse()
    print(f"  reverse:        {d!r}")

    print(f"  size:           {d.size()}")
    print(f"  len:            {len(d)}")
    print(f"  bool:           {bool(d)}")
    print(f"  is_empty:       {d.is_empty()}")
    print(f"  iter:           {list(d)}")

    d2 = LinkedDeque([1, 2, 3, 4, 5])
    print(f"  from list:      {d2!r}")
    c = d2.copy()
    print(f"  copy:           {c!r}")
    print(f"  eq:             {d2 == c}")

    d2.clear()
    print(f"  cleared:        {d2!r}")

    try:
        LinkedDeque().pop()
    except EmptyStructureError as e:
        print(f"  empty pop:      {e}")

    try:
        LinkedDeque().peek()
    except EmptyStructureError as e:
        print(f"  empty peek:     {e}")

# ---------------------------------------------------------------------------
# Section: BinarySearchTree
# ---------------------------------------------------------------------------

def test_bst():
    print(f"\n{SEP}")
    print("  BinarySearchTree")
    print(f"{DASH}")

    bst = BinarySearchTree()
    print(f"  new:            {bst!r}")
    print(f"  is_empty:       {bst.is_empty()}")

    for v in [5, 3, 7, 2, 4, 6, 8]:
        bst.insert(v)
    print(f"  after inserts:  {bst!r}")
    print(f"  size:           {bst.size()}")
    print(f"  len:            {len(bst)}")
    print(f"  height:         {bst.height()}")
    print(f"  min:            {bst.min()}")
    print(f"  max:            {bst.max()}")
    print(f"  inorder:        {list(bst)}")

    print(f"  search(4):      {bst.search(4)}")
    print(f"  search(99):     {bst.search(99)}")
    print(f"  contains(7):    {bst.contains(7)}")
    print(f"  contains(99):   {bst.contains(99)}")
    print(f"  7 in tree:      {7 in bst}")
    print(f"  99 in tree:     {99 in bst}")

    bst.update(key=4, value="four")
    print(f"  search(4) after update: {bst.search(4)}")

    bst.delete(7)
    print(f"  after del(7):   {list(bst)}")
    bst.delete(3)
    print(f"  after del(3):   {list(bst)}")

    # floor / ceil
    bst2 = BinarySearchTree()
    for v in [10, 5, 15, 3, 7, 12, 18]:
        bst2.insert(v)
    print(f"  floor(6):       {bst2.floor(6)}")
    print(f"  ceil(6):        {bst2.ceil(6)}")
    print(f"  floor(3):       {bst2.floor(3)}")
    print(f"  ceil(18):       {bst2.ceil(18)}")

    # predecessor / successor
    print(f"  pred(12):       {bst2.predecessor(12)}")
    print(f"  succ(12):       {bst2.successor(12)}")
    print(f"  pred(3):        {bst2.predecessor(3)}")
    print(f"  succ(18):       {bst2.successor(18)}")

    # validate
    print(f"  validate:       {bst2.validate()}")

    # copy
    cp = bst2.copy()
    print(f"  copy:           {list(cp)}")
    print(f"  copy eq:        {list(cp) == list(bst2)}")

    # invert
    orig = BinarySearchTree()
    for v in [4, 2, 6, 1, 3, 5, 7]:
        orig.insert(v)
    inv = orig.copy()
    inv.invert()
    print(f"  original:       {list(orig)}")
    print(f"  inverted:       {list(inv)}")

    # is_balanced / diameter / width
    print(f"  is_balanced:    {bst2.is_balanced()}")
    print(f"  diameter:       {bst2.diameter()}")
    print(f"  width:          {bst2.width()}")

    # find_lca
    print(f"  LCA(3, 12):     {bst2.find_lca(3, 12)}")
    print(f"  LCA(5, 18):     {bst2.find_lca(5, 18)}")

    # kth_smallest / kth_largest
    print(f"  kth_smallest(1): {bst2.kth_smallest(1)}")
    print(f"  kth_largest(1): {bst2.kth_largest(1)}")
    print(f"  kth_smallest(4): {bst2.kth_smallest(4)}")

    # range_query
    print(f"  range_query(6, 18): {bst2.range_query(6, 18)}")

    # path_sum
    print(f"  path_sum(18):   {bst2.path_sum(18)} (10+5+3)")
    print(f"  path_sum(999):  {bst2.path_sum(999)}")

    # root_to_leaf_paths
    print(f"  root_to_leaf:   {bst2.root_to_leaf_paths()}")

    # serialize / deserialize
    data = bst2.serialize()
    print(f"  serialize:      {data}")
    new_bst = BinarySearchTree()
    new_bst.deserialize(data)
    print(f"  deserialize:    {list(new_bst)}")

    # boundary_traversal / vertical_order / zigzag_order
    print(f"  boundary:       {bst2.boundary_traversal()}")
    print(f"  vertical_order: {bst2.vertical_order()}")
    print(f"  zigzag_order:   {bst2.zigzag_order()}")

    # Edge cases
    empty = BinarySearchTree()
    print(f"  empty iter:     {list(empty)}")
    print(f"  empty len:      {len(empty)}")
    try:
        empty.min()
    except ValueError as e:
        print(f"  empty min:      ValueError: {e}")
    try:
        empty.max()
    except ValueError as e:
        print(f"  empty max:      ValueError: {e}")

    # duplicates
    bst_dup = BinarySearchTree(allow_duplicates=True)
    bst_dup.insert(5)
    try:
        bst_dup.insert(5)
    except ValueError as e:
        print(f"  duplicate(5) err: {e}")
    print(f"  after dupe:     {list(bst_dup)} (one 5)")

    # single
    single = BinarySearchTree()
    single.insert(1)
    print(f"  single:         {list(single)}")
    print(f"  single height:  {single.height()}")

    try:
        empty.delete(1)
    except (KeyError, KeyNotFoundError) as e:
        print(f"  del empty:      {e}")

# ---------------------------------------------------------------------------
# Section: AVLTree
# ---------------------------------------------------------------------------

def test_avl():
    print(f"\n{SEP}")
    print("  AVLTree")
    print(f"{DASH}")

    avl = AVLTree()
    print(f"  new:            {avl!r}")

    for v in [1, 2, 3, 4, 5, 6, 7]:
        avl.insert(v)
    print(f"  after inserts:  {list(avl)}")
    print(f"  height:         {avl.height()}")
    print(f"  is_avl_valid:   {avl.is_avl_valid()}")
    print(f"  validate:       {avl.validate()}")

    avl.delete(4)
    print(f"  after del(4):   {list(avl)}")
    print(f"  is_avl_valid:   {avl.is_avl_valid()}")

    print(f"  balance_factor(2): {avl.balance_factor(2)}")
    print(f"  balance_factor(5): {avl.balance_factor(5)}")

    # inherited BST features
    print(f"  search(3):      {avl.search(3)}")
    print(f"  floor(6):       {avl.floor(6)}")
    print(f"  LCA(1, 7):      {avl.find_lca(1, 7)}")
    print(f"  kth_smallest(3): {avl.kth_smallest(3)}")
    print(f"  range_query(3,6): {avl.range_query(3, 6)}")

    # serialize/deserialize
    data = avl.serialize()
    new_avl = AVLTree()
    new_avl.deserialize(data)
    print(f"  serialize:      {data}")
    print(f"  deserialize:    {list(new_avl)}")
    print(f"  deserialized valid: {new_avl.is_avl_valid()}")

    # copy
    cp = avl.copy()
    print(f"  copy list:      {list(cp)}")
    print(f"  copy match:     {list(cp) == list(avl)}")

    # Edge: empty
    empty = AVLTree()
    print(f"  empty valid:    {empty.is_avl_valid()}")
    print(f"  empty iter:     {list(empty)}")

    # Edge: single
    single = AVLTree()
    single.insert(1)
    print(f"  single list:    {list(single)}")
    print(f"  single valid:   {single.is_avl_valid()}")

# ---------------------------------------------------------------------------
# Section: RedBlackTree
# ---------------------------------------------------------------------------

def test_red_black():
    print(f"\n{SEP}")
    print("  RedBlackTree")
    print(f"{DASH}")

    rbt = RedBlackTree()
    print(f"  new:            {rbt!r}")

    for v in [10, 20, 30, 15, 25, 5, 1]:
        rbt.insert(v)
    print(f"  after inserts:  {list(rbt)}")
    print(f"  size:           {rbt.size()}")
    print(f"  len:            {len(rbt)}")
    print(f"  height:         {rbt.height()}")
    print(f"  black_height:   {rbt.black_height()}")
    print(f"  min:            {rbt.min()}")
    print(f"  max:            {rbt.max()}")
    print(f"  search(15):     {rbt.search(15)}")
    print(f"  contains(99):   {rbt.contains(99)}")
    print(f"  validate:       {rbt.validate()}")
    print(f"  is_rb_valid:    {rbt.is_red_black_valid()}")

    rbt.delete(20)
    print(f"  after del(20):  {list(rbt)}")
    print(f"  is_rb_valid:    {rbt.is_red_black_valid()}")

    rbt.update(15, "updated")
    print(f"  search(15) upd: {rbt.search(15)}")

    print(f"  predecessor(30): {rbt.predecessor(30)}")
    print(f"  successor(10):  {rbt.successor(10)}")

    cp = rbt.copy()
    print(f"  copy:           {list(cp)}")
    print(f"  copy valid:     {cp.is_red_black_valid()}")

    rbt.clear()
    print(f"  cleared:        {rbt!r}")
    print(f"  is_empty:       {rbt.is_empty()}")

    # Edge: empty
    empty = RedBlackTree()
    print(f"  empty valid:    {empty.is_red_black_valid()}")

    # Edge: single
    single = RedBlackTree()
    single.insert(1)
    print(f"  single list:    {list(single)}")

    try:
        empty.delete(1)
    except (KeyError, KeyNotFoundError) as e:
        print(f"  del empty:      {e}")

# ---------------------------------------------------------------------------
# Section: BTree
# ---------------------------------------------------------------------------

def test_btree():
    print(f"\n{SEP}")
    print("  BTree (order 3)")
    print(f"{DASH}")

    bt = BTree(order=3)
    print(f"  new:            {bt!r}")
    print(f"  order:          {bt.order}")

    for v in [10, 20, 30, 40, 50, 60, 70]:
        bt.insert(v)
    print(f"  after inserts:  {list(bt)}")
    print(f"  size:           {bt.size()}")
    print(f"  len:            {len(bt)}")
    print(f"  min:            {bt.min()}")
    print(f"  max:            {bt.max()}")
    print(f"  search(40):     {bt.search(40)}")
    print(f"  contains(99):   {bt.contains(99)}")
    print(f"  validate:       {bt.validate()}")

    bt.delete(40)
    print(f"  after del(40):  {list(bt)}")
    bt.delete(10)
    print(f"  after del(10):  {list(bt)}")
    bt.delete(70)
    print(f"  after del(70):  {list(bt)}")

    bt.update(30, "thirty")
    print(f"  search(30) upd: {bt.search(30)}")

    bt.clear()
    print(f"  cleared:        {bt!r}")

    # Edge: order 2 (minimum valid)
    bt2 = BTree(order=2)
    for v in [5, 3, 7, 2, 4, 6, 8]:
        bt2.insert(v)
    print(f"  order 2 list:   {list(bt2)}")
    print(f"  order 2 valid:  {bt2.validate()}")

    try:
        BTree(order=1)
    except InvalidOrderError as e:
        print(f"  invalid order:  {e}")

    # Single
    bt3 = BTree(order=3)
    bt3.insert(1)
    print(f"  single list:    {list(bt3)}")

# ---------------------------------------------------------------------------
# Section: BPlusTree
# ---------------------------------------------------------------------------

def test_bplus():
    print(f"\n{SEP}")
    print("  BPlusTree (order 3)")
    print(f"{DASH}")

    bpt = BPlusTree(order=3)
    print(f"  new:            {bpt!r}")
    print(f"  order:          {bpt.order}")

    for v in [10, 20, 30, 40, 50, 60, 70]:
        bpt.insert(v, value=f"val_{v}")
    print(f"  after inserts:  {list(bpt)}")
    print(f"  size:           {bpt.size()}")
    print(f"  len:            {len(bpt)}")
    print(f"  min:            {bpt.min()}")
    print(f"  max:            {bpt.max()}")
    print(f"  search(40):     {bpt.search(40)}")
    print(f"  contains(99):   {bpt.contains(99)}")
    print(f"  validate:       {bpt.validate()}")

    bpt.delete(40)
    print(f"  after del(40):  {list(bpt)}")

    bpt.update(30, "updated_30")
    print(f"  search(30) upd: {bpt.search(30)}")

    bpt2 = BPlusTree(order=3)
    for v in [5, 3, 7, 2, 4, 6, 8]:
        bpt2.insert(v)
    print(f"  leaf_traversal: {bpt2.leaf_traversal()}")
    print(f"  range_query(3,7): {bpt2.range_query(3, 7)}")

    try:
        BPlusTree(order=1)
    except InvalidOrderError as e:
        print(f"  invalid order:  {e}")

# ---------------------------------------------------------------------------
# Section: SegmentTree
# ---------------------------------------------------------------------------

def test_segment_tree():
    print(f"\n{SEP}")
    print("  SegmentTree")
    print(f"{DASH}")

    data = [1, 3, 5, 7, 9, 11]
    st = SegmentTree(data)
    print(f"  new:            {st!r}")
    print(f"  size:           {st.size}")
    print(f"  len:            {len(st)}")

    print(f"  query(0, 2):    {st.query(0, 2)} (1+3+5=9)")
    print(f"  query(1, 4):    {st.query(1, 4)} (3+5+7+9=24)")
    print(f"  query(0, 5):    {st.query(0, 5)}")

    st.update(index=2, value=10)
    print(f"  query(0,3) after update(2,10): {st.query(0, 3)} (1+3+10+7=21)")

    st.range_update(left=1, right=3, value=2)
    print(f"  query(0,5) after range_upd(1,3,2): {st.query(0, 5)}")

    # rebuild
    st.rebuild([10, 20, 30])
    print(f"  rebuild:        {st!r}")
    print(f"  query(0,2):     {st.query(0, 2)} (60)")

    print(f"  validate:       {st.validate()}")

    st.clear()
    print(f"  cleared:        {st!r}")
    st.build([5, 10, 15])
    print(f"  rebuild(5,10,15): {st!r}")

    # different operations
    st_min = SegmentTree([3, 1, 4, 1, 5, 9], operation="min")
    print(f"  min query(0,5): {st_min.query(0, 5)} (1)")
    st_max = SegmentTree([3, 1, 4, 1, 5, 9], operation="max")
    print(f"  max query(0,5): {st_max.query(0, 5)} (9)")
    st_xor = SegmentTree([1, 2, 3, 4], operation="xor")
    print(f"  xor query(0,3): {st_xor.query(0, 3)} (1^2^3^4=4)")

# ---------------------------------------------------------------------------
# Section: FenwickTree
# ---------------------------------------------------------------------------

def test_fenwick():
    print(f"\n{SEP}")
    print("  FenwickTree")
    print(f"{DASH}")

    ft = FenwickTree([3, 2, -1, 6, 5, 4])
    print(f"  new:            {ft!r}")
    print(f"  size:           {ft.size}")
    print(f"  len:            {len(ft)}")

    print(f"  prefix_sum(3):  {ft.prefix_sum(3)} (3+2+(-1)=4)")
    print(f"  query(6):       {ft.query(6)} (all={ft.query(6)})")
    print(f"  range_query(2,4): {ft.range_query(2, 4)} (2+(-1)+6=7)")

    ft.update(index=3, delta=6)
    print(f"  prefix_sum(3) after upd(3,+6): {ft.prefix_sum(3)} (4+6=10)")

    print(f"  lower_bound(10): {ft.lower_bound(10)}")
    print(f"  validate:       {ft.validate()}")

    ft.clear()
    print(f"  cleared:        {ft!r}")
    ft.build([1, 2, 3, 4])
    print(f"  rebuild:        {ft!r}")
    print(f"  range_query(1,4): {ft.range_query(1, 4)} (10)")
    print(f"  lower_bound(5): {ft.lower_bound(5)}")

    # Edge: empty
    ft2 = FenwickTree(n=5)
    print(f"  empty tree:     {ft2!r}")
    print(f"  query all:      {ft2.query(5)} (0)")

# ---------------------------------------------------------------------------
# Section: IntervalTree
# ---------------------------------------------------------------------------

def test_interval_tree():
    print(f"\n{SEP}")
    print("  IntervalTree")
    print(f"{DASH}")

    it = IntervalTree()
    print(f"  new:            {it!r}")

    intervals = [(15, 20), (10, 30), (5, 8), (12, 18), (17, 25)]
    for lo, hi in intervals:
        it.insert(lo, hi)
    print(f"  after 5 inserts: {len(it)} intervals")
    print(f"  size:           {it.size}")
    print(f"  height:         {it.height()}")

    print(f"  overlap(14,16): {it.overlap(14, 16)} (True)")
    print(f"  overlap(1,4):   {it.overlap(1, 4)} (False)")

    results = it.search(14, 16)
    print(f"  search(14,16):  {results}")
    results = it.all_overlaps(14, 16)
    print(f"  all_overlaps:   {results}")

    contained = it.contains_point(7)
    print(f"  contains_point(7): {contained}")
    contained = it.contains_point(100)
    print(f"  contains_point(100): {contained}")
    print(f"  15-20 in tree:  {(15, 20) in it}")
    print(f"  max_endpoint:   {it.max_endpoint}")
    print(f"  validate:       {it.validate()}")

    it.delete(15, 20)
    print(f"  after del(15,20): {it.size} intervals")
    print(f"  overlap(14,16): {it.overlap(14, 16)} (after delete)")

    it2 = IntervalTree()
    for lo, hi in [(1, 5), (3, 7), (6, 10), (8, 12)]:
        it2.insert(lo, hi)
    it2.merge_overlaps()
    print(f"  after merge:    {it2.size} intervals")
    print(f"  intervals:      {sorted(it2)}")

    it2.clear()
    print(f"  cleared:        {len(it2)} intervals")

    try:
        it2.search(5, 10)
    except EmptyTreeError as e:
        print(f"  empty search:   {e}")

    print(f"  __iter__:       {list(sorted(it))}")

# ---------------------------------------------------------------------------
# Section: Exception hierarchy
# ---------------------------------------------------------------------------

def test_exceptions():
    print(f"\n{SEP}")
    print("  Exception Hierarchy")
    print(f"{DASH}")

    print(f"  PkstructError:          {issubclass(PkstructError, Exception)}")
    print(f"  ValidationError:        {issubclass(ValidationError, PkstructError)}")
    print(f"  IndexOutOfRangeError:   {issubclass(IndexOutOfRangeError, (PkstructError, IndexError))}")
    print(f"  ValueNotFoundError:     {issubclass(ValueNotFoundError, (PkstructError, ValueError))}")
    print(f"  EmptyStructureError:    {issubclass(EmptyStructureError, PkstructError)}")
    print(f"  QueueFullError:         {issubclass(QueueFullError, IndexError)}")
    print(f"  TreeError:              {issubclass(TreeError, Exception)}")
    print(f"  KeyNotFoundError:       {issubclass(KeyNotFoundError, TreeError)}")
    print(f"  DuplicateKeyError:      {issubclass(DuplicateKeyError, TreeError)}")
    print(f"  InvalidOrderError:      {issubclass(InvalidOrderError, TreeError)}")

    # Instantiate each exception type
    excs = [
        PkstructError("generic"),
        ValidationError("bad input"),
        IndexOutOfRangeError(5, 10),
        ValueNotFoundError(42),
        EmptyStructureError("pop"),
        InvalidRangeError(5, 3, 10),
        KeyNotFoundError(999),
        DuplicateKeyError(7),
        EmptyTreeError("delete"),
        InvalidOrderError(0),
        InvalidOperationError("unsupported"),
        TreeBalanceError(),
        TreeSerializationError(),
        InvalidIntervalError(10, 5),
        IndexOutOfBoundsError(5, 3),
    ]
    for e in excs:
        print(f"    {type(e).__name__}: {e}")

# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    print(f"\n{'=' * 72}")
    print("  pkstruct v0.1.0 - Comprehensive Manual Test")
    print(f"{'=' * 72}")

    test_singly_linked_list()
    test_doubly_linked_list()
    test_circular_linked_list()
    test_stacks()
    test_queues()
    test_priority_queue()
    test_linked_deque()
    test_bst()
    test_avl()
    test_red_black()
    test_btree()
    test_bplus()
    test_segment_tree()
    test_fenwick()
    test_interval_tree()
    test_exceptions()

    print(f"\n{'=' * 72}")
    print("  DONE - Read through the output above and verify correctness.")
    print("  Each section prints structure state at each step so you can")
    print("  visually confirm the expected behaviour.")
    print(f"{'=' * 72}\n")

if __name__ == "__main__":
    main()

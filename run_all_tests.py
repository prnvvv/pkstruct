#!/usr/bin/env python3
"""
Complete test runner for pkstruct.linear
Run: python run_all_tests.py
"""

import sys
import os
# Add src/ directory so 'import pkstruct' resolves the package
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import time
import tracemalloc

def print_section(title, char="="):
    print(f"\n{char * 70}")
    print(f"{title:^70}")
    print(f"{char * 70}\n")

class TestRunner:
    def __init__(self):
        self.results = []
        self.failures = []

    def run_test(self, name, test_func):
        print(f"[TEST] {name}...", end=" ", flush=True)
        try:
            start = time.perf_counter()
            tracemalloc.start()
            result = test_func()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            elapsed = time.perf_counter() - start

            print(f"PASSED ({elapsed*1000:.2f}ms, {peak/1024:.1f}KB peak)")
            self.results.append((name, True, elapsed, peak))
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"FAILED: {e}")
            self.failures.append((name, e))
            return None
        finally:
            tracemalloc.stop()

    def summary(self):
        print_section("TEST SUMMARY", "=")
        print(f"Total: {len(self.results) + len(self.failures)}")
        print(f"Passed: {len(self.results)}")
        print(f"Failed: {len(self.failures)}")

        if self.failures:
            print("\nFAILURES:")
            for name, err in self.failures:
                print(f"  - {name}: {err}")
        else:
            print("\nALL TESTS PASSED!")

        if self.results:
            avg_time = sum(t for _, _, t, _ in self.results) / len(self.results)
            max_mem = max(p for _, _, _, p in self.results)
            print(f"\nPerformance: {avg_time*1000:.2f}ms avg | {max_mem/1024:.1f}KB peak")


def comprehensive_tests():
    from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
    from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
    from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList
    from pkstruct.linear.exceptions import (
        EmptyStructureError, IndexOutOfRangeError,
        ValueNotFoundError, ValidationError
    )

    runner = TestRunner()

    # ============ SINGLY LINKED LIST TESTS ============
    print_section("SINGLY LINKED LIST", "-")

    def test_sll_creation():
        sll = SinglyLinkedList.create()
        assert sll.is_empty()
        assert len(sll) == 0
        assert sll.to_list() == []

        sll2 = SinglyLinkedList.from_list([1, 2, 3])
        assert sll2.to_list() == [1, 2, 3]
        return sll2

    runner.run_test("Creation", test_sll_creation)

    def test_sll_insertion():
        sll = SinglyLinkedList.from_list([10, 30])
        sll.insert(20, position=1)
        assert sll.to_list() == [10, 20, 30]

        sll.insert(5, position=0)
        assert sll.to_list() == [5, 10, 20, 30]

        sll.insert(40, position=None)
        assert sll.to_list() == [5, 10, 20, 30, 40]

        sll.insert(15, after=10)
        assert sll.to_list() == [5, 10, 15, 20, 30, 40]

        print(f"  After insertion: {sll.to_list()}")
        return sll

    sll = runner.run_test("Insertion", test_sll_insertion)

    def test_sll_deletion():
        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        sll.delete(position=2)
        assert sll.to_list() == [1, 2, 4, 5]

        sll.delete(value=4)
        assert sll.to_list() == [1, 2, 5]

        sll.delete(range=(0, 1))
        assert sll.to_list() == [5]

        sll.clear()
        assert sll.is_empty()
        print(f"  After deletions: {sll.to_list()}")
        return True

    runner.run_test("Deletion", test_sll_deletion)

    def test_sll_reverse():
        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        original = sll.to_list()
        sll.reverse()
        assert sll.to_list() == [5, 4, 3, 2, 1]

        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        sll.reverse(start=1, end=3)
        assert sll.to_list() == [1, 4, 3, 2, 5]
        print(f"  Reverse example: {original} -> {sll.to_list()}")
        return True

    runner.run_test("Reverse", test_sll_reverse)

    def test_sll_rotate():
        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        sll.rotate(shift=2, start=0, end=4, direction=True)
        assert sll.to_list() == [4, 5, 1, 2, 3]
        print(f"  Rotate right by 2: {sll.to_list()}")
        return True

    runner.run_test("Rotation", test_sll_rotate)

    def test_sll_sort():
        sll = SinglyLinkedList.from_list([5, 2, 8, 1, 9])
        sll.sort()
        assert sll.to_list() == [1, 2, 5, 8, 9]

        sll.sort(reverse=True)
        assert sll.to_list() == [9, 8, 5, 2, 1]
        print(f"  Sorted: {sll.to_list()}")
        return True

    runner.run_test("Sort", test_sll_sort)

    def test_sll_merge():
        sll1 = SinglyLinkedList.from_list([1, 3, 5])
        sll2 = SinglyLinkedList.from_list([2, 4, 6])
        sll1.merge(sll2)
        assert sll1.to_list() == [1, 3, 5, 2, 4, 6]
        print(f"  Merged: {sll1.to_list()}")
        return True

    runner.run_test("Merge", test_sll_merge)

    def test_sll_search():
        sll = SinglyLinkedList.from_list([10, 20, 30, 20, 40])
        idx = sll.index(20)
        assert idx == 1

        count = sll.count(20)
        assert count == 2

        assert 30 in sll
        assert 100 not in sll
        print(f"  Index of 20: {idx}, Count: {count}")
        return True

    runner.run_test("Search", test_sll_search)

    def test_sll_interview_problems():
        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        assert not sll.detect_cycle()

        sll = SinglyLinkedList.from_list([1, 2, 3, 2, 1])
        assert sll.palindrome()

        sll2 = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        assert not sll2.palindrome()

        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5, 6])
        sll.segregate_even_odd()
        print(f"  Segregated (even-odd): {sll.to_list()}")
        return True

    runner.run_test("Interview Problems", test_sll_interview_problems)

    def test_sll_dunders():
        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        assert sll[2] == 3
        sll[2] = 10
        assert sll[2] == 10

        sll2 = SinglyLinkedList.from_list([1, 2, 10, 4, 5])
        assert sll == sll2

        print(f"  Getitem/setitem working")
        return True

    runner.run_test("Dunder Methods", test_sll_dunders)

    def test_sll_visualization():
        sll = SinglyLinkedList.from_list([10, 20, 30, 40])
        viz = sll.visualize(style="ascii")
        print(f"\n  ASCII Visualization:\n   {viz}")

        debug_info = sll.debug()
        print(f"  Debug info: {debug_info.get('size')} nodes, head: {debug_info.get('head')}")
        return True

    runner.run_test("Visualization", test_sll_visualization)

    # ============ DOUBLY LINKED LIST TESTS ============
    print_section("DOUBLY LINKED LIST", "-")

    def test_dll_insertion():
        dll = DoublyLinkedList.from_list([10, 20, 30])
        dll.insert(25, after=20)
        assert dll.to_list() == [10, 20, 25, 30]

        dll.insert(5, before=10)
        assert dll.to_list() == [5, 10, 20, 25, 30]
        print(f"  DLL: {dll.to_list()}")
        return True

    runner.run_test("DLL Insertion", test_dll_insertion)

    def test_dll_bidirectional():
        dll = DoublyLinkedList.from_list([1, 2, 3, 4, 5])
        val = dll.get(2, from_end=True)
        assert val == 3
        print(f"  Get from end (position 2 from end): {val}")
        return True

    runner.run_test("Bidirectional Access", test_dll_bidirectional)

    def test_dll_swap():
        dll = DoublyLinkedList.from_list([1, 2, 3, 4, 5])
        dll.swap(pos1=1, pos2=3)
        assert dll.to_list() == [1, 4, 3, 2, 5]
        print(f"  After swap positions 1 and 3: {dll.to_list()}")
        return True

    runner.run_test("Swap", test_dll_swap)

    # ============ CIRCULAR LINKED LIST TESTS ============
    print_section("CIRCULAR LINKED LIST", "-")

    def test_cll_creation():
        cll = CircularLinkedList.from_list([1, 2, 3, 4, 5])
        assert len(cll) == 5
        print(f"  CLL size: {len(cll)}")
        return True

    runner.run_test("CLL Creation", test_cll_creation)

    def test_cll_rotation():
        cll = CircularLinkedList.from_list([1, 2, 3, 4, 5])
        cll.rotate(shift=2)
        assert cll.to_list() == [4, 5, 1, 2, 3]
        print(f"  CLL rotate: {cll.to_list()}")
        return True

    runner.run_test("CLL Rotation", test_cll_rotation)

    # ============ EDGE CASES & ERROR HANDLING ============
    print_section("EDGE CASES & ERROR HANDLING", "-")

    def test_empty_operations():
        sll = SinglyLinkedList.create()
        try:
            sll.get(0)
            assert False, "Should raise EmptyStructureError"
        except EmptyStructureError:
            print("  Empty list correctly raises EmptyStructureError")

        try:
            sll.delete(position=0)
            assert False
        except EmptyStructureError:
            print("  Delete on empty raises EmptyStructureError")
        return True

    runner.run_test("Empty Operations", test_empty_operations)

    def test_invalid_positions():
        sll = SinglyLinkedList.from_list([1, 2, 3])
        try:
            sll.get(10)
            assert False
        except IndexOutOfRangeError:
            print("  Invalid position correctly caught")
        return True

    runner.run_test("Invalid Positions", test_invalid_positions)

    def test_missing_value():
        sll = SinglyLinkedList.from_list([1, 2, 3])
        try:
            sll.index(99)
            assert False
        except ValueNotFoundError:
            print("  Missing value correctly raises exception")
        return True

    runner.run_test("Missing Value", test_missing_value)

    # ============ PERFORMANCE TESTS ============
    print_section("PERFORMANCE BENCHMARKS", "-")

    def test_traversal_performance():
        sll = SinglyLinkedList.from_list(list(range(100000)))
        start = time.perf_counter()
        result = sll.to_list()
        list_time = time.perf_counter() - start

        lst = list(range(100000))
        start = time.perf_counter()
        result2 = lst.copy()
        copy_time = time.perf_counter() - start

        print(f"  SLL traversal 100k: {list_time*1000:.2f}ms")
        print(f"  List copy 100k: {copy_time*1000:.2f}ms")
        return True

    runner.run_test("Traversal Performance", test_traversal_performance)

    # ============ MEMORY USAGE TESTS ============
    print_section("MEMORY USAGE", "-")

    def test_memory_efficiency():
        import sys
        from pkstruct.linear.linked_lists.nodes import SinglyNode

        s_node = SinglyNode(10)
        s_size = sys.getsizeof(s_node)

        print(f"  SinglyNode size: {s_size} bytes (with __slots__)")

        class RegularNode:
            def __init__(self, value):
                self.value = value
                self.next = None

        r_node = RegularNode(10)
        r_size = sys.getsizeof(r_node) + sys.getsizeof(r_node.__dict__)
        print(f"  Regular node (no __slots__): ~{r_size} bytes")
        print(f"  Memory saved: {(1 - s_size/r_size)*100:.1f}%")

        assert s_size < r_size
        return True

    runner.run_test("Memory Efficiency", test_memory_efficiency)

    # ============ SERIALIZATION TESTS ============
    print_section("SERIALIZATION", "-")

    def test_json_serialization():
        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        json_str = sll.to_json()

        sll2 = SinglyLinkedList.from_json(json_str)
        assert sll == sll2

        print(f"  JSON roundtrip: {json_str}")
        return True

    runner.run_test("JSON Serialization", test_json_serialization)

    # ============ THREADING TESTS ============
    print_section("THREADING SAFETY", "-")

    def test_thread_safety():
        import threading

        sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
        errors = []

        def worker(worker_id):
            try:
                for i in range(100):
                    sll.insert(i, position=0)
                    sll.delete(position=0)
                    sll.to_list()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        print(f"  Thread safety test passed (10 threads, 100 ops each)")
        return True

    runner.run_test("Thread Safety", test_thread_safety)

    # ============ EXAMPLE USAGE SHOWCASE ============
    print_section("EXAMPLE USAGE SHOWCASE", "-")

    def showcase_real_world_use():
        print("\n  Real-world examples:\n")

        playlist = CircularLinkedList.from_list([
            "Song A", "Song B", "Song C", "Song D"
        ])
        print(f"    Playlist: {' -> '.join(playlist.to_list())} -> (back to head)")

        history = SinglyLinkedList()
        pages = ["Home", "Products", "About", "Contact"]
        for page in pages:
            history.insert(page)
        print(f"    Browser history: {' <- '.join(history.to_list())}")

        print("    LRU Cache structure ready")

        return True

    runner.run_test("Real-world Examples", showcase_real_world_use)

    return runner


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PKSTRUCT.LINEAR COMPREHENSIVE TEST SUITE")
    print("="*70)

    runner = comprehensive_tests()
    runner.summary()

    status = 0 if len(runner.failures) == 0 else 1
    sys.exit(status)

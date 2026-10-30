"""DSA King System: curated Easy / Medium / Hard problem statements and Python judge tests.

Integration with existing app.py (after existing TESTS, get_tests and /api/problems):

    from dsa_problem_bank import PROBLEMS as CURATED_PROBLEMS, TESTS as CURATED_TESTS
    TESTS.update(CURATED_TESTS)

In get_tests(problem_id), the existing `if pid in TESTS: return TESTS[pid]`
will then recognize these problems. Add the CURATED_PROBLEMS entries to the
JSON returned by /api/problems, and update your frontend's statement renderer
to read `description`, `example`, `constraints`, `difficulty`, `function`.

The existing frontend may require further changes: simply copying this module
into the folder does NOT automatically display these new problems. Python
solution signatures are `def solve(...):` as documented per problem.

Security: existing Python judge execution must be sandboxed before allowing
untrusted users to submit code on a public website.
"""

PROBLEMS = [
    # EASY
    dict(id=2001,title='Contains Duplicate',difficulty='Easy',topic='Arrays / Hash Set',function='solve(nums)',description='Return True if any value appears at least twice in nums; otherwise return False.',example='nums=[1,2,3,1] -> True',constraints='1 <= len(nums) <= 100000'),
    dict(id=2002,title='Valid Anagram',difficulty='Easy',topic='Strings / Frequency',function='solve(s, t)',description='Return True if t is an anagram of s, using exactly the same characters and frequencies.',example='s="anagram", t="nagaram" -> True',constraints='0 <= len(s),len(t) <= 100000; lowercase English letters'),
    dict(id=2003,title='Best Time to Buy and Sell Stock',difficulty='Easy',topic='Arrays / Greedy',function='solve(prices)',description='Choose one day to buy and a later day to sell. Return the maximum possible profit, or 0 if no profit is possible.',example='prices=[7,1,5,3,6,4] -> 5',constraints='1 <= len(prices) <= 100000'),
    dict(id=2004,title='Move Zeroes',difficulty='Easy',topic='Two Pointers',function='solve(nums)',description='Return a new array with all zeroes moved to the end, preserving the relative order of nonzero elements.',example='nums=[0,1,0,3,12] -> [1,3,12,0,0]',constraints='0 <= len(nums) <= 100000'),
    dict(id=2005,title='Missing Number',difficulty='Easy',topic='Math / XOR',function='solve(nums)',description='An array of n distinct integers contains numbers from 0 to n with one missing. Return the missing number.',example='nums=[3,0,1] -> 2',constraints='1 <= len(nums) <= 100000'),
    dict(id=2006,title='Climbing Stairs',difficulty='Easy',topic='Dynamic Programming',function='solve(n)',description='You may climb 1 or 2 steps at a time. Return the number of distinct ways to reach step n.',example='n=4 -> 5',constraints='1 <= n <= 40'),
    # MEDIUM
    dict(id=2101,title='Longest Substring Without Repeating Characters',difficulty='Medium',topic='Sliding Window',function='solve(s)',description='Return the length of the longest contiguous substring containing no repeated characters.',example='s="abcabcbb" -> 3',constraints='0 <= len(s) <= 100000'),
    dict(id=2102,title='Product of Array Except Self',difficulty='Medium',topic='Prefix / Suffix',function='solve(nums)',description='Return an array where result[i] equals the product of all nums elements except nums[i]. Do not use division.',example='nums=[1,2,3,4] -> [24,12,8,6]',constraints='2 <= len(nums) <= 100000'),
    dict(id=2103,title='Container With Most Water',difficulty='Medium',topic='Two Pointers',function='solve(height)',description='Choose two vertical lines that form a container. Return the maximum area of water they can hold.',example='height=[1,8,6,2,5,4,8,3,7] -> 49',constraints='2 <= len(height) <= 100000'),
    dict(id=2104,title='Coin Change',difficulty='Medium',topic='Dynamic Programming',function='solve(coins, amount)',description='Return the minimum number of coins needed to form amount, with unlimited copies of each denomination. Return -1 if impossible.',example='coins=[1,2,5], amount=11 -> 3',constraints='1 <= len(coins) <= 12; 0 <= amount <= 10000; positive denominations'),
    dict(id=2105,title='Search in Rotated Sorted Array',difficulty='Medium',topic='Binary Search',function='solve(nums, target)',description='A strictly increasing array was rotated at an unknown pivot. Return the index of target, or -1 if absent.',example='nums=[4,5,6,7,0,1,2], target=0 -> 4',constraints='1 <= len(nums) <= 100000; distinct integers'),
    dict(id=2106,title='Number of Islands',difficulty='Medium',topic='Graph / DFS / BFS',function='solve(grid)',description='Given a rectangular grid of strings "1" (land) and "0" (water), return the number of 4-directionally connected islands.',example='grid=[["1","1","0"],["0","1","0"],["0","0","1"]] -> 2',constraints='1 <= rows,cols <= 200'),
    # HARD
    dict(id=2201,title='Median of Two Sorted Arrays',difficulty='Hard',topic='Binary Search',function='solve(nums1, nums2)',description='Return the median of two sorted integer arrays. Aim for O(log(min(m,n))) time. The combined array is nonempty.',example='nums1=[1,3], nums2=[2] -> 2.0',constraints='0 <= m,n <= 1000; m+n >= 1'),
    dict(id=2202,title='Minimum Window Substring',difficulty='Hard',topic='Sliding Window',function='solve(s, t)',description='Return the shortest substring of s containing all characters of t, including duplicates. Return "" if none exists.',example='s="ADOBECODEBANC", t="ABC" -> "BANC"',constraints='1 <= len(s),len(t) <= 100000'),
    dict(id=2203,title='Edit Distance',difficulty='Hard',topic='Dynamic Programming',function='solve(word1, word2)',description='Return the minimum number of insertions, deletions, and replacements to transform word1 into word2.',example='word1="horse", word2="ros" -> 3',constraints='0 <= len(word1),len(word2) <= 500'),
    dict(id=2204,title='Regular Expression Matching',difficulty='Hard',topic='Dynamic Programming',function='solve(s, p)',description='Return True if pattern p matches the entire string s. A dot matches any one character; an asterisk matches zero or more of the immediately preceding element.',example='s="aab", p="c*a*b" -> True',constraints='0 <= len(s) <= 20; 1 <= len(p) <= 30; valid pattern'),
    dict(id=2205,title='Burst Balloons',difficulty='Hard',topic='Interval DP',function='solve(nums)',description='Burst balloons in any order. Bursting index i gains left*nums[i]*right using currently adjacent balloons; nonexistent neighbors have value 1. Return the maximum coins.',example='nums=[3,1,5,8] -> 167',constraints='1 <= len(nums) <= 300; 0 <= nums[i] <= 100'),
    dict(id=2206,title='Sliding Window Maximum',difficulty='Hard',topic='Monotonic Deque',function='solve(nums, k)',description='Return the maximum value in every contiguous window of size k.',example='nums=[1,3,-1,-3,5,3,6,7], k=3 -> [3,3,5,5,6,7]',constraints='1 <= k <= len(nums) <= 100000'),
]

# Format compatible with the current DSA King System judge: each test is
# ([positional_arguments], expected_return_value).
TESTS = {
 2001:[([[1,2,3,1]],True),([[1,2,3,4]],False),([[1,1,1,3,3,4,3,2,4,2]],True)],
 2002:[(['anagram','nagaram'],True),(['rat','car'],False),(['',''],True),(['a','aa'],False)],
 2003:[([[7,1,5,3,6,4]],5),([[7,6,4,3,1]],0),([[1,2]],1)],
 2004:[([[0,1,0,3,12]],[1,3,12,0,0]),([[0,0]],[0,0]),([[4,5,6]],[4,5,6])],
 2005:[([[3,0,1]],2),([[0,1]],2),([[9,6,4,2,3,5,7,0,1]],8)],
 2006:[([1],1),([2],2),([4],5),([10],89)],
 2101:[(['abcabcbb'],3),(['bbbbb'],1),(['pwwkew'],3),([''],0)],
 2102:[([[1,2,3,4]],[24,12,8,6]),([[-1,1,0,-3,3]],[0,0,9,0,0]),([[2,3]],[3,2])],
 2103:[([[1,8,6,2,5,4,8,3,7]],49),([[1,1]],1),([[4,3,2,1,4]],16)],
 2104:[([[1,2,5],11],3),([[2],3],-1),([[1],0],0),([[2,5,10,1],27],4)],
 2105:[([[4,5,6,7,0,1,2],0],4),([[4,5,6,7,0,1,2],3],-1),([[1],0],-1),([[1,3],3],1)],
 2106:[([[["1","1","0"],["0","1","0"],["0","0","1"]]],2),([[["1","1"],["1","1"]]],1),([[["0","0"]]],0)],
 2201:[([[1,3],[2]],2.0),([[1,2],[3,4]],2.5),([[],[1]],1.0),([[0,0],[0,0]],0.0)],
 2202:[(['ADOBECODEBANC','ABC'],'BANC'),(['a','a'],'a'),(['a','aa'],''),(['aa','aa'],'aa')],
 2203:[(['horse','ros'],3),(['intention','execution'],5),(['','abc'],3),(['abc','abc'],0)],
 2204:[(['aa','a'],False),(['aa','a*'],True),(['ab','.*'],True),(['aab','c*a*b'],True),(['mississippi','mis*is*p*.'],False)],
 2205:[([[3,1,5,8]],167),([[1,5]],10),([[1]],1),([[0,1]],1)],
 2206:[([[1,3,-1,-3,5,3,6,7],3],[3,3,5,5,6,7]),([[1],1],[1]),([[9,8,7],2],[9,8])],
}

def grouped_problems():
    """Return difficulty-grouped public problem statements."""
    return {difficulty:[p.copy() for p in PROBLEMS if p['difficulty']==difficulty]
            for difficulty in ('Easy','Medium','Hard')}

if __name__ == '__main__':
    from collections import Counter
    print('DSA King System curated problems:', dict(Counter(p['difficulty'] for p in PROBLEMS)))
    print('Test sets:', len(TESTS))


# ADDITIONAL HARD PROBLEMS — DSA King System
# These IDs are unique and are automatically included by the existing app.py import.
PROBLEMS.extend([
    dict(id=2207, title="First Missing Positive", difficulty="Hard",
         topic="Arrays / In-place Hashing", function="solve(nums)",
         description="Given an unsorted integer array, find the smallest positive integer that is not present. Aim for O(n) time and O(1) auxiliary space. Negative values and zero do not count.",
         example="Input: nums=[3,4,-1,1] | Output: 2 | Explanation: 1 is present but 2 is missing.",
         constraints="1 <= len(nums) <= 100000; -2^31 <= nums[i] <= 2^31-1"),
    dict(id=2208, title="Longest Valid Parentheses", difficulty="Hard",
         topic="Stack / Dynamic Programming", function="solve(s)",
         description="Given a string containing only '(' and ')', return the length of its longest contiguous substring that forms a valid sequence of matched parentheses.",
         example='Input: s=")()())" | Output: 4 | Explanation: The substring "()()" is valid.',
         constraints="0 <= len(s) <= 30000; s contains only '(' and ')'"),
    dict(id=2209, title="Distinct Subsequences", difficulty="Hard",
         topic="Dynamic Programming / Strings", function="solve(s, t)",
         description="Count how many distinct ways the string t can be formed by deleting zero or more characters from s without changing the order of the remaining characters.",
         example='Input: s="rabbbit", t="rabbit" | Output: 3',
         constraints="0 <= len(s),len(t) <= 1000; result fits in a signed 32-bit integer"),
    dict(id=2210, title="Split Array Largest Sum", difficulty="Hard",
         topic="Binary Search / Greedy", function="solve(nums, k)",
         description="Split a nonnegative integer array into exactly k nonempty contiguous subarrays. Minimize the largest subarray sum and return that minimum.",
         example="Input: nums=[7,2,5,10,8], k=2 | Output: 18 | Explanation: [7,2,5] and [10,8].",
         constraints="1 <= k <= len(nums) <= 1000; 0 <= nums[i] <= 1000000"),
    dict(id=2211, title="Count of Smaller Numbers After Self", difficulty="Hard",
         topic="Merge Sort / Fenwick Tree", function="solve(nums)",
         description="For every index i, count the elements strictly smaller than nums[i] that appear to its right. Return the counts in original order.",
         example="Input: nums=[5,2,6,1] | Output: [2,1,1,0]",
         constraints="1 <= len(nums) <= 100000; -10000 <= nums[i] <= 10000"),
    dict(id=2212, title="Maximal Rectangle", difficulty="Hard",
         topic="Monotonic Stack / Matrix", function="solve(matrix)",
         description="Given a rectangular binary matrix of strings '0' and '1', find the area of the largest axis-aligned rectangle containing only '1' cells.",
         example='Input: matrix=[["1","0","1"],["1","1","1"]] | Output: 3',
         constraints="1 <= rows,cols <= 200; each cell is '0' or '1'"),
    dict(id=2213, title="N-Queens II", difficulty="Hard",
         topic="Backtracking / Bitmasks", function="solve(n)",
         description="Place n queens on an n-by-n chessboard so that no two queens share a row, column, or diagonal. Return the number of distinct valid arrangements.",
         example="Input: n=4 | Output: 2",
         constraints="1 <= n <= 9"),
    dict(id=2214, title="Shortest Path Visiting All Nodes", difficulty="Hard",
         topic="Graph / BFS / Bitmask DP", function="solve(graph)",
         description="Given an undirected connected graph as a zero-indexed adjacency list, find the minimum number of edges in a walk that visits every node at least once. You may start anywhere and revisit nodes.",
         example="Input: graph=[[1,2,3],[0],[0],[0]] | Output: 4",
         constraints="1 <= len(graph) <= 12; graph is connected, undirected, and has no self-loops"),
])

TESTS.update({
    2207: [([[1,2,0]],3), ([[3,4,-1,1]],2), ([[7,8,9,11,12]],1), ([[1]],2), ([[-1,-2]],1)],
    2208: [(['(()'],2), ([')()())'],4), ([''],0), (['()(())'],6), (['())(()'],2)],
    2209: [(['rabbbit','rabbit'],3), (['babgbag','bag'],5), (['abc',''],1), (['','a'],0), (['aaa','aa'],3)],
    2210: [([[7,2,5,10,8],2],18), ([[1,2,3,4,5],2],9), ([[1,4,4],3],4), ([[0,0,0],2],0)],
    2211: [([[5,2,6,1]],[2,1,1,0]), ([[-1]],[0]), ([[-1,-1]],[0,0]), ([[3,2,1]],[2,1,0]), ([[1,2,3]],[0,0,0])],
    2212: [([[["1","0","1"],["1","1","1"]]],3), ([[["0"]]],0), ([[["1"]]],1), ([[["1","1"],["1","1"]]],4), ([[["1","0"],["1","1"],["1","1"]]],3)],
    2213: [([1],1), ([2],0), ([3],0), ([4],2), ([5],10), ([6],4)],
    2214: [([[[1,2,3],[0],[0],[0]]],4), ([[[1],[0,2,4],[1,3,4],[2],[1,2]]],4), ([[[]]],0), ([[[1],[0]]],1), ([[[1],[0,2],[1]]],2)],
})

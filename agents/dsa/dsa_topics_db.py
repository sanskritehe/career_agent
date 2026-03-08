# DSA Topics Database - Similar to NeetCode
# Comprehensive mapping of all DSA topics with problems and metadata

DSA_TOPICS_MAP = {
    "Arrays & Hashing": {
        "description": "Master fundamental array operations and hash-based problems",
        "estimated_weeks": 3,
        "problems": [
            {"id": "217", "name": "Contains Duplicate", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/contains-duplicate/", "tags": ["Array", "Hash Set"]},
            {"id": "242", "name": "Valid Anagram", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/valid-anagram/", "tags": ["Array", "Hash"]},
            {"id": "1", "name": "Two Sum", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/two-sum/", "tags": ["Array", "Hash Map"]},
            {"id": "49", "name": "Group Anagrams", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/group-anagrams/", "tags": ["Hash Map", "String"]},
            {"id": "347", "name": "Top K Frequent Elements", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/top-k-frequent-elements/", "tags": ["Hash Map", "Heap"]},
            {"id": "238", "name": "Product of Array Except Self", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/product-of-array-except-self/", "tags": ["Array", "Prefix/Suffix"]},
            {"id": "36", "name": "Valid Sudoku", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/valid-sudoku/", "tags": ["Hash Set", "Matrix"]},
            {"id": "128", "name": "Longest Consecutive", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/longest-consecutive/", "tags": ["Hash Set", "Array"]},
        ]
    },
    "Two Pointers": {
        "description": "Solve array and string problems using two pointer technique",
        "estimated_weeks": 2,
        "problems": [
            {"id": "125", "name": "Valid Palindrome", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/valid-palindrome/", "tags": ["Two Pointers", "String"]},
            {"id": "167", "name": "Two Sum II Input Array Is Sorted", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/", "tags": ["Two Pointers", "Array"]},
            {"id": "15", "name": "3Sum", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/3sum/", "tags": ["Two Pointers", "Sorting"]},
            {"id": "11", "name": "Container With Most Water", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/container-with-most-water/", "tags": ["Two Pointers", "Array"]},
            {"id": "42", "name": "Trapping Rain Water", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/trapping-rain-water/", "tags": ["Two Pointers", "Array", "DP"]},
        ]
    },
    "Sliding Window": {
        "description": "Optimize array and string problems using sliding window",
        "estimated_weeks": 2,
        "problems": [
            {"id": "121", "name": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "tags": ["Sliding Window", "One Pass"]},
            {"id": "3", "name": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "tags": ["Sliding Window", "Hash Map"]},
            {"id": "76", "name": "Minimum Window Substring", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/minimum-window-substring/", "tags": ["Sliding Window", "Hash Map"]},
            {"id": "209", "name": "Minimum Size Subarray Sum", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/minimum-size-subarray-sum/", "tags": ["Sliding Window", "Array"]},
            {"id": "239", "name": "Sliding Window Maximum", "difficulty": "Hard", "time_estimate_mins": 40, "leetcode_link": "https://leetcode.com/problems/sliding-window-maximum/", "tags": ["Sliding Window", "Deque"]},
        ]
    },
    "Stack": {
        "description": "Master stack-based problems and applications",
        "estimated_weeks": 2,
        "problems": [
            {"id": "20", "name": "Valid Parentheses", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/valid-parentheses/", "tags": ["Stack", "String"]},
            {"id": "155", "name": "Min Stack", "difficulty": "Medium", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/min-stack/", "tags": ["Stack", "Design"]},
            {"id": "150", "name": "Evaluate Reverse Polish Notation", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/evaluate-reverse-polish-notation/", "tags": ["Stack", "Math"]},
            {"id": "22", "name": "Generate Parentheses", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/generate-parentheses/", "tags": ["Stack", "Backtracking"]},
            {"id": "739", "name": "Daily Temperatures", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/daily-temperatures/", "tags": ["Stack", "Array"]},
        ]
    },
    "Linked List": {
        "description": "Understand linked list operations and manipulations",
        "estimated_weeks": 3,
        "problems": [
            {"id": "206", "name": "Reverse Linked List", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/reverse-linked-list/", "tags": ["Linked List"]},
            {"id": "21", "name": "Merge Two Sorted Lists", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/merge-two-sorted-lists/", "tags": ["Linked List"]},
            {"id": "141", "name": "Linked List Cycle", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/linked-list-cycle/", "tags": ["Linked List", "Two Pointers"]},
            {"id": "2", "name": "Add Two Numbers", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/add-two-numbers/", "tags": ["Linked List", "Math"]},
            {"id": "19", "name": "Remove Nth Node From End of List", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/", "tags": ["Linked List", "Two Pointers"]},
            {"id": "143", "name": "Reorder List", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/reorder-list/", "tags": ["Linked List"]},
            {"id": "25", "name": "Reverse Nodes in k-Group", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/reverse-nodes-in-k-group/", "tags": ["Linked List"]},
        ]
    },
    "Binary Search": {
        "description": "Master binary search and its applications",
        "estimated_weeks": 2,
        "problems": [
            {"id": "704", "name": "Binary Search", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/binary-search/", "tags": ["Binary Search"]},
            {"id": "74", "name": "Search a 2D Matrix", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/search-a-2d-matrix/", "tags": ["Binary Search", "Matrix"]},
            {"id": "33", "name": "Search in Rotated Sorted Array", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/search-in-rotated-sorted-array/", "tags": ["Binary Search"]},
            {"id": "153", "name": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/", "tags": ["Binary Search"]},
            {"id": "4", "name": "Median of Two Sorted Arrays", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/median-of-two-sorted-arrays/", "tags": ["Binary Search", "Array"]},
        ]
    },
    "Trees": {
        "description": "Understand tree traversals and tree-based problems",
        "estimated_weeks": 4,
        "problems": [
            {"id": "226", "name": "Invert Binary Tree", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/invert-binary-tree/", "tags": ["Tree", "DFS"]},
            {"id": "104", "name": "Maximum Depth of Binary Tree", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "tags": ["Tree", "DFS/BFS"]},
            {"id": "100", "name": "Same Tree", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/same-tree/", "tags": ["Tree", "DFS"]},
            {"id": "110", "name": "Balanced Binary Tree", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/balanced-binary-tree/", "tags": ["Tree", "DFS"]},
            {"id": "572", "name": "Subtree of Another Tree", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/subtree-of-another-tree/", "tags": ["Tree", "DFS"]},
            {"id": "235", "name": "Lowest Common Ancestor of BST", "difficulty": "Medium", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/", "tags": ["Tree", "BST"]},
            {"id": "102", "name": "Binary Tree Level Order Traversal", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/binary-tree-level-order-traversal/", "tags": ["Tree", "BFS"]},
            {"id": "199", "name": "Binary Tree Right Side View", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/binary-tree-right-side-view/", "tags": ["Tree", "BFS"]},
            {"id": "98", "name": "Validate Binary Search Tree", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/validate-binary-search-tree/", "tags": ["Tree", "BST", "DFS"]},
            {"id": "105", "name": "Construct Binary Tree from Preorder and Inorder Traversal", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/", "tags": ["Tree", "DFS"]},
            {"id": "297", "name": "Serialize and Deserialize Binary Tree", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/", "tags": ["Tree", "DFS", "BFS"]},
        ]
    },
    "Graphs": {
        "description": "Learn graph representations and traversal algorithms",
        "estimated_weeks": 4,
        "problems": [
            {"id": "200", "name": "Number of Islands", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/number-of-islands/", "tags": ["Graph", "DFS/BFS"]},
            {"id": "133", "name": "Clone Graph", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/clone-graph/", "tags": ["Graph", "DFS/BFS"]},
            {"id": "207", "name": "Course Schedule", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/course-schedule/", "tags": ["Graph", "Topological Sort"]},
            {"id": "210", "name": "Course Schedule II", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/course-schedule-ii/", "tags": ["Graph", "Topological Sort"]},
            {"id": "417", "name": "Pacific Atlantic Water Flow", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/pacific-atlantic-water-flow/", "tags": ["Graph", "DFS"]},
            {"id": "127", "name": "Word Ladder", "difficulty": "Hard", "time_estimate_mins": 40, "leetcode_link": "https://leetcode.com/problems/word-ladder/", "tags": ["Graph", "BFS"]},
            {"id": "269", "name": "Alien Dictionary", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/alien-dictionary/", "tags": ["Graph", "Topological Sort"]},
        ]
    },
    "Heap": {
        "description": "Master heap data structure and priority queues",
        "estimated_weeks": 2,
        "problems": [
            {"id": "703", "name": "Kth Largest Element in a Stream", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/kth-largest-element-in-a-stream/", "tags": ["Heap", "Design"]},
            {"id": "1046", "name": "Last Stone Weight", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/last-stone-weight/", "tags": ["Heap"]},
            {"id": "973", "name": "K Closest Points to Origin", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/k-closest-points-to-origin/", "tags": ["Heap"]},
            {"id": "295", "name": "Find Median from Data Stream", "difficulty": "Hard", "time_estimate_mins": 40, "leetcode_link": "https://leetcode.com/problems/find-median-from-data-stream/", "tags": ["Heap", "Design"]},
        ]
    },
    "Dynamic Programming": {
        "description": "Master DP with overlapping subproblems and optimal substructure",
        "estimated_weeks": 5,
        "problems": [
            {"id": "70", "name": "Climbing Stairs", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/climbing-stairs/", "tags": ["DP"]},
            {"id": "53", "name": "Maximum Subarray", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/maximum-subarray/", "tags": ["DP", "Greedy"]},
            {"id": "198", "name": "House Robber", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/house-robber/", "tags": ["DP"]},
            {"id": "300", "name": "Longest Increasing Subsequence", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/longest-increasing-subsequence/", "tags": ["DP"]},
            {"id": "1143", "name": "Longest Common Subsequence", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/longest-common-subsequence/", "tags": ["DP", "2D DP"]},
            {"id": "139", "name": "Word Break", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/word-break/", "tags": ["DP"]},
            {"id": "322", "name": "Coin Change", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/coin-change/", "tags": ["DP"]},
            {"id": "416", "name": "Partition Equal Subset Sum", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/partition-equal-subset-sum/", "tags": ["DP", "Array"]},
            {"id": "312", "name": "Burst Balloons", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/burst-balloons/", "tags": ["DP", "2D DP"]},
            {"id": "32", "name": "Longest Valid Parentheses", "difficulty": "Hard", "time_estimate_mins": 40, "leetcode_link": "https://leetcode.com/problems/longest-valid-parentheses/", "tags": ["DP", "Stack"]},
        ]
    },
    "Greedy": {
        "description": "Learn greedy algorithms and optimal choice problems",
        "estimated_weeks": 2,
        "problems": [
            {"id": "455", "name": "Assign Cookies", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/assign-cookies/", "tags": ["Greedy", "Sorting"]},
            {"id": "435", "name": "Non-overlapping Intervals", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/non-overlapping-intervals/", "tags": ["Greedy", "Sorting"]},
            {"id": "134", "name": "Gas Station", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/gas-station/", "tags": ["Greedy"]},
            {"id": "678", "name": "Valid Parenthesis String", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/valid-parenthesis-string/", "tags": ["Greedy"]},
        ]
    },
    "Intervals": {
        "description": "Master interval-based problems and scheduling",
        "estimated_weeks": 2,
        "problems": [
            {"id": "228", "name": "Summary Ranges", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/summary-ranges/", "tags": ["Array"]},
            {"id": "57", "name": "Insert Interval", "difficulty": "Medium", "time_estimate_mins": 35, "leetcode_link": "https://leetcode.com/problems/insert-interval/", "tags": ["Intervals", "Array"]},
            {"id": "56", "name": "Merge Intervals", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/merge-intervals/", "tags": ["Intervals", "Sorting"]},
            {"id": "452", "name": "Minimum Number of Arrows to Burst Balloons", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/", "tags": ["Greedy", "Sorting"]},
        ]
    },
    "Math & Geometry": {
        "description": "Learn number theory, combinatorics, and geometry problems",
        "estimated_weeks": 2,
        "problems": [
            {"id": "50", "name": "Pow(x, n)", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/powx-n/", "tags": ["Math", "Recursion"]},
            {"id": "43", "name": "Multiply Strings", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/multiply-strings/", "tags": ["Math", "String"]},
            {"id": "202", "name": "Happy Number", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/happy-number/", "tags": ["Math", "Hash"]},
            {"id": "263", "name": "Ugly Number", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/ugly-number/", "tags": ["Math"]},
        ]
    },
    "Strings": {
        "description": "Master string manipulation and pattern matching",
        "estimated_weeks": 3,
        "problems": [
            {"id": "205", "name": "Isomorphic Strings", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/isomorphic-strings/", "tags": ["String", "Hash"]},
            {"id": "392", "name": "Is Subsequence", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/is-subsequence/", "tags": ["String", "Two Pointers"]},
            {"id": "207", "name": "Longest Palindromic Substring", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/longest-palindromic-substring/", "tags": ["String", "DP"]},
            {"id": "10", "name": "Regular Expression Matching", "difficulty": "Hard", "time_estimate_mins": 45, "leetcode_link": "https://leetcode.com/problems/regular-expression-matching/", "tags": ["String", "DP", "Recursion"]},
        ]
    },
    "Backtracking": {
        "description": "Master backtracking for combinatorial and permutation problems",
        "estimated_weeks": 3,
        "problems": [
            {"id": "78", "name": "Subsets", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/subsets/", "tags": ["Backtracking", "Array"]},
            {"id": "46", "name": "Permutations", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/permutations/", "tags": ["Backtracking"]},
            {"id": "39", "name": "Combination Sum", "difficulty": "Medium", "time_estimate_mins": 30, "leetcode_link": "https://leetcode.com/problems/combination-sum/", "tags": ["Backtracking"]},
            {"id": "51", "name": "N-Queens", "difficulty": "Hard", "time_estimate_mins": 40, "leetcode_link": "https://leetcode.com/problems/n-queens/", "tags": ["Backtracking"]},
        ]
    },
    "Bit Manipulation": {
        "description": "Learn bit operations and bitwise techniques",
        "estimated_weeks": 1,
        "problems": [
            {"id": "136", "name": "Single Number", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/single-number/", "tags": ["Bit Manipulation"]},
            {"id": "191", "name": "Number of 1 Bits", "difficulty": "Easy", "time_estimate_mins": 15, "leetcode_link": "https://leetcode.com/problems/number-of-1-bits/", "tags": ["Bit Manipulation"]},
            {"id": "338", "name": "Counting Bits", "difficulty": "Easy", "time_estimate_mins": 20, "leetcode_link": "https://leetcode.com/problems/counting-bits/", "tags": ["Bit Manipulation", "DP"]},
            {"id": "371", "name": "Sum of Two Integers", "difficulty": "Medium", "time_estimate_mins": 25, "leetcode_link": "https://leetcode.com/problems/sum-of-two-integers/", "tags": ["Bit Manipulation"]},
        ]
    },
}

# Time estimation for 3-6 month plans
TIME_PLAN_CONFIGS = {
    "3_months": {
        "total_days": 90,
        "daily_requirement": "1 Easy + 1 Medium",
        "total_problems": 180,
        "description": "Intensive 3-month plan - 1 Easy + 1 Medium per day"
    },
    "6_months": {
        "total_days": 180,
        "daily_requirement": "1 Easy + 1 Medium",
        "total_problems": 360,
        "description": "Moderate 6-month plan - 1 Easy + 1 Medium per day"
    },
}

def get_easy_and_medium_problems():
    """Get all easy and medium problems separately"""
    easy = get_easy_problems()
    medium = get_medium_problems()
    return easy, medium

def generate_daily_schedule(months):
    """
    Generate a daily learning schedule with 1 easy and 1 medium per day
    
    Args:
        months: 3 or 6
    
    Returns:
        List of daily assignments with problems
    """
    time_key = f"{months}_months"
    if time_key not in TIME_PLAN_CONFIGS:
        return None
    
    config = TIME_PLAN_CONFIGS[time_key]
    total_days = config['total_days']
    
    # Get all easy and medium problems with their topics
    easy_problems = []
    medium_problems = []
    
    # Gather all easy and medium problems with topic info
    for topic_name, topic_data in DSA_TOPICS_MAP.items():
        topic_problems = topic_data.get('problems', [])
        for problem in topic_problems:
            problem_with_topic = problem.copy()
            problem_with_topic['topic'] = topic_name
            
            if problem['difficulty'] == 'Easy':
                easy_problems.append(problem_with_topic)
            elif problem['difficulty'] == 'Medium':
                medium_problems.append(problem_with_topic)
    
    # Create daily schedule
    daily_schedule = []
    
    for day in range(1, total_days + 1):
        # Cycle through problems if we don't have enough
        easy_idx = (day - 1) % len(easy_problems) if easy_problems else 0
        medium_idx = (day - 1) % len(medium_problems) if medium_problems else 0
        
        easy_prob = easy_problems[easy_idx] if easy_problems else None
        medium_prob = medium_problems[medium_idx] if medium_problems else None
        
        daily_assignment = {
            "day": day,
            "easy_problem": easy_prob,
            "easy_topic": easy_prob['topic'] if easy_prob else "N/A",
            "medium_problem": medium_prob,
            "medium_topic": medium_prob['topic'] if medium_prob else "N/A",
            "completed_easy": False,
            "completed_medium": False
        }
        
        daily_schedule.append(daily_assignment)
    
    return daily_schedule

def get_all_topics():
    """Returns list of all DSA topics"""
    return list(DSA_TOPICS_MAP.keys())

def get_topic_problems(topic_name):
    """Returns all problems for a specific topic"""
    if topic_name in DSA_TOPICS_MAP:
        return DSA_TOPICS_MAP[topic_name]["problems"]
    return []

def get_topic_info(topic_name):
    """Returns metadata about a topic"""
    if topic_name in DSA_TOPICS_MAP:
        topic = DSA_TOPICS_MAP[topic_name].copy()
        topic["problem_count"] = len(topic["problems"])  # Count of problems
        topic.pop("problems")  # Remove the full problems list
        return topic
    return None

def count_total_problems():
    """Count total problems across all topics"""
    return sum(len(topic["problems"]) for topic in DSA_TOPICS_MAP.values())

def get_easy_problems():
    """Get all easy difficulty problems"""
    easy = []
    for topic_name, topic_data in DSA_TOPICS_MAP.items():
        for problem in topic_data["problems"]:
            if problem["difficulty"] == "Easy":
                easy.append({"topic": topic_name, **problem})
    return easy

def get_medium_problems():
    """Get all medium difficulty problems"""
    medium = []
    for topic_name, topic_data in DSA_TOPICS_MAP.items():
        for problem in topic_data["problems"]:
            if problem["difficulty"] == "Medium":
                medium.append({"topic": topic_name, **problem})
    return medium

def get_hard_problems():
    """Get all hard difficulty problems"""
    hard = []
    for topic_name, topic_data in DSA_TOPICS_MAP.items():
        for problem in topic_data["problems"]:
            if problem["difficulty"] == "Hard":
                hard.append({"topic": topic_name, **problem})
    return hard

# sample_slow.py
# Example of unoptimized python code with some style violations

def find_common_elements(list1, list2):
    # O(N*M) search complexity. Can be optimized to O(N + M) using sets.
    common = []
    for item in list1:
        if item in list2: # Linear scan inside a loop
            if item not in common:
                common.append(item)
    return common

def read_file_without_with(filepath):
    # Resource leak: open file is never explicitly closed
    f = open(filepath, 'r')
    content = f.read()
    return content

class slow_calculator: # PEP 8 naming style issue: should be PascalCase
    def __init__(self, values):
        self.values = values

    def sum_squares(self):
        # Can be simplified using generator expression
        total = 0
        for v in self.values:
            total += v ** 2
        return total

if __name__ == '__main__':
    l1 = [i for i in range(1000)]
    l2 = [i for i in range(500, 1500)]
    print(find_common_elements(l1, l2))

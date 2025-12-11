"""
Complex legacy code with multiple code smells for testing.
"""

import os
import sys
import json
import time
from datetime import datetime


class DataProcessor:
    """Legacy data processor with many issues."""
    
    def process_data(self, data, type, format, validate, transform, filter, sort, limit, offset, debug):
        """Function with too many parameters."""
        results = []
        
        if debug:
            print("Debug mode on")
        
        # Long function with high complexity
        for item in data:
            if type == "user":
                if validate:
                    if item.get("age"):
                        if item["age"] > 0:
                            if item["age"] < 150:
                                if format == "json":
                                    if transform:
                                        item["age"] = str(item["age"])
                                    results.append(item)
                                elif format == "xml":
                                    # XML formatting (not implemented)
                                    pass
            elif type == "product":
                if validate:
                    if item.get("price"):
                        if item["price"] > 0:
                            results.append(item)
        
        # More nesting
        if filter:
            filtered = []
            for r in results:
                if filter(r):
                    filtered.append(r)
            results = filtered
        
        if sort:
            results = sorted(results, key=sort)
        
        if limit:
            results = results[:limit]
        
        if offset:
            results = results[offset:]
        
        return results
    
    def calculate_stats(self, numbers):
        """Very long function."""
        total = 0
        count = 0
        min_val = None
        max_val = None
        
        for n in numbers:
            total += n
            count += 1
            if min_val is None or n < min_val:
                min_val = n
            if max_val is None or n > max_val:
                max_val = n
        
        avg = total / count if count > 0 else 0
        
        # Calculate median
        sorted_nums = sorted(numbers)
        if len(sorted_nums) % 2 == 0:
            median = (sorted_nums[len(sorted_nums)//2 - 1] + sorted_nums[len(sorted_nums)//2]) / 2
        else:
            median = sorted_nums[len(sorted_nums)//2]
        
        # Calculate variance
        variance = 0
        for n in numbers:
            variance += (n - avg) ** 2
        variance = variance / count if count > 0 else 0
        
        # Calculate std dev
        std_dev = variance ** 0.5
        
        # Calculate quartiles
        q1_idx = len(sorted_nums) // 4
        q3_idx = 3 * len(sorted_nums) // 4
        q1 = sorted_nums[q1_idx]
        q3 = sorted_nums[q3_idx]
        iqr = q3 - q1
        
        # Detect outliers
        outliers = []
        for n in numbers:
            if n < q1 - 1.5 * iqr or n > q3 + 1.5 * iqr:
                outliers.append(n)
        
        return {
            'total': total,
            'count': count,
            'min': min_val,
            'max': max_val,
            'avg': avg,
            'median': median,
            'variance': variance,
            'std_dev': std_dev,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'outliers': outliers,
        }


def complex_nested_function(a, b, c, d, e):
    """Function with deep nesting."""
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if a > b:
                            if c > d:
                                if e > 0:
                                    return "deep"
    return "shallow"


def duplicate_code_1(items):
    """First duplicate."""
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result


def duplicate_code_2(values):
    """Second duplicate."""
    result = []
    for item in values:
        if item > 0:
            result.append(item * 2)
    return result


# Global variable (code smell)
GLOBAL_CACHE = {}

def use_global():
    """Uses global variable."""
    global GLOBAL_CACHE
    GLOBAL_CACHE['last_access'] = datetime.now()
    return GLOBAL_CACHE

import pandas as pd
import datetime
from typing import Dict, Any, List, Tuple

def analyze_call_data(file_path: str) -> Dict[str, Any]:
    """
    Analyze call data from a CSV file and return results.
    
    Args:
        file_path: Path to the CSV file containing call data
        
    Returns:
        Dictionary containing analysis results
    """
    # Read the CSV file
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise Exception(f"Error reading CSV file: {e}")
    
    # Convert StartTime to datetime format
    df['StartTime'] = df['StartTime'].str.strip('"')
    df['StartTime'] = pd.to_datetime(df['StartTime'], format='%Y-%m-%d %H:%M:%S')
    
    # Define shift timings
    shifts = {
        "Shift 1": (datetime.time(5, 0), datetime.time(14, 0)),  # 5 AM - 2 PM
        "Shift 2": (datetime.time(9, 0), datetime.time(18, 0)),  # 9 AM - 6 PM
        "Shift 3": (datetime.time(11, 0), datetime.time(20, 0)), # 11 AM - 8 PM
        "Shift 4": (datetime.time(18, 0), datetime.time(5, 0))   # 6 PM - 5 AM (crosses midnight)
    }
    
    # Define resource distribution time sections and the number of resources in each
    resource_distribution = {
        "5 AM - 9 AM": {"start": datetime.time(5, 0), "end": datetime.time(9, 0), "resources": 1},
        "9 AM - 11 AM": {"start": datetime.time(9, 0), "end": datetime.time(11, 0), "resources": 2},
        "11 AM - 2 PM": {"start": datetime.time(11, 0), "end": datetime.time(14, 0), "resources": 3},
        "2 PM - 6 PM": {"start": datetime.time(14, 0), "end": datetime.time(18, 0), "resources": 2},
        "6 PM - 8 PM": {"start": datetime.time(18, 0), "end": datetime.time(20, 0), "resources": 2},
        "8 PM - 5 AM": {"start": datetime.time(20, 0), "end": datetime.time(5, 0), "resources": 1}
    }
    
    # Define time sections and their overlapping shifts
    time_sections_shifts = {
        "5 AM - 9 AM": ["Shift 1"],
        "9 AM - 11 AM": ["Shift 1", "Shift 2"],
        "11 AM - 2 PM": ["Shift 1", "Shift 2", "Shift 3"],
        "2 PM - 6 PM": ["Shift 2", "Shift 3"],
        "6 PM - 8 PM": ["Shift 3", "Shift 4"],
        "8 PM - 5 AM": ["Shift 4"]
    }
    
    # Count calls in each shift
    shift_counts = {shift: 0 for shift in shifts}
    
    for _, row in df.iterrows():
        call_time = row['StartTime'].time()
        
        for shift, (start, end) in shifts.items():
            if is_time_in_range(call_time, start, end):
                shift_counts[shift] += 1
    
    # Count calls in each resource distribution time section
    resource_counts = {section: 0 for section in resource_distribution}
    
    for _, row in df.iterrows():
        call_time = row['StartTime'].time()
        
        for section, time_info in resource_distribution.items():
            if is_time_in_range(call_time, time_info["start"], time_info["end"]):
                resource_counts[section] += 1
    
    # Calculate non-repetitive calls per shift
    shift_counts_non_repetitive = {shift: 0 for shift in shifts}
    
    for section, section_shifts in time_sections_shifts.items():
        # Get the time range information for this section
        time_info = resource_distribution[section]
        section_call_count = 0
        
        # Count calls in this time section
        for _, row in df.iterrows():
            call_time = row['StartTime'].time()
            if is_time_in_range(call_time, time_info["start"], time_info["end"]):
                section_call_count += 1
        
        # Distribute calls evenly among shifts that cover this time section
        calls_per_shift = section_call_count / len(section_shifts)
        
        # Add the distributed calls to each shift
        for shift in section_shifts:
            shift_counts_non_repetitive[shift] += calls_per_shift
    
    # Count calls by hour of the day (New requirement - point 6)
    hourly_counts = {}
    
    # Initialize all hours with zero counts
    for hour in range(1, 13):
        hourly_counts[f"{hour} AM"] = 0
        hourly_counts[f"{hour} PM"] = 0
    
    # Count calls for each hour
    for _, row in df.iterrows():
        hour = row['StartTime'].hour
        am_pm = "AM" if hour < 12 else "PM"
        
        # Convert to 12-hour format
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
            
        key = f"{hour_12} {am_pm}"
        hourly_counts[key] += 1
    
    # Prepare the results dictionary
    resource_counts_result = {}
    for section, count in resource_counts.items():
        resources = resource_distribution[section]["resources"]
        calls_per_resource = count / resources if resources > 0 else 0
        resource_counts_result[section] = {
            "total_calls": count,
            "resources": resources,
            "calls_per_resource": round(calls_per_resource, 2)
        }
    
    non_repetitive_counts_result = {shift: round(count, 2) for shift, count in shift_counts_non_repetitive.items()}
    
    # Compile results
    results = {
        "shift_counts": shift_counts,
        "resource_counts": resource_counts_result,
        "non_repetitive_counts": non_repetitive_counts_result,
        "hourly_counts": hourly_counts
    }
    
    return results

def is_time_in_range(time, start, end):
    """Check if a time is within a range, handling cases that cross midnight."""
    if start <= end:
        return start <= time <= end
    else:
        return start <= time or time <= end 
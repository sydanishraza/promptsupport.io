#!/usr/bin/env python3
"""
More precise removal of refined engine endpoints
"""

def find_function_end(lines, start_line):
    """Find the end of a function definition"""
    indent_level = None
    
    for i in range(start_line, len(lines)):
        line = lines[i]
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
            
        # Find the function definition line
        if line.strip().startswith('async def ') or line.strip().startswith('def '):
            # This is the function definition, find its base indentation
            indent_level = len(line) - len(line.lstrip())
            continue
            
        if indent_level is not None:
            current_indent = len(line) - len(line.lstrip())
            
            # If we find a line with the same or less indentation (and it's not empty/comment)
            if current_indent <= indent_level and line.strip():
                # Check if this is the start of a new function or endpoint
                if (line.strip().startswith('@app.') or 
                    line.strip().startswith('async def ') or 
                    line.strip().startswith('def ') or
                    line.strip().startswith('class ')):
                    return i
    
    return len(lines)

def remove_refined_endpoints():
    """Remove refined engine endpoints precisely"""
    
    with open('backend/server.py', 'r') as f:
        lines = f.readlines()
    
    # Find endpoints to remove
    endpoints_to_remove = []
    
    for i, line in enumerate(lines):
        if '@app.' in line and any(endpoint in line for endpoint in [
            'process-advanced', 'upload-advanced', 'upload-batch-advanced',
            'cleanup-formatting', 'compare-engines', 'migrate-articles', 
            'engine-statistics', 'analytics/advanced', 'process-refined', 'upload-refined'
        ]):
            # Find the end of this function
            end_line = find_function_end(lines, i + 1)
            endpoints_to_remove.append((i, end_line, line.strip()))
    
    print(f"Found {len(endpoints_to_remove)} endpoints to remove:")
    for start, end, desc in endpoints_to_remove:
        print(f"  Lines {start+1}-{end}: {desc}")
    
    # Remove endpoints in reverse order to maintain line numbers
    for start, end, desc in reversed(endpoints_to_remove):
        print(f"Removing lines {start+1}-{end}: {desc}")
        del lines[start:end]
    
    # Write back the file
    with open('backend/server.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Endpoint removal complete!")

if __name__ == "__main__":
    remove_refined_endpoints()
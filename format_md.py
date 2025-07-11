#!/usr/bin/env python3
import re
import sys
from typing import List, Optional

def format_markdown_table(lines: List[str]) -> List[str]:
    """Formats a Markdown table to align columns."""
    if not any('|' in line for line in lines):
        return lines

    # Find table rows (ignore empty/gutter lines)
    rows = [line.strip() for line in lines if '|' in line and line.strip()]
    if len(rows) < 2:
        return lines

    # Split into columns and calculate max widths
    columns = []
    for row in rows:
        cols = [c.strip() for c in row.split('|') if c.strip() != '']
        columns.append(cols)
    
    if not all(len(cols) == len(columns[0]) for cols in columns):
        return lines  # Not a properly formatted table

    # Calculate max width per column
    col_widths = [
        max(len(cols[i]) for cols in columns)
        for i in range(len(columns[0]))
    ]

    # Build formatted rows
    formatted = []
    for i, cols in enumerate(columns):
        # Align left for all cells except numbers (right-align)
        formatted_cols = []
        for j, content in enumerate(cols):
            if re.match(r'^[\d.,]+$', content):
                # Right-align numbers
                formatted_cols.append(content.rjust(col_widths[j]))
            else:
                # Left-align text
                formatted_cols.append(content.ljust(col_widths[j]))
        
        formatted_row = '| ' + ' | '.join(formatted_cols) + ' |'
        formatted.append(formatted_row)

        # Add separator after header
        if i == 0:
            sep = '|-' + '-|-'.join('-' * w for w in col_widths) + '-|'
            formatted.append(sep)

    return formatted

def format_markdown_file(filename: str):
    """Formats an entire Markdown file."""
    with open(filename, 'r') as f:
        content = f.read().splitlines()

    formatted_content = []
    current_table = []

    for line in content:
        if '|' in line:
            current_table.append(line)
        else:
            if current_table:
                formatted_content.extend(format_markdown_table(current_table))
                current_table = []
            formatted_content.append(line)

    # Handle table at end of file
    if current_table:
        formatted_content.extend(format_markdown_table(current_table))

    with open(filename, 'w') as f:
        f.write('\n'.join(formatted_content))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python format_md.py file.md")
        sys.exit(1)
    
    format_markdown_file(sys.argv[1])
    print(f"Formatted {sys.argv[1]} successfully!")

#!/usr/bin/env python3
import re
import sys


def parse_tools(lines):
    tool_blocks = {}
    current_tool = None
    current_lines = []
    tool_re = re.compile(r"^Running command: (\d+)\.")
    for line in lines:
        m = tool_re.match(line)
        if m:
            if current_tool is not None:
                tool_blocks[current_tool] = "".join(current_lines).strip()
            current_tool = int(m.group(1))
            current_lines = [line]
        else:
            if current_tool is not None:
                current_lines.append(line)
    if current_tool is not None:
        tool_blocks[current_tool] = "".join(current_lines).strip()
    return tool_blocks


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <file1> <file2>")
    sys.exit(1)

file1, file2 = sys.argv[1], sys.argv[2]
with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
    lines1 = f1.readlines()
    lines2 = f2.readlines()

tools1 = parse_tools(lines1)
tools2 = parse_tools(lines2)
all_tool_nums = sorted(set(tools1.keys()) | set(tools2.keys()))

print(f"Comparing {file1} and {file2} (tool by tool):\n")
for num in all_tool_nums:
    t1 = tools1.get(num, None)
    t2 = tools2.get(num, None)
    if t1 != t2:
        print(f"Tool {num} differs:")
        if t1 is None:
            print(f"  {file1}: [MISSING]")
        else:
            print(f"  {file1} response:\n{t1}\n")
        if t2 is None:
            print(f"  {file2}: [MISSING]")
        else:
            print(f"  {file2} response:\n{t2}\n")
        print("-" * 60)

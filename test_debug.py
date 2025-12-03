from chatline import Chatline

# Test with debug
content = open('chat_example.txt', 'r', encoding='utf-8').read()
lines = content.split('\n')

print("Testing first few lines:\n")
prev = None
for i, line in enumerate(lines[:5]):
    if line.strip():
        print(f"Line {i+1}: {line[:80]}")
        c = Chatline(line, previous_line=prev, debug=True)
        prev = c

from chatline import Chatline

# Test parsing
content = open('chat_example.txt', 'r', encoding='utf-8').read()
lines = content.split('\n')

chats = []
prev = None
for line in lines:
    if line.strip():
        c = Chatline(line, previous_line=prev)
        chats.append(c)
        prev = c

msgs = [c for c in chats if c.line_type == "Chat"]
print(f"✅ Parsed {len(chats)} lines")
print(f"✅ Found {len(msgs)} chat messages")

if msgs:
    print(f"\nFirst 3 messages:")
    for m in msgs[:3]:
        print(f"  {m.sender}: {m.body[:50] if m.body else '(empty)'}...")

data = open('stress_test.mold', 'rb').read()
count = int.from_bytes(data[18:20], 'big')

offset = 20
msg_lens = []
for i in range(count):
    msg_len = int.from_bytes(data[offset:offset+2], 'big')
    msg_type = chr(data[offset+2])  # ITCH messages start with a 1-byte type char
    msg_lens.append((msg_type, msg_len))
    offset += 2 + msg_len

print('parsed messages:', len(msg_lens))
print('consumed bytes:', offset, 'vs file total:', len(data))
print('type breakdown:', {t: sum(1 for x in msg_lens if x[0]==t) for t in set(t for t,_ in msg_lens)})
import sys
import time

mb = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
secs = int(sys.argv[2]) if len(sys.argv) > 2 else 30

blocks = []
for i in range(mb):
    blocks.append(bytearray(b"\x01") * (1024 * 1024))
    if (i + 1) % 100 == 0:
        print("allocated", i + 1, "MB")

print("holding", mb, "MB for", secs, "seconds, watch your tools now")
end = time.time() + secs
while time.time() < end:
    for b in blocks:
        for j in range(0, len(b), 4096):
            b[j] = 2
    time.sleep(0.2)
print("done")

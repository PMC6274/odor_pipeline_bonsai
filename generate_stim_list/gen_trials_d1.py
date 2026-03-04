import random
import os

random.seed()

blocks = []
for _ in range(25):
    block = list(range(1, 9))
    random.shuffle(block)
    blocks.extend(block)

out_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
path1 = os.path.join(out_dir, "odor_sequence_numbers.csv")
path2 = os.path.join(out_dir, "odor_sequence_D1_format.txt")

# file 1：odor number（trial_index, odor_id）
with open(path1, "w", encoding="utf-8") as f:
    for i, odor in enumerate(blocks, start=1):
        f.write(f"{i},{odor}\n")

# file 2：it == k ? "D1:X" : ... "D1:0"
with open(path2, "w", encoding="utf-8") as f:
    for i, odor in enumerate(blocks, start=1):
        f.write(f'it == {i}  ? "D1:{odor}" :\n')
    f.write('"D1:0"\n')

print("Done. Saved:", path1, "and", path2)
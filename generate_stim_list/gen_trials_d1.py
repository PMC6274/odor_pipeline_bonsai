import random
import os

random.seed()  # 用当前时间，每次运行顺序不同；要固定顺序可写 random.seed(0)

blocks = []
for _ in range(25):
    block = list(range(1, 9))
    random.shuffle(block)
    blocks.extend(block)

# 脚本所在目录作为输出目录
out_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
path1 = os.path.join(out_dir, "odor_sequence_numbers.csv")
path2 = os.path.join(out_dir, "odor_sequence_D1_format.txt")

# 文件 1：纯数字（trial_index, odor_id）
with open(path1, "w", encoding="utf-8") as f:
    for i, odor in enumerate(blocks, start=1):
        f.write(f"{i},{odor}\n")

# 文件 2：it == k ? "D1:X" : ... "D1:0"
with open(path2, "w", encoding="utf-8") as f:
    for i, odor in enumerate(blocks, start=1):
        f.write(f'it == {i}  ? "D1:{odor}" :\n')
    f.write('"D1:0"\n')

print("Done. Saved:", path1, "and", path2)
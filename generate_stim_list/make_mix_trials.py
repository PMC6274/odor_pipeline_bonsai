from pathlib import Path
import random
import csv

# A B C D E F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]


def code_to_row(code: int):
    """
    把 0~63 的 code 转成:
    A, B, C, D, E, F, flow
    code=0 时表示全关，对应 flow=900
    """
    outputs = []
    on_count = 0

    for bit, val in enumerate(ODOR_VALUES):
        if code & (1 << bit):
            outputs.append(val)
            on_count += 1
        else:
            outputs.append(0)

    flow = 900 - 100 * on_count
    return outputs + [flow]


def make_trial_list(block_num: int, seed=None):
    """
    生成 trial 顺序。
    每个 block 都是 0~63，block 内随机打乱。
    返回 [(block, code), ...]
    """
    rng = random.Random(seed)
    trials = []

    for block_idx in range(1, block_num + 1):
        block_codes = list(range(0, 64))   # 改成包含 0
        rng.shuffle(block_codes)
        for code in block_codes:
            trials.append((block_idx, code))

    return trials


def save_bonsai_and_csv(
    block_num=3,
    seed=123,
    txt_file="bonsai_conditions_shuffled.txt",
    csv_file="trial_table.csv"
):
    trials = make_trial_list(block_num, seed)

    txt_lines = []
    csv_rows = []

    for trial_idx, (block_idx, code) in enumerate(trials, start=1):
        row = code_to_row(code)
        a, b, c, d, e, f, flow = row

        if trial_idx < 10:
            txt_line = f'it == {trial_idx}  ? "{a},{b},{c},{d},{e},{f},{flow}" :'
        else:
            txt_line = f'it == {trial_idx} ? "{a},{b},{c},{d},{e},{f},{flow}" :'
        txt_lines.append(txt_line)

        csv_rows.append([
            trial_idx,
            block_idx,
            code,
            a, b, c, d, e, f,
            flow
        ])

    txt_lines.append('"0,0,0,0,0,0,0"')

    Path(txt_file).write_text("\n".join(txt_lines), encoding="utf-8")

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trial", "block", "code",
            "A", "B", "C", "D", "E", "F",
            "flow"
        ])
        writer.writerows(csv_rows)

    print(f"Saved: {txt_file}")
    print(f"Saved: {csv_file}")
    print(f"Total trials: {len(csv_rows)}")


if __name__ == "__main__":
    BLOCK_NUM = 10
    SEED = None   # 固定数字则可复现；None 则每次都重新随机

    save_bonsai_and_csv(
        block_num=BLOCK_NUM,
        seed=SEED,
        txt_file="bonsai_conditions_shuffled.txt",
        csv_file="trial_table.csv"
    )
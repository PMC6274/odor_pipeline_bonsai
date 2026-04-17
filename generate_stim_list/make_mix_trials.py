from pathlib import Path
import random
import csv

# txt file 里 A~F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]


def code_to_states(code: int):
    """
    0~63 -> A~F 六个 0/1
    """
    return [1 if code & (1 << bit) else 0 for bit in range(6)]


def states_to_flow(states):
    """
    carrier = 900 - 100 * 开启 odor 数
    """
    return 900 - 100 * sum(states)


def states_to_txt_row(states):
    """
    给 Bonsai txt 用:
    开启的 odor 输出 1,2,3,5,6,7
    未开启输出 0
    """
    outputs = []
    for state, odor_val in zip(states, ODOR_VALUES):
        outputs.append(odor_val if state else 0)
    return outputs


def states_to_type(states):
    """
    生成 6 位 0/1 字符串
    例如:
      000000
      110000
      001010
      111111
    """
    return "".join(str(x) for x in states)


def make_trial_list(block_num: int, seed=None):
    """
    每个 block 都是 0~63，block 内随机打乱
    返回 [(block, code), ...]
    """
    rng = random.Random(seed)
    trials = []

    for block_idx in range(1, block_num + 1):
        block_codes = list(range(0, 64))
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
        states = code_to_states(code)              # 0/1 for csv
        flow = states_to_flow(states)
        txt_vals = states_to_txt_row(states)       # 1,2,3,5,6,7 for txt
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        # Bonsai txt: 仍然输出 1,2,3,5,6,7 风格
        if trial_idx < 10:
            txt_line = f'it == {trial_idx}  ? "{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{flow}" :'
        else:
            txt_line = f'it == {trial_idx} ? "{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{flow}" :'
        txt_lines.append(txt_line)

        # CSV: 保存 0/1 trial table
        csv_rows.append([
            trial_idx,
            block_idx,
            code,
            a, b, c, d, e, f,
            flow,
            type_str
        ])

    # fallback line 给 Bonsai
    txt_lines.append('"0,0,0,0,0,0,0"')

    Path(txt_file).write_text("\n".join(txt_lines), encoding="utf-8")

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trial", "block", "code",
            "A", "B", "C", "D", "E", "F",
            "flow", "type"
        ])
        writer.writerows(csv_rows)

    print(f"Saved: {txt_file}")
    print(f"Saved: {csv_file}")
    print(f"Total trials: {len(csv_rows)}")


if __name__ == "__main__":
    BLOCK_NUM = 10
    SEED = None   # None = 每次都重新随机；整数 = 可复现

    save_bonsai_and_csv(
        block_num=BLOCK_NUM,
        seed=SEED,
        txt_file="bonsai_conditions_shuffled.txt",
        csv_file="trial_table.csv"
    )
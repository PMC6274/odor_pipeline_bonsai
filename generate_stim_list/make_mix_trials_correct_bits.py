from pathlib import Path
import random
import csv

# txt file 里 A~F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]


def code_to_states(code: int):
    """
    0~63 -> A~F 六个 0/1

    IMPORTANT:
    A B C D E F 对应 binary 从高位到低位:
    A=bit5, B=bit4, C=bit3, D=bit2, E=bit1, F=bit0

    例如:
    code = 59
    binary = 111011
    -> A B C D E F = 1 1 1 0 1 1
    """
    bits = f"{code:06b}"   # standard binary string, MSB -> LSB
    return [int(b) for b in bits]


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
    return [odor_val if state else 0 for state, odor_val in zip(states, ODOR_VALUES)]


def states_to_type(states):
    """
    生成 6 位 0/1 字符串，顺序就是 A B C D E F
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
        block_codes = list(range(64))
        rng.shuffle(block_codes)
        for code in block_codes:
            trials.append((block_idx, code))

    return trials


def save_bonsai_and_csv(
    block_num=10,
    seed=None,
    txt_file="bonsai_conditions_shuffled.txt",
    csv_file="trial_table.csv"
):
    trials = make_trial_list(block_num, seed)

    txt_lines = []
    csv_rows = []

    for trial_idx, (block_idx, code) in enumerate(trials, start=1):
        states = code_to_states(code)
        flow = states_to_flow(states)
        txt_vals = states_to_txt_row(states)
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        # Bonsai txt: it still runs from 1..total_trials
        if trial_idx < 10:
            txt_line = f'it == {trial_idx}  ? "{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{flow}" :'
        else:
            txt_line = f'it == {trial_idx} ? "{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{flow}" :'
        txt_lines.append(txt_line)

        csv_rows.append([
            trial_idx,
            block_idx,
            code,
            a, b, c, d, e, f,
            flow,
            type_str
        ])

    # fallback line
    txt_lines.append('"0,0,0,0,0,0,900"')

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
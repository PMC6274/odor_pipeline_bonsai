from pathlib import Path
import random
import csv

# txt file 里 A~F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]
ODOR_FLOW = 100


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
    bits = f"{code:06b}"   # MSB -> LSB
    return [int(b) for b in bits]


def states_to_total_odor_flow(states):
    """
    odor 总 flow
    每个 odor 固定 100
    全关 -> 0
    """
    return ODOR_FLOW * sum(states)


def output_flow(states):
    """
    你要的 flow 列：
    - 只要有任何 odor 开启，flow = 100
    - 如果全部关闭，flow = 0
    """
    return ODOR_FLOW if sum(states) > 0 else 0


def states_to_carrier_out(states):
    """
    carrier_out 保持旧逻辑:
    900 - 100 * 开启 odor 数
    全关 -> 900
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
        total_odor_flow = states_to_total_odor_flow(states)
        flow = output_flow(states)   # 新的 flow 规则
        carrier_out = states_to_carrier_out(states)
        txt_vals = states_to_txt_row(states)
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        # txt 最后一列仍然是 carrier_out
        if trial_idx < 10:
            txt_line = f'it == {trial_idx}  ? "{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{carrier_out}" :'
        else:
            txt_line = f'it == {trial_idx} ? "{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{carrier_out}" :'
        txt_lines.append(txt_line)

        csv_rows.append([
            trial_idx,
            block_idx,
            a, b, c, d, e, f,
            type_str,
            code,
            sum(states),          # odor_number
            flow,                 # 0 or 100
            total_odor_flow,      # 总 odor flow
            carrier_out,
        ])

    # fallback line: txt 最后一列也保持 carrier_out
    txt_lines.append('"0,0,0,0,0,0,900"')

    Path(txt_file).write_text("\n".join(txt_lines), encoding="utf-8")

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trial", "block",
            "A", "B", "C", "D", "E", "F",
            "type", "code", "odor_number",
            "flow", "total_odor_flow", "carrier_out"
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
        txt_file="bonsai_conditions_add_conc.txt",
        csv_file="trial_table_add_conc.csv"
    )
from pathlib import Path
import random
import csv

# A~F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]
ODOR_FLOW = 100
CAR_FLOW = 800


def code_to_states(code: int):
    """
    0~63 -> A~F 六个 0/1
    A B C D E F 对应 binary 高位到低位
    """
    bits = f"{code:06b}"
    return [int(b) for b in bits]


def states_to_type(states):
    """
    生成 6 位 0/1 字符串，顺序就是 A B C D E F
    """
    return "".join(str(x) for x in states)


def states_to_txt_row(states):
    """
    前 6 个输出：
    开启的 odor 输出 1,2,3,5,6,7
    未开启输出 0
    """
    return [odor_val if state else 0 for state, odor_val in zip(states, ODOR_VALUES)]


def divider_output(states):
    """
    第7个输出：
    开启 odor 的总数
    """
    return sum(states)


def flow_from_divider(divider: int):
    """
    trial table 里的 flow:
    - divider > 0 时，flow = 100 / divider
    - divider = 0 时，flow = 0
    """
    if divider <= 0:
        return 0.0
    return ODOR_FLOW / divider


def final_carrier_output(states):
    """
    第8个输出：
    - 如果有任何 odor 开启，输出 800
    - 如果全部关闭，输出 900
    """
    return CAR_FLOW if sum(states) > 0 else CAR_FLOW + ODOR_FLOW


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
    txt_file="bonsai_conditions_divider_8out.txt",
    csv_file="trial_table_divider_8out.csv"
):
    trials = make_trial_list(block_num, seed)

    txt_lines = []
    csv_rows = []

    for trial_idx, (block_idx, code) in enumerate(trials, start=1):
        states = code_to_states(code)
        type_str = states_to_type(states)

        # 前6个：1,2,3,5,6,7 风格
        txt_vals = states_to_txt_row(states)

        # 第7个：divider
        divider = divider_output(states)

        # trial table 里的 flow = 100/divider
        flow = flow_from_divider(divider)

        # 第8个：carrier 输出
        carrier_out = final_carrier_output(states)

        payload_list = txt_vals + [divider, carrier_out]
        payload = ",".join(map(str, payload_list))

        if trial_idx < 10:
            txt_line = f'it == {trial_idx}  ? "{payload}" :'
        else:
            txt_line = f'it == {trial_idx} ? "{payload}" :'
        txt_lines.append(txt_line)

        a, b, c, d, e, f = states

        csv_rows.append([
            trial_idx,
            block_idx,
            a, b, c, d, e, f,
            type_str,
            code,
            divider,
            flow,
            round(divider*flow),
            carrier_out
        ])

    # fallback line
    txt_lines.append('"0,0,0,0,0,0,0,900"')

    Path(txt_file).write_text("\n".join(txt_lines), encoding="utf-8")

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trial", "block",
            "A", "B", "C", "D", "E", "F",
            "type", "code",
            "odor_number",
            "flow","total_odor_flow",
            "carrier_out"
        ])
        writer.writerows(csv_rows)

    print(f"Saved: {txt_file}")
    print(f"Saved: {csv_file}")
    print(f"Total trials: {len(csv_rows)}")


if __name__ == "__main__":
    BLOCK_NUM = 10
    SEED = None   # None = 每次重新随机；整数 = 可复现

    save_bonsai_and_csv(
        block_num=BLOCK_NUM,
        seed=SEED,
        txt_file="bonsai_conditions_same_conc.txt",
        csv_file="trial_table_same_conc.csv"
    )
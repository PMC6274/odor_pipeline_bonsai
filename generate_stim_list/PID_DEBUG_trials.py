from pathlib import Path
import csv

# txt file 里 A~F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]
ODOR_NAMES = ["A", "B", "C", "D", "E", "F"]

ODOR_FLOW = 100


def normalize_odor_sequence(odor_sequence: str):
    """
    Allow both:
    "ABCEDF"
    "A B C E D F"
    "A,B,C,E,D,F"

    Return:
    ["A", "B", "C", "E", "D", "F"]
    """
    odor_sequence = odor_sequence.upper()
    odor_sequence = odor_sequence.replace(",", " ")
    odor_sequence = odor_sequence.replace(";", " ")

    # Case 1: user writes "A B D E F C"
    if " " in odor_sequence:
        odors = [x.strip() for x in odor_sequence.split() if x.strip()]
    else:
        # Case 2: user writes "ABDEFC"
        odors = list(odor_sequence)

    for odor_name in odors:
        if odor_name not in ODOR_NAMES:
            raise ValueError(
                f"Unknown odor in sequence: {odor_name}. "
                f"Must be one of A B C D E F"
            )

    return odors


def code_to_states(code: int):
    """
    0~63 -> A~F 六个 0/1

    A B C D E F 对应 binary 从高位到低位:
    A=bit5, B=bit4, C=bit3, D=bit2, E=bit1, F=bit0
    """
    bits = f"{code:06b}"
    return [int(b) for b in bits]


def states_to_code(states):
    """
    A~F states -> code
    """
    bit_str = "".join(str(x) for x in states)
    return int(bit_str, 2)


def odor_to_states(odor_name: str):
    """
    Single odor only.
    A -> [1,0,0,0,0,0]
    B -> [0,1,0,0,0,0]
    ...
    """
    odor_name = odor_name.upper()

    if odor_name not in ODOR_NAMES:
        raise ValueError(f"Unknown odor: {odor_name}. Must be one of A B C D E F")

    return [1 if name == odor_name else 0 for name in ODOR_NAMES]


def states_to_total_odor_flow(states):
    """
    odor 总 flow
    single odor -> 100
    """
    return ODOR_FLOW * sum(states)


def output_flow(states):
    """
    flow 列:
    - 只要有任何 odor 开启，flow = 100
    - 如果全部关闭，flow = 0
    """
    return ODOR_FLOW if sum(states) > 0 else 0


def states_to_carrier_out(states):
    """
    single odor:
    900 - 100 * 1 = 800
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


def make_trial_list(odor_sequence: str, block_num: int):
    """
    odor_sequence example:
    "ABCEDF"
    "A B D E F C"
    "A,B,D,E,F,C"

    block_num = 10

    Example:
    A repeated 10 times
    B repeated 10 times
    D repeated 10 times
    E repeated 10 times
    F repeated 10 times
    C repeated 10 times

    所有 block 都是 1
    """
    trials = []

    odors = normalize_odor_sequence(odor_sequence)

    for odor_name in odors:
        for _ in range(block_num):
            block_idx = 1
            states = odor_to_states(odor_name)
            code = states_to_code(states)
            trials.append((block_idx, code, odor_name))

    return trials


def save_bonsai_and_csv(
    odor_sequence="ABDEFC",
    block_num=10,
    txt_file="bonsai_conditions_single_odor.txt",
    csv_file="trial_table_single_odor.csv"
):
    trials = make_trial_list(odor_sequence, block_num)

    txt_lines = []
    csv_rows = []

    for trial_idx, (block_idx, code, odor_name) in enumerate(trials, start=1):
        states = code_to_states(code)

        total_odor_flow = states_to_total_odor_flow(states)
        flow = output_flow(states)
        carrier_out = states_to_carrier_out(states)

        txt_vals = states_to_txt_row(states)
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        if trial_idx < 10:
            txt_line = (
                f'it == {trial_idx}  ? '
                f'"{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{carrier_out}" :'
            )
        else:
            txt_line = (
                f'it == {trial_idx} ? '
                f'"{a_txt},{b_txt},{c_txt},{d_txt},{e_txt},{f_txt},{carrier_out}" :'
            )

        txt_lines.append(txt_line)

        csv_rows.append([
            trial_idx,
            block_idx,
            odor_name,
            a, b, c, d, e, f,
            type_str,
            code,
            sum(states),
            flow,
            total_odor_flow,
            carrier_out,
        ])

    # fallback line
    txt_lines.append('"0,0,0,0,0,0,900"')

    Path(txt_file).write_text("\n".join(txt_lines), encoding="utf-8")

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "trial", "block", "odor",
            "A", "B", "C", "D", "E", "F",
            "type", "code", "odor_number",
            "flow", "total_odor_flow", "carrier_out"
        ])

        writer.writerows(csv_rows)

    print(f"Saved: {txt_file}")
    print(f"Saved: {csv_file}")
    print(f"Total trials: {len(csv_rows)}")
    print(f"Odor order: {' '.join(normalize_odor_sequence(odor_sequence))}")


if __name__ == "__main__":
    # You can write it either way:
    # ODOR_SEQUENCE = "ABCEDF"
    # ODOR_SEQUENCE = "A B C E D F"
    # ODOR_SEQUENCE = "A,B,C,E,D,F"

    ODOR_SEQUENCE = "A B D E F C"
    BLOCK_NUM = 10

    save_bonsai_and_csv(
        odor_sequence=ODOR_SEQUENCE,
        block_num=BLOCK_NUM,
        txt_file="DEBUG_bonsai_trials.txt",
        csv_file="DEBUG_trial_table.csv"
    )
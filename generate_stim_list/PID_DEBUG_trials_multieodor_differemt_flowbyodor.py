from pathlib import Path
import csv
import random

# txt file 里 A~F 开启时对应输出值
ODOR_VALUES = [1, 2, 3, 5, 6, 7]
ODOR_NAMES = ["A", "B", "C", "D", "E", "F"]

TOTAL_FLOW = 900


def normalize_odor_sequence(odor_sequence: str):
    """
    Allow:
    "ABCDEF"
    "A B C D E F"
    "A,B,C,D,E,F"
    """
    odor_sequence = odor_sequence.upper()
    odor_sequence = odor_sequence.replace(",", " ")
    odor_sequence = odor_sequence.replace(";", " ")

    if " " in odor_sequence:
        odors = [x.strip() for x in odor_sequence.split() if x.strip()]
    else:
        odors = list(odor_sequence)

    for odor_name in odors:
        if odor_name not in ODOR_NAMES:
            raise ValueError(
                f"Unknown odor in sequence: {odor_name}. "
                f"Must be one of A B C D E F"
            )

    return odors


def odor_to_states(odor_name: str):
    """
    Single odor only.
    A -> [1,0,0,0,0,0]
    """
    odor_name = odor_name.upper()

    if odor_name not in ODOR_NAMES:
        raise ValueError(f"Unknown odor: {odor_name}")

    return [1 if name == odor_name else 0 for name in ODOR_NAMES]


def states_to_code(states):
    """
    Convert A~F states to decimal code
    """
    bit_str = "".join(str(x) for x in states)
    return int(bit_str, 2)


def states_to_type(states):
    """
    Convert states to 6-bit string
    """
    return "".join(str(x) for x in states)


def states_to_txt_row(states):
    """
    Bonsai txt row:
    opened odor -> 1,2,3,5,6,7
    closed -> 0
    """
    return [
        odor_val if state else 0
        for state, odor_val in zip(states, ODOR_VALUES)
    ]


def make_trial_list(
    odor_sequence: str,
    block_num: int,
    repeat_num: int,
):
    """
    Each block:
        all odors repeated repeat_num times
        randomized order

    Example:
    odors = A B C
    repeat_num = 2

    One block may become:
    B A C A C B
    """

    odors = normalize_odor_sequence(odor_sequence)

    trials = []

    for block_idx in range(1, block_num + 1):

        block_trials = odors * repeat_num
        random.shuffle(block_trials)

        for odor_name in block_trials:
            states = odor_to_states(odor_name)
            code = states_to_code(states)

            trials.append((block_idx, odor_name, states, code))

    return trials


def save_bonsai_and_csv(
    odor_sequence="A B C D E F",
    block_num=10,
    repeat_num=1,
    flow_range=(810, 890),
    txt_file="DEBUG_bonsai.txt",
    csv_file="DEBUG_bonsai_table.csv"
):
    """
    flow_range:
        carrier_out random range
        example:
            (810, 890)

    odor flow:
        TOTAL_FLOW - carrier_out
    """

    min_carrier, max_carrier = flow_range

    trials = make_trial_list(
        odor_sequence=odor_sequence,
        block_num=block_num,
        repeat_num=repeat_num,
    )

    txt_lines = []
    csv_rows = []

    for trial_idx, (block_idx, odor_name, states, code) in enumerate(trials, start=1):

        # random carrier flow
        carrier_out = random.randint(min_carrier, max_carrier)

        # odor flow automatically computed
        odor_flow = TOTAL_FLOW - carrier_out

        txt_vals = states_to_txt_row(states)
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        # txt line
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
            odor_flow,
            carrier_out,
        ])

    # fallback line
    txt_lines.append('"0,0,0,0,0,0,900"')

    # save txt
    Path(txt_file).write_text(
        "\n".join(txt_lines),
        encoding="utf-8"
    )

    # save csv
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "trial",
            "block",
            "odor",
            "A", "B", "C", "D", "E", "F",
            "type",
            "code",
            "odor_flow",
            "carrier_out",
        ])

        writer.writerows(csv_rows)

    print(f"Saved: {txt_file}")
    print(f"Saved: {csv_file}")
    print(f"Total trials: {len(csv_rows)}")
    print(f"Blocks: {block_num}")
    print(f"Repeat per odor per block: {repeat_num}")
    print(f"Carrier range: {flow_range}")
    print(f"Odors: {' '.join(normalize_odor_sequence(odor_sequence))}")


if __name__ == "__main__":

    ODOR_SEQUENCE = "A B C D E F"

    BLOCK_NUM = 10

    # each odor repeated N times inside each block
    REPEAT_NUM = 3

    # carrier_out random range
    FLOW_RANGE = (810, 890)

    save_bonsai_and_csv(
        odor_sequence=ODOR_SEQUENCE,
        block_num=BLOCK_NUM,
        repeat_num=REPEAT_NUM,
        flow_range=FLOW_RANGE,
        txt_file="DEBUG_bonsai_cc.txt",
        csv_file="DEBUG_bonsai_table_cc.csv"
    )
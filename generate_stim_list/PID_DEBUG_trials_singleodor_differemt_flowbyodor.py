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
                f"Unknown odor in sequence: {odor_name}"
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


def make_flow_list(flow_range, block_num):
    """
    Create one fixed flow per block.

    Example:
    flow_range=(810,890)
    block_num=5

    -> [810, 830, 850, 870, 890]
    """

    start_flow, end_flow = flow_range

    if block_num == 1:
        return [start_flow]

    step = (end_flow - start_flow) / (block_num - 1)

    flows = [
        round(start_flow + i * step)
        for i in range(block_num)
    ]

    return flows


def make_trial_list(
    odor_name: str,
    block_num: int,
    repeat_num: int,
    flow_range=(810, 890),
):
    """
    SAME odor every trial.

    Different blocks use different carrier flow.

    Example:
    block1 -> carrier 810
    block2 -> carrier 830
    block3 -> carrier 850
    """

    odor_name = odor_name.upper()

    states = odor_to_states(odor_name)
    code = states_to_code(states)

    carrier_flows = make_flow_list(flow_range, block_num)

    trials = []

    for block_idx in range(1, block_num + 1):

        carrier_out = carrier_flows[block_idx - 1]

        for _ in range(repeat_num):

            odor_flow = TOTAL_FLOW - carrier_out

            trials.append((
                block_idx,
                odor_name,
                states,
                code,
                odor_flow,
                carrier_out,
            ))

    return trials


def save_bonsai_and_csv(
    odor_name="A",
    block_num=5,
    repeat_num=10,
    flow_range=(810, 890),
    txt_file="DEBUG_bonsai.txt",
    csv_file="DEBUG_bonsai_table.csv"
):

    trials = make_trial_list(
        odor_name=odor_name,
        block_num=block_num,
        repeat_num=repeat_num,
        flow_range=flow_range,
    )

    txt_lines = []
    csv_rows = []

    for trial_idx, (
        block_idx,
        odor_name,
        states,
        code,
        odor_flow,
        carrier_out,
    ) in enumerate(trials, start=1):

        txt_vals = states_to_txt_row(states)
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        # txt format
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
    print(f"Odor: {odor_name}")
    print(f"Blocks: {block_num}")
    print(f"Repeat per block: {repeat_num}")
    print(f"Flow range: {flow_range}")


if __name__ == "__main__":

    # SAME odor every trial
    ODOR_NAME = "C"

    # each block uses different flow
    BLOCK_NUM = 10

    # repeats inside each block
    REPEAT_NUM = 10

    # carrier flow range
    FLOW_RANGE = (800, 890)

    save_bonsai_and_csv(
        odor_name=ODOR_NAME,
        block_num=BLOCK_NUM,
        repeat_num=REPEAT_NUM,
        flow_range=FLOW_RANGE,
        txt_file="DEBUG_bonsai_c2.txt",
        csv_file="DEBUG_bonsai_table_c2.csv"
    )
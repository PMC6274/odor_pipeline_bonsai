from pathlib import Path
import csv
import random

# Bonsai txt output value when each odor is ON
# A B C D E F
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
            raise ValueError(f"Unknown odor in sequence: {odor_name}")

    return odors


def odor_to_states(odor_name: str):
    """
    Single odor only.

    A -> [1,0,0,0,0,0]
    B -> [0,1,0,0,0,0]
    C -> [0,0,1,0,0,0]
    """
    odor_name = odor_name.upper()

    if odor_name not in ODOR_NAMES:
        raise ValueError(f"Unknown odor: {odor_name}")

    return [1 if name == odor_name else 0 for name in ODOR_NAMES]


def states_to_code(states):
    """
    Convert A~F states to decimal code.

    A = 100000 -> 32
    B = 010000 -> 16
    C = 001000 -> 8
    D = 000100 -> 4
    E = 000010 -> 2
    F = 000001 -> 1
    """
    bit_str = "".join(str(x) for x in states)
    return int(bit_str, 2)


def states_to_type(states):
    """
    Convert states to 6-bit string.

    Important:
    This keeps leading zeros in the CSV text file.
    Excel may display 001000 as 1000 unless you import the column as text.
    """
    return "".join(str(x) for x in states)


def states_to_txt_row(states):
    """
    Bonsai txt row:
    opened odor -> 1,2,3,5,6,7
    closed odor -> 0

    Example:
    C on -> [0,0,3,0,0,0]
    """
    return [
        odor_val if state else 0
        for state, odor_val in zip(states, ODOR_VALUES)
    ]


def make_flow_list(flow_range, block_num):
    """
    Create one carrier flow per block.

    Example:
    flow_range=(800,890)
    block_num=10

    -> [800,810,820,830,840,850,860,870,880,890]
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


def make_trial_list_all_odors(
    odor_sequence="ABCDEF",
    block_num=10,
    repeat_num=10,
    flow_range=(800, 890),
    shuffle_within_block=False,
    seed=1,
):
    """
    Generate trials for all single odors.

    Structure:
    block 1:
        A repeated repeat_num times
        B repeated repeat_num times
        C repeated repeat_num times
        ...
        F repeated repeat_num times

    block 2:
        same odor sequence, but with next carrier flow

    If shuffle_within_block=True:
        all odor trials inside each block are randomized.
    """

    odors = normalize_odor_sequence(odor_sequence)
    carrier_flows = make_flow_list(flow_range, block_num)

    rng = random.Random(seed)

    trials = []

    for block_idx in range(1, block_num + 1):

        carrier_out = carrier_flows[block_idx - 1]
        flow = TOTAL_FLOW - carrier_out
        total_odor_flow = flow

        block_trials = []

        for odor_name in odors:

            states = odor_to_states(odor_name)
            code = states_to_code(states)

            for rep_idx in range(1, repeat_num + 1):

                block_trials.append((
                    block_idx,
                    rep_idx,
                    odor_name,
                    states,
                    code,
                    flow,
                    total_odor_flow,
                    carrier_out,
                ))

        if shuffle_within_block:
            rng.shuffle(block_trials)

        trials.extend(block_trials)

    return trials


def save_bonsai_and_csv_all_odors(
    odor_sequence="ABCDEF",
    block_num=10,
    repeat_num=10,
    flow_range=(800, 890),
    shuffle_within_block=False,
    seed=1,
    txt_file="DEBUG_bonsai_ABCDEF.txt",
    csv_file="DEBUG_bonsai_table_ABCDEF.csv",
):
    """
    Save:
    1. Bonsai txt condition file
    2. CSV trial table
    """

    trials = make_trial_list_all_odors(
        odor_sequence=odor_sequence,
        block_num=block_num,
        repeat_num=repeat_num,
        flow_range=flow_range,
        shuffle_within_block=shuffle_within_block,
        seed=seed,
    )

    txt_lines = []
    csv_rows = []

    for trial_idx, (
        block_idx,
        rep_idx,
        odor_name,
        states,
        code,
        flow,
        total_odor_flow,
        carrier_out,
    ) in enumerate(trials, start=1):

        txt_vals = states_to_txt_row(states)
        type_str = states_to_type(states)

        a_txt, b_txt, c_txt, d_txt, e_txt, f_txt = txt_vals
        a, b, c, d, e, f = states

        # Bonsai txt format
        # Same structure as your original code
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
            flow,
            total_odor_flow,
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
            "flow",
            "total_odor_flow",
            "carrier_out",
        ])

        writer.writerows(csv_rows)

    print(f"Saved: {txt_file}")
    print(f"Saved: {csv_file}")
    print(f"Total trials: {len(csv_rows)}")
    print(f"Odor sequence: {odor_sequence}")
    print(f"Blocks: {block_num}")
    print(f"Repeat per odor per block: {repeat_num}")
    print(f"Flow range: {flow_range}")
    print(f"Shuffle within block: {shuffle_within_block}")

    print("")
    print("First few rows:")
    for row in csv_rows[:10]:
        print(row)


if __name__ == "__main__":

    # Go through all single odors
    ODOR_SEQUENCE = "ABCDEF"

    # each block uses different carrier flow
    BLOCK_NUM = 5

    # repeat each odor inside each block
    REPEAT_NUM = 10

    # carrier flow range
    # block 1 carrier = 800, odor flow = 100
    # block 10 carrier = 890, odor flow = 10
    FLOW_RANGE = (860, 890)

    # False:
    # block 1 = A A A ... B B B ... C C C ...
    #
    # True:
    # block 1 has A-F randomized, but each odor still appears REPEAT_NUM times
    SHUFFLE_WITHIN_BLOCK = False

    save_bonsai_and_csv_all_odors(
        odor_sequence=ODOR_SEQUENCE,
        block_num=BLOCK_NUM,
        repeat_num=REPEAT_NUM,
        flow_range=FLOW_RANGE,
        shuffle_within_block=SHUFFLE_WITHIN_BLOCK,
        seed=1,
        txt_file="DEBUG_bonsai_ABCDEF2.txt",
        csv_file="DEBUG_bonsai_table_ABCDEF2.csv",
    )
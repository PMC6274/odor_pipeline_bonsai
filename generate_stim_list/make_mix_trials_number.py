from pathlib import Path
import random
import csv

# 6 odors: A, B, C, D, E, F
# Each block includes all 64 conditions: 0~63
# Bonsai payload format:
#   device1_odor | device1_check | device2_odor | device2_check | flow
# Empty fields are written as "None" so you can branch/skip in Bonsai.

def code_to_binary_states(code: int):
    """
    Convert 0~63 code into six binary states [A,B,C,D,E,F].
    """
    return [1 if (code & (1 << bit)) else 0 for bit in range(6)]


def states_to_flow(states):
    """
    Flow rule:
      carrier = 900 - 100 * number_of_active_odors
    """
    return 900 - 100 * sum(states)


def nz(s: str) -> str:
    """
    Replace empty string with 'None' for easier Bonsai condition checks.
    """
    return s if s else "0"


def make_device_strings(states):
    """
    Input: [A,B,C,D,E,F] as 0/1

    Device 1 uses A,B,C -> Valve0, Valve1, Valve2
    Device 2 uses D,E,F -> Valve0, Valve1, Valve2

    Returns:
      d1_odor_str, d1_check_str, d2_odor_str, d2_check_str
    """
    a, b, c, d, e, f = states

    d1_odor = []
    d1_check = []
    if a:
        d1_odor.append("1")
        d1_check.append("100")
    if b:
        d1_odor.append("2")
        d1_check.append("200")
    if c:
        d1_odor.append("4")
        d1_check.append("400")

    d2_odor = []
    d2_check = []
    if d:
        d2_odor.append("1")
        d2_check.append("100")
    if e:
        d2_odor.append("2")
        d2_check.append("200")
    if f:
        d2_odor.append("4")
        d2_check.append("400")

    return (
        nz("-".join(d1_odor)),
        nz("-".join(d1_check)),
        nz("-".join(d2_odor)),
        nz("-".join(d2_check)),
    )


def code_to_bonsai_payload(code: int):
    """
    Final Bonsai payload:
      d1_odor|d1_check|d2_odor|d2_check|flow
    Example:
      Valve0,Valve1|CheckValve0,CheckValve1|Valve1|CheckValve1|600
    """
    states = code_to_binary_states(code)
    flow = states_to_flow(states)
    d1_odor, d1_check, d2_odor, d2_check = make_device_strings(states)
    return f"{d1_odor},{d1_check},{d2_odor},{d2_check},{flow}"


def make_trial_list(block_num: int, seed=None):
    """
    Create shuffled trial list.
    Each block contains all 64 conditions: 0~63, shuffled within block.

    Returns:
      [(block_index, code), ...]
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
    seed=None,
    txt_file="bonsai_conditions_shuffled.txt",
    csv_file="trial_table.csv"
):
    trials = make_trial_list(block_num, seed)

    txt_lines = []
    csv_rows = []

    for trial_idx, (block_idx, code) in enumerate(trials, start=1):
        states = code_to_binary_states(code)
        flow = states_to_flow(states)
        payload = code_to_bonsai_payload(code)

        if trial_idx < 10:
            txt_line = f'it == {trial_idx}  ? "{payload}" :'
        else:
            txt_line = f'it == {trial_idx} ? "{payload}" :'
        txt_lines.append(txt_line)

        csv_rows.append([
            trial_idx,
            block_idx,
            code,
            states[0],  # A
            states[1],  # B
            states[2],  # C
            states[3],  # D
            states[4],  # E
            states[5],  # F
            flow
        ])

    txt_lines.append('"None, None, None, None, 0"')

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
    SEED = None   # None = different random order each run; integer = reproducible

    save_bonsai_and_csv(
        block_num=BLOCK_NUM,
        seed=SEED,
        txt_file="bonsai_conditions_shuffled.txt",
        csv_file="trial_table.csv"
    )
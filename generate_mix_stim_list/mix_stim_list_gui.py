from pathlib import Path
import csv
import random
import tkinter as tk
from tkinter import filedialog, messagebox


ODOR_VALUES = [1, 2, 3, 5, 6, 7]
DEFAULT_CARRIER_TARGET_FLOW = 549
DEFAULT_ODOR_FLOW = 100


def code_to_states(code: int):
    # 0-63 -> A-F, MSB to LSB.
    return [int(bit) for bit in f"{code:06b}"]


def states_to_type(states):
    return "".join(str(state) for state in states)


def states_to_txt_values(states):
    return [
        odor_value if state else 0
        for state, odor_value in zip(states, ODOR_VALUES)
    ]


def lane_counts(states):
    # Values 1, 3, 5 share carrier output 1; values 2, 4, 6 share carrier output 2.
    lane1_count = states[0] + states[2] + states[4]
    lane2_count = states[1] + states[3] + states[5]
    return lane1_count, lane2_count


def carrier_out(carrier_target_flow: int, odor_flow: int, active_count: int):
    value = carrier_target_flow - odor_flow * active_count
    if value < 0:
        raise ValueError(
            f"Carrier flow would be negative: target={carrier_target_flow}, "
            f"odor_flow={odor_flow}, active_count={active_count}."
        )
    return value


def make_trial_list(blocks: int, seed=None, shuffle=True):
    rng = random.Random(seed)
    trials = []

    for block in range(1, blocks + 1):
        codes = list(range(64))
        if shuffle:
            rng.shuffle(codes)
        for code in codes:
            trials.append((block, code))

    return trials


def save_bonsai_and_csv(
    blocks: int,
    seed,
    shuffle: bool,
    txt_path: Path,
    csv_path: Path,
    carrier_target_flow: int,
    odor_flow: int,
):
    if blocks < 1:
        raise ValueError("Blocks must be at least 1.")
    if carrier_target_flow < 0:
        raise ValueError("Carrier target flow must be 0 or greater.")
    if odor_flow < 0:
        raise ValueError("Odor flow must be 0 or greater.")

    trials = make_trial_list(blocks, seed=seed, shuffle=shuffle)
    txt_lines = []
    csv_rows = []

    for trial_idx, (block, code) in enumerate(trials, start=1):
        states = code_to_states(code)
        txt_values = states_to_txt_values(states)
        lane1_count, lane2_count = lane_counts(states)
        carrier1_out = carrier_out(carrier_target_flow, odor_flow, lane1_count)
        carrier2_out = carrier_out(carrier_target_flow, odor_flow, lane2_count)
        payload_values = [*txt_values, carrier1_out, carrier2_out]
        payload = ",".join(str(value) for value in payload_values)
        spacing = "  " if trial_idx < 10 else " "
        txt_lines.append(f'it == {trial_idx}{spacing}? "{payload}" :')

        odor_number = sum(states)
        total_odor_flow = odor_number * odor_flow
        flow = odor_flow if odor_number > 0 else 0
        type_str = states_to_type(states)
        a, b, c, d, e, f = states

        csv_rows.append([
            trial_idx,
            block,
            a,
            b,
            c,
            d,
            e,
            f,
            type_str,
            code,
            odor_number,
            flow,
            total_odor_flow,
            carrier1_out,
            carrier2_out,
            payload,
        ])

    fallback = ",".join(["0", "0", "0", "0", "0", "0", str(carrier_target_flow), str(carrier_target_flow)])
    txt_lines.append(f'"{fallback}"')
    txt_path.write_text("\n".join(txt_lines), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "trial",
            "block",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "type",
            "code",
            "odor_number",
            "flow",
            "total_odor_flow",
            "carrier1_out",
            "carrier2_out",
            "payload",
        ])
        writer.writerows(csv_rows)

    return len(csv_rows)


class MixStimListGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Six Odor All-64 Mixture Generator")
        self.resizable(False, False)

        output_dir = Path.home() / "Documents" / "odor_stimuli"
        self.blocks_var = tk.IntVar(value=10)
        self.carrier_target_flow_var = tk.IntVar(value=DEFAULT_CARRIER_TARGET_FLOW)
        self.odor_flow_var = tk.IntVar(value=DEFAULT_ODOR_FLOW)
        self.shuffle_var = tk.BooleanVar(value=True)
        self.seed_var = tk.StringVar(value="")
        self.prefix_var = tk.StringVar(value="six_odor_all64mix_type_conc_up")
        self.output_dir_var = tk.StringVar(value=str(output_dir))
        self.status_var = tk.StringVar(value="")

        self._build_layout()

    def _build_layout(self):
        frame = tk.Frame(self, padx=14, pady=14)
        frame.grid(row=0, column=0, sticky="nsew")

        settings = tk.LabelFrame(frame, text="Settings", padx=10, pady=10)
        settings.grid(row=0, column=0, sticky="ew")

        tk.Label(settings, text="Blocks").grid(row=0, column=0, sticky="w")
        tk.Spinbox(settings, from_=1, to=999, width=8, textvariable=self.blocks_var).grid(
            row=0, column=1, sticky="w", padx=(8, 18)
        )

        tk.Label(settings, text="Carrier target flow").grid(row=0, column=2, sticky="w")
        tk.Spinbox(
            settings,
            from_=0,
            to=9999,
            width=8,
            textvariable=self.carrier_target_flow_var,
        ).grid(row=0, column=3, sticky="w", padx=(8, 0))

        tk.Label(settings, text="Odor flow / odor").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Spinbox(settings, from_=0, to=9999, width=8, textvariable=self.odor_flow_var).grid(
            row=1, column=1, sticky="w", padx=(8, 18), pady=(10, 0)
        )

        tk.Label(settings, text="Seed (blank=random)").grid(row=1, column=2, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=10, textvariable=self.seed_var).grid(
            row=1, column=3, sticky="w", padx=(8, 0), pady=(10, 0)
        )

        tk.Checkbutton(
            settings,
            text="Shuffle all 64 mixtures inside each block",
            variable=self.shuffle_var,
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))

        tk.Label(settings, text="File prefix").grid(row=3, column=0, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=48, textvariable=self.prefix_var).grid(
            row=3, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        tk.Label(settings, text="Output folder").grid(row=4, column=0, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=48, textvariable=self.output_dir_var).grid(
            row=4, column=1, columnspan=2, sticky="ew", padx=(8, 8), pady=(10, 0)
        )
        tk.Button(settings, text="Browse", command=self._choose_output_dir).grid(
            row=4, column=3, sticky="ew", pady=(10, 0)
        )

        explanation = (
            "Output TXT payload: A,B,C,D,E,F,carrier1_out,carrier2_out\n"
            "Example with target=549 and odor_flow=100: "
            "1,2,0,0,6,7 -> 1,2,0,0,6,7,349,349"
        )
        tk.Label(frame, text=explanation, justify="left", fg="#555555").grid(
            row=1, column=0, sticky="w", pady=(12, 0)
        )

        actions = tk.Frame(frame)
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        tk.Button(actions, text="Generate TXT + CSV", command=self._generate).grid(row=0, column=0, sticky="w")
        tk.Label(actions, textvariable=self.status_var, anchor="w", width=58).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )

    def _choose_output_dir(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if selected:
            self.output_dir_var.set(selected)

    def _generate(self):
        try:
            blocks = int(self.blocks_var.get())
            carrier_target_flow = int(self.carrier_target_flow_var.get())
            odor_flow = int(self.odor_flow_var.get())
            seed_text = self.seed_var.get().strip()
            seed = None if seed_text == "" else int(seed_text)
            prefix = self.prefix_var.get().strip()
            output_dir = Path(self.output_dir_var.get()).expanduser()

            if not prefix:
                raise ValueError("File prefix cannot be empty.")

            output_dir.mkdir(parents=True, exist_ok=True)
            txt_path = output_dir / f"{prefix}.txt"
            csv_path = output_dir / f"{prefix}.csv"
            trial_count = save_bonsai_and_csv(
                blocks=blocks,
                seed=seed,
                shuffle=self.shuffle_var.get(),
                txt_path=txt_path,
                csv_path=csv_path,
                carrier_target_flow=carrier_target_flow,
                odor_flow=odor_flow,
            )

            self.status_var.set(f"Saved {trial_count} trials")
        except Exception as exc:
            messagebox.showerror("Could not generate files", str(exc))


if __name__ == "__main__":
    MixStimListGui().mainloop()

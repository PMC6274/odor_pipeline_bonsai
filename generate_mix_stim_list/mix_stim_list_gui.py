from pathlib import Path
import csv
import random
import tkinter as tk
from tkinter import filedialog, messagebox


ODOR_VALUES = [1, 2, 3, 5, 6, 7]
DEFAULT_NO_ODOR_CARRIER_PER_LINE = 499
DEFAULT_ODOR_FLOW = 100
MODE_MIXTURE = "Mixture all 64"
MODE_SINGLE_ODOR = "Single odor only"


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


def side_counts(states):
    # Physical layout:
    # A-C are device 1 odors; D-F are device 2 odors.
    # Channel 4 is not used on either device.
    side1_count = states[0] + states[1] + states[2]
    side2_count = states[3] + states[4] + states[5]
    return side1_count, side2_count


def carrier_out(no_odor_carrier_per_line: int, odor_flow: int, side_odor_count: int):
    # Keep each side total balanced:
    # side odor flow + side carrier = no_odor_carrier_per_line.
    value = no_odor_carrier_per_line - odor_flow * side_odor_count
    if value < 0:
        raise ValueError(
            f"Carrier flow would be negative: no_odor_carrier_per_line={no_odor_carrier_per_line}, "
            f"odor_flow={odor_flow}, side_odor_count={side_odor_count}."
        )
    return value


def mode_codes(mode: str):
    if mode == MODE_MIXTURE:
        return list(range(64))
    if mode == MODE_SINGLE_ODOR:
        return [32, 16, 8, 4, 2, 1]
    raise ValueError(f"Unknown mode: {mode}")


def make_trial_list(blocks: int, seed=None, shuffle=True, mode=MODE_MIXTURE):
    rng = random.Random(seed)
    trials = []

    for block in range(1, blocks + 1):
        codes = mode_codes(mode)
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
    no_odor_carrier_per_line: int,
    odor_flow: int,
    mode: str = MODE_MIXTURE,
):
    if blocks < 1:
        raise ValueError("Blocks must be at least 1.")
    if no_odor_carrier_per_line < 0:
        raise ValueError("No-odor carrier / line must be 0 or greater.")
    if odor_flow < 0:
        raise ValueError("Odor flow must be 0 or greater.")

    trials = make_trial_list(blocks, seed=seed, shuffle=shuffle, mode=mode)
    txt_lines = []
    csv_rows = []

    for trial_idx, (block, code) in enumerate(trials, start=1):
        states = code_to_states(code)
        txt_values = states_to_txt_values(states)
        odor_number = sum(states)
        side1_count, side2_count = side_counts(states)
        carrier1_out = carrier_out(no_odor_carrier_per_line, odor_flow, side1_count)
        carrier2_out = carrier_out(no_odor_carrier_per_line, odor_flow, side2_count)
        payload_values = [*txt_values, carrier1_out, carrier2_out]
        payload = ",".join(str(value) for value in payload_values)
        spacing = "  " if trial_idx < 10 else " "
        txt_lines.append(f'it == {trial_idx}{spacing}? "{payload}" :')

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
            carrier1_out + side1_count * odor_flow,
            carrier2_out + side2_count * odor_flow,
            payload,
        ])

    fallback = ",".join(["0", "0", "0", "0", "0", "0", str(no_odor_carrier_per_line), str(no_odor_carrier_per_line)])
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
            "side1_total_flow",
            "side2_total_flow",
            "payload",
        ])
        writer.writerows(csv_rows)

    return len(csv_rows)


class MixStimListGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Six Odor Stim List Generator")
        self.resizable(False, False)

        output_dir = Path.home() / "Documents" / "odor_stimuli"
        self.blocks_var = tk.IntVar(value=10)
        self.no_odor_carrier_per_line_var = tk.IntVar(value=DEFAULT_NO_ODOR_CARRIER_PER_LINE)
        self.odor_flow_var = tk.IntVar(value=DEFAULT_ODOR_FLOW)
        self.mode_var = tk.StringVar(value=MODE_MIXTURE)
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

        tk.Label(settings, text="No-odor carrier / line").grid(row=0, column=2, sticky="w")
        tk.Spinbox(
            settings,
            from_=0,
            to=9999,
            width=8,
            textvariable=self.no_odor_carrier_per_line_var,
        ).grid(row=0, column=3, sticky="w", padx=(8, 0))

        tk.Label(settings, text="Mode").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.OptionMenu(settings, self.mode_var, MODE_MIXTURE, MODE_SINGLE_ODOR).grid(
            row=1, column=1, sticky="ew", padx=(8, 18), pady=(10, 0)
        )

        tk.Label(settings, text="Odor flow / odor").grid(row=2, column=0, sticky="w", pady=(10, 0))
        tk.Spinbox(settings, from_=0, to=9999, width=8, textvariable=self.odor_flow_var).grid(
            row=2, column=1, sticky="w", padx=(8, 18), pady=(10, 0)
        )

        tk.Label(settings, text="Seed (blank=random)").grid(row=2, column=2, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=10, textvariable=self.seed_var).grid(
            row=2, column=3, sticky="w", padx=(8, 0), pady=(10, 0)
        )

        tk.Checkbutton(
            settings,
            text="Shuffle conditions inside each block",
            variable=self.shuffle_var,
        ).grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 0))

        tk.Label(settings, text="File prefix").grid(row=4, column=0, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=48, textvariable=self.prefix_var).grid(
            row=4, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        tk.Label(settings, text="Output folder").grid(row=5, column=0, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=48, textvariable=self.output_dir_var).grid(
            row=5, column=1, columnspan=2, sticky="ew", padx=(8, 8), pady=(10, 0)
        )
        tk.Button(settings, text="Browse", command=self._choose_output_dir).grid(
            row=5, column=3, sticky="ew", pady=(10, 0)
        )

        explanation = (
            "Output TXT payload: A,B,C,D,E,F,carrier1_out,carrier2_out\n"
            "Each side stays balanced: side odor flow + side carrier = no-odor carrier / line.\n"
            "Single odor example with no-odor carrier/line=499 and odor_flow=100: "
            "A -> 1,0,0,0,0,0,399,499"
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
            no_odor_carrier_per_line = int(self.no_odor_carrier_per_line_var.get())
            odor_flow = int(self.odor_flow_var.get())
            mode = self.mode_var.get()
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
                no_odor_carrier_per_line=no_odor_carrier_per_line,
                odor_flow=odor_flow,
                mode=mode,
            )

            self.status_var.set(f"Saved {trial_count} trials ({mode})")
        except Exception as exc:
            messagebox.showerror("Could not generate files", str(exc))


if __name__ == "__main__":
    MixStimListGui().mainloop()

from pathlib import Path
import csv
import re
import tkinter as tk
from tkinter import filedialog, messagebox


CHANNELS_PER_DEVICE = 4
DEFAULT_CHANNEL_FLOW = 40
DEFAULT_TOTAL_FLOW = 900


def parse_sequence(text: str):
    text = text.strip()
    if not text:
        raise ValueError("Enter at least one odor number.")

    if re.search(r"[\s,;]", text):
        tokens = [token for token in re.split(r"[\s,;]+", text) if token]
    elif text.isdigit():
        # Compact notation: 11115 -> 1, 1, 1, 1, 5.
        tokens = list(text)
    else:
        raise ValueError("Use digits separated by spaces/commas, or compact digits 1-9.")

    try:
        sequence = [int(token) for token in tokens]
    except ValueError as exc:
        raise ValueError("Every odor must be a positive integer.") from exc

    if any(odor < 1 for odor in sequence):
        raise ValueError("Odor numbers start at 1.")
    return sequence


def odor_location(global_odor: int):
    device = ((global_odor - 1) // CHANNELS_PER_DEVICE) + 1
    channel = ((global_odor - 1) % CHANNELS_PER_DEVICE) + 1
    code = device * 10 + channel
    return device, channel, code


def write_sequence_files(
    sequence,
    device_count: int,
    repeats_per_block: int,
    blocks: int,
    txt_path: Path,
    csv_path: Path,
    channel_flow: int,
    total_flow: int,
):
    maximum_odor = device_count * CHANNELS_PER_DEVICE
    invalid = [odor for odor in sequence if odor > maximum_odor]
    if invalid:
        raise ValueError(
            f"Odor {invalid[0]} requires more than {device_count} device(s). "
            f"Valid odors are 1-{maximum_odor}."
        )
    if channel_flow < 0:
        raise ValueError("Channel flow must be 0 or greater.")
    if total_flow < channel_flow:
        raise ValueError("Total flow must be greater than or equal to channel flow.")

    carrier_out = total_flow - channel_flow
    txt_lines = []
    csv_rows = []
    trial = 1

    for block in range(1, blocks + 1):
        for repeat in range(1, repeats_per_block + 1):
            for position, global_odor in enumerate(sequence, start=1):
                device, channel, code = odor_location(global_odor)
                spacing = "  " if trial < 10 else " "
                txt_lines.append(f'it == {trial}{spacing}? "{code},{carrier_out}" :')
                csv_rows.append([
                    trial,
                    block,
                    repeat,
                    position,
                    global_odor,
                    device,
                    channel,
                    code,
                    channel_flow,
                    carrier_out,
                    total_flow,
                ])
                trial += 1

    txt_lines.append(f'"0,{total_flow}"')
    txt_path.write_text("\n".join(txt_lines), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "trial",
            "block",
            "repeat_in_block",
            "position_in_sequence",
            "global_odor",
            "device",
            "device_odor",
            "code",
            "channel_flow",
            "carrier_out",
            "total_flow",
        ])
        writer.writerows(csv_rows)

    return len(csv_rows)


class CustomSequenceGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Custom Odor Sequence Generator")
        self.resizable(False, False)

        output_dir = Path(__file__).resolve().parent
        self.devices_var = tk.IntVar(value=3)
        self.sequence_var = tk.StringVar(value="1234")
        self.repeats_var = tk.IntVar(value=1)
        self.blocks_var = tk.IntVar(value=1)
        self.channel_flow_var = tk.IntVar(value=DEFAULT_CHANNEL_FLOW)
        self.total_flow_var = tk.IntVar(value=DEFAULT_TOTAL_FLOW)
        self.prefix_var = tk.StringVar(value="custom_odor_sequence")
        self.output_dir_var = tk.StringVar(value=str(output_dir))
        self.status_var = tk.StringVar(value="")

        self._build_layout()

    def _build_layout(self):
        frame = tk.Frame(self, padx=14, pady=14)
        frame.grid(row=0, column=0)

        tk.Label(frame, text="Devices (1-9)").grid(row=0, column=0, sticky="w")
        tk.Spinbox(frame, from_=1, to=9, width=7, textvariable=self.devices_var).grid(
            row=0, column=1, sticky="w", padx=(8, 18)
        )
        tk.Label(frame, text="Blocks").grid(row=0, column=2, sticky="w")
        tk.Spinbox(frame, from_=1, to=999, width=7, textvariable=self.blocks_var).grid(
            row=0, column=3, sticky="w", padx=(8, 0)
        )

        tk.Label(frame, text="Odor sequence").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Entry(frame, width=44, textvariable=self.sequence_var).grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=(10, 0)
        )
        tk.Label(
            frame,
            text="Examples: 1234 or 11115; use commas/spaces for 10+: 1, 5, 12",
            fg="#555555",
        ).grid(row=2, column=1, columnspan=3, sticky="w")

        tk.Label(frame, text="Repeats / block").grid(row=3, column=0, sticky="w", pady=(10, 0))
        tk.Spinbox(frame, from_=1, to=999, width=7, textvariable=self.repeats_var).grid(
            row=3, column=1, sticky="w", padx=(8, 18), pady=(10, 0)
        )
        tk.Label(frame, text="Channel flow").grid(row=3, column=2, sticky="w", pady=(10, 0))
        tk.Spinbox(frame, from_=0, to=9999, width=7, textvariable=self.channel_flow_var).grid(
            row=3, column=3, sticky="w", padx=(8, 0), pady=(10, 0)
        )

        tk.Label(frame, text="Total flow").grid(row=4, column=0, sticky="w", pady=(10, 0))
        tk.Spinbox(frame, from_=1, to=9999, width=7, textvariable=self.total_flow_var).grid(
            row=4, column=1, sticky="w", padx=(8, 18), pady=(10, 0)
        )
        tk.Label(frame, text="File prefix").grid(row=4, column=2, sticky="w", pady=(10, 0))
        tk.Entry(frame, width=20, textvariable=self.prefix_var).grid(
            row=4, column=3, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        tk.Label(frame, text="Output folder").grid(row=5, column=0, sticky="w", pady=(10, 0))
        tk.Entry(frame, width=44, textvariable=self.output_dir_var).grid(
            row=5, column=1, columnspan=2, sticky="ew", padx=(8, 8), pady=(10, 0)
        )
        tk.Button(frame, text="Browse", command=self._choose_output).grid(
            row=5, column=3, sticky="ew", pady=(10, 0)
        )

        tk.Button(frame, text="Generate TXT + CSV", command=self._generate).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(14, 0)
        )
        tk.Label(frame, textvariable=self.status_var, anchor="w", width=48).grid(
            row=6, column=1, columnspan=3, sticky="e", pady=(14, 0)
        )

    def _choose_output(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if selected:
            self.output_dir_var.set(selected)

    def _generate(self):
        try:
            sequence = parse_sequence(self.sequence_var.get())
            devices = int(self.devices_var.get())
            repeats = int(self.repeats_var.get())
            blocks = int(self.blocks_var.get())
            channel_flow = int(self.channel_flow_var.get())
            total_flow = int(self.total_flow_var.get())
            prefix = self.prefix_var.get().strip()
            output_dir = Path(self.output_dir_var.get()).expanduser()

            if not 1 <= devices <= 9:
                raise ValueError("Devices must be between 1 and 9.")
            if repeats < 1 or blocks < 1:
                raise ValueError("Repeats and blocks must be at least 1.")
            if not prefix:
                raise ValueError("File prefix cannot be empty.")

            output_dir.mkdir(parents=True, exist_ok=True)
            txt_path = output_dir / f"{prefix}.txt"
            csv_path = output_dir / f"{prefix}.csv"
            trial_count = write_sequence_files(
                sequence,
                devices,
                repeats,
                blocks,
                txt_path,
                csv_path,
                channel_flow,
                total_flow,
            )
            self.status_var.set(f"Saved {trial_count} trials")
        except Exception as exc:
            messagebox.showerror("Could not generate files", str(exc))


if __name__ == "__main__":
    CustomSequenceGui().mainloop()

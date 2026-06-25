from pathlib import Path
import csv
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox


CHANNELS_PER_DEVICE = 4
CHANNEL_FLOW = 40
TOTAL_FLOW = 900
FALLBACK = "0,900"


def condition_label(index: int) -> str:
    if index < len(string.ascii_uppercase):
        return string.ascii_uppercase[index]
    return f"X{index + 1}"


def make_conditions(device_count: int, enabled_channels_by_device):
    conditions = []

    for device in range(1, device_count + 1):
        for channel in enabled_channels_by_device.get(device, []):
            label = condition_label(len(conditions))
            code = device * 10 + channel
            conditions.append({
                "label": label,
                "device": device,
                "device_odor": channel,
                "code": code,
            })

    return conditions


def write_stim_files(
    conditions,
    repeats: int,
    txt_path: Path,
    csv_path: Path,
    channel_flow: int = CHANNEL_FLOW,
    total_flow: int = TOTAL_FLOW,
):
    if not conditions:
        raise ValueError("Select at least one enabled channel.")
    if channel_flow < 0:
        raise ValueError("Channel flow must be 0 or greater.")
    if total_flow < channel_flow:
        raise ValueError("Total flow must be greater than or equal to channel flow.")

    txt_lines = []
    csv_rows = []
    condition_labels = [condition["label"] for condition in conditions]
    carrier_out = total_flow - channel_flow
    trial_idx = 1

    for block_idx in range(1, repeats + 1):
        block_conditions = conditions.copy()
        random.shuffle(block_conditions)

        for condition in block_conditions:
            states = [
                1 if label == condition["label"] else 0
                for label in condition_labels
            ]
            type_str = "".join(str(state) for state in states)
            payload = f'{condition["code"]},{carrier_out}'

            if trial_idx < 10:
                txt_lines.append(f'it == {trial_idx}  ? "{payload}" :')
            else:
                txt_lines.append(f'it == {trial_idx} ? "{payload}" :')

            csv_rows.append([
                trial_idx,
                block_idx,
                condition["label"],
                *states,
                type_str,
                condition["code"],
                condition["device"],
                condition["device_odor"],
                channel_flow,
                channel_flow,
                carrier_out,
            ])
            trial_idx += 1

    txt_lines.append(f'"{FALLBACK}"')
    txt_path.write_text("\n".join(txt_lines), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trial",
            "block",
            "odor",
            *condition_labels,
            "type",
            "code",
            "device",
            "device_odor",
            "flow",
            "total_odor_flow",
            "carrier_out",
        ])
        writer.writerows(csv_rows)

    return len(csv_rows)


class StimListGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Stim List Generator")
        self.resizable(False, False)
        self.output_dir = Path(__file__).resolve().parent
        self.channel_vars = {}

        self.device_count_var = tk.IntVar(value=3)
        self.repeats_var = tk.IntVar(value=25)
        self.channel_flow_var = tk.IntVar(value=CHANNEL_FLOW)
        self.total_flow_var = tk.IntVar(value=TOTAL_FLOW)
        self.prefix_var = tk.StringVar(value="stim_3device_9odor_25blocks")
        self.output_dir_var = tk.StringVar(value=str(self.output_dir))

        self._build_layout()
        self._rebuild_channels()

    def _build_layout(self):
        outer = tk.Frame(self, padx=14, pady=14)
        outer.grid(row=0, column=0, sticky="nsew")

        settings = tk.LabelFrame(outer, text="Settings", padx=10, pady=10)
        settings.grid(row=0, column=0, sticky="ew")

        tk.Label(settings, text="Devices").grid(row=0, column=0, sticky="w")
        tk.Spinbox(
            settings,
            from_=1,
            to=9,
            width=6,
            textvariable=self.device_count_var,
            command=self._rebuild_channels,
        ).grid(row=0, column=1, sticky="w", padx=(8, 18))

        tk.Label(settings, text="Repeats / blocks").grid(row=0, column=2, sticky="w")
        tk.Spinbox(
            settings,
            from_=1,
            to=999,
            width=6,
            textvariable=self.repeats_var,
        ).grid(row=0, column=3, sticky="w", padx=(8, 0))

        tk.Label(settings, text="Channel flow").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Spinbox(
            settings,
            from_=0,
            to=900,
            width=6,
            textvariable=self.channel_flow_var,
        ).grid(row=1, column=1, sticky="w", padx=(8, 18), pady=(10, 0))

        tk.Label(settings, text="Total flow").grid(row=1, column=2, sticky="w", pady=(10, 0))
        tk.Spinbox(
            settings,
            from_=1,
            to=9999,
            width=6,
            textvariable=self.total_flow_var,
        ).grid(row=1, column=3, sticky="w", padx=(8, 0), pady=(10, 0))

        tk.Label(settings, text="File prefix").grid(row=2, column=0, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=42, textvariable=self.prefix_var).grid(
            row=2,
            column=1,
            columnspan=3,
            sticky="ew",
            padx=(8, 0),
            pady=(10, 0),
        )

        tk.Label(settings, text="Output folder").grid(row=3, column=0, sticky="w", pady=(10, 0))
        tk.Entry(settings, width=42, textvariable=self.output_dir_var).grid(
            row=3,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(8, 8),
            pady=(10, 0),
        )
        tk.Button(settings, text="Browse", command=self._choose_output_dir).grid(
            row=3,
            column=3,
            sticky="ew",
            pady=(10, 0),
        )

        self.channels_frame = tk.LabelFrame(outer, text="Enabled Channels", padx=10, pady=10)
        self.channels_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        actions = tk.Frame(outer)
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        tk.Button(actions, text="Generate TXT + CSV", command=self._generate).grid(
            row=0,
            column=0,
            sticky="w",
        )
        self.status_var = tk.StringVar(value="")
        tk.Label(actions, textvariable=self.status_var, anchor="w", width=58).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(12, 0),
        )

    def _rebuild_channels(self):
        for child in self.channels_frame.winfo_children():
            child.destroy()

        self.channel_vars = {}
        device_count = max(1, int(self.device_count_var.get()))

        for device in range(1, device_count + 1):
            tk.Label(self.channels_frame, text=f"Device {device}").grid(
                row=device - 1,
                column=0,
                sticky="w",
                pady=2,
            )

            for channel in range(1, CHANNELS_PER_DEVICE + 1):
                var = tk.BooleanVar(value=True)
                self.channel_vars[(device, channel)] = var
                tk.Checkbutton(
                    self.channels_frame,
                    text=f"Ch {channel}",
                    variable=var,
                ).grid(row=device - 1, column=channel, sticky="w", padx=(10, 0), pady=2)

    def _choose_output_dir(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if selected:
            self.output_dir_var.set(selected)

    def _enabled_channels_by_device(self):
        device_count = max(1, int(self.device_count_var.get()))
        enabled = {}

        for device in range(1, device_count + 1):
            channels = [
                channel
                for channel in range(1, CHANNELS_PER_DEVICE + 1)
                if self.channel_vars[(device, channel)].get()
            ]
            enabled[device] = channels

        return enabled

    def _generate(self):
        try:
            device_count = max(1, int(self.device_count_var.get()))
            repeats = max(1, int(self.repeats_var.get()))
            channel_flow = max(0, int(self.channel_flow_var.get()))
            total_flow = max(1, int(self.total_flow_var.get()))
            prefix = self.prefix_var.get().strip()
            output_dir = Path(self.output_dir_var.get()).expanduser()

            if not prefix:
                raise ValueError("File prefix cannot be empty.")

            output_dir.mkdir(parents=True, exist_ok=True)
            conditions = make_conditions(device_count, self._enabled_channels_by_device())

            txt_path = output_dir / f"{prefix}.txt"
            csv_path = output_dir / f"{prefix}.csv"
            trial_count = write_stim_files(
                conditions,
                repeats,
                txt_path,
                csv_path,
                channel_flow=channel_flow,
                total_flow=total_flow,
            )

            carrier_out = total_flow - channel_flow
            self.status_var.set(
                f"Saved {trial_count} trials; carrier_out={carrier_out}"
            )
        except Exception as exc:
            messagebox.showerror("Could not generate files", str(exc))


if __name__ == "__main__":
    StimListGui().mainloop()

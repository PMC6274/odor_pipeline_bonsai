# odor_pipeline_bonsai

Bonsai workflows and tools for shuffled-block odor delivery experiments. The
stimulus generator supports **one to nine Harp Olfactometers**; the current main
workflow, `3device1blank.bonsai`, is configured for three devices.

- Main repo: https://github.com/PMC6274/odor_pipeline_bonsai/tree/main  
- Harp Olfactometer docs: https://fchampalimaud.github.io/olfactometer-docs/docs/overview  

## Deploy on another Windows PC

Windows may mark every file from a downloaded ZIP as coming from the internet.
This can block PowerShell scripts, generated C# files, and extension DLLs. After
copying or extracting the project on a new PC, double-click:

```text
scripts\setup_windows.cmd
```

This removes the Windows zone marker from files inside this project only. It
does **not** permanently change the machine or user PowerShell execution policy.

For the cleanest ZIP deployment, unblock before extraction: right-click the ZIP,
choose **Properties**, check **Unblock**, click **OK**, and then extract it. A Git
clone normally does not carry these ZIP zone markers.

If local policy still prevents direct `.ps1` execution, use the command wrapper:

```cmd
scripts\run_experiment.cmd experiments\example.yaml -OpenOnly
```

It runs `run_experiment.ps1` with a process-only execution-policy bypass. You can
also use `-ValidateOnly` or no mode flag with this wrapper. Company
Group Policy can override process-level settings; contact the PC administrator
if both setup and the wrapper are denied.

For common launch modes, use these batch files. The root `start_experiment.bat`
is the normal day-to-day launcher: double-click it, select a YAML file in the
file picker, and Bonsai opens with that YAML loaded. From a terminal, you can
still pass a YAML file as the first argument.

| File | What it does |
| --- | --- |
| `scripts\validate_experiment.bat` | Checks the YAML and prints the Bonsai properties without opening Bonsai. |
| `scripts\open_experiment.bat` | Opens Bonsai with the YAML values loaded, but does not start the workflow. |
| `start_experiment.bat` | Opens a YAML file picker, then opens Bonsai with the selected YAML loaded. It does not start the workflow. |

Example:

```cmd
start_experiment.bat experiments\2026-07-01_mouse-001.yaml
```

## Protocol

- **Stimulus generator:** 1–9 Harp Olfactometers.
- **Main workflow:** `3device1blank.bonsai` controls three olfactometers.
- **Channels:** up to four selectable odor channels per device.
- **Trial order:** every enabled channel appears once per block, shuffled without
  replacement.
- **Blocks:** selected as `Repeats / blocks` in the generator GUI.
- **Timing and flow:** configured per experiment in YAML (see below).

The trial count is `enabled channels across all devices × blocks`. For example,
three enabled channels on each of nine devices repeated for 25 blocks produces
`27 × 25 = 675` trials. Only generate device codes supported by the Bonsai
workflow you plan to use; `3device1blank.bonsai` uses devices 1–3.

## Generate a stimulus list with the Python GUI

The generator requires Python 3 with Tkinter. On the acquisition computer,
double-click:

```text
generate_stim_list\run_stim_list_gui.bat
```

The batch file currently uses `D:\software\miniconda\python.exe`. If Python is
installed elsewhere, edit `PYTHON_EXE` in the batch file. You can also launch it
from PowerShell:

```powershell
python .\generate_stim_list\stim_list_gui.py
```

In the GUI:

1. Set **Devices** from 1 to 9. When using `3device1blank.bonsai`, select 3 or
   fewer because that workflow defines only three device connections.
2. Set **Repeats / blocks**.
3. Check the enabled channels for every device. At least one channel must remain
   enabled.
4. Set **Channel flow** and **Total flow**. Total flow must be greater than or
   equal to channel flow.
5. Enter a descriptive **File prefix** and choose an **Output folder**. The
   default output folder is the Windows Documents folder:
   `C:\Users\<you>\Documents\odor_stimuli`.
6. Click **Generate TXT + CSV**.

The GUI creates:

- `<prefix>.txt`: the shuffled conditional expression for Bonsai.
- `<prefix>.csv`: the matching trial table, including trial, block, odor label,
  device, channel, device/channel code, and flow values.

Every block is shuffled independently, and a new random order is generated each
time. Keep the CSV file with the recorded experiment data.

### Generate an exact custom odor sequence

Use the separate custom-sequence GUI when trial order must be specified rather
than shuffled:

```text
generate_stim_list\run_custom_sequence_gui.bat
```

Or launch it directly:

```powershell
python .\generate_stim_list\custom_sequence_gui.py
```

Odors are numbered globally using four channels per device:

| Global odor | Device | Device channel | Payload code |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 1 | 11 |
| 4 | 1 | 4 | 14 |
| 5 | 2 | 1 | 21 |
| 8 | 2 | 4 | 24 |
| 9 | 3 | 1 | 31 |

Compact input is supported for odors 1–9. For example, `1234` produces odors
1,2,3,4 and `11115` produces 1,1,1,1,5, where odor 5 is device 2/channel 1.
For multi-digit odor numbers, use spaces or commas, such as `1, 5, 12`.

The custom GUI preserves the entered order. **Repeats / block** repeats the
entire sequence inside each block, and **Blocks** repeats that block. Thus,
`11115`, two repeats per block, and three blocks produces `5 × 2 × 3 = 30`
trials. Its TXT and CSV files use the same format and YAML workflow as the
shuffled generator.

### Generate six-odor mixture stimuli

Use the mixture GUI for `six_odor_all64mix_type_conc_up.bonsai`:

```text
generate_mix_stim_list\run_mix_stim_list_gui.bat
```

The GUI generates all 64 binary mixtures of six odors for each block, optionally
shuffled within each block. The TXT payload has eight comma-separated values:

```text
A,B,C,D,E,F,carrier1_out,carrier2_out
```

For example, with carrier target flow `549` and odor flow `100`:

```text
it == 52 ? "1,2,0,0,6,7,349,349" :
```

The matching CSV includes `A`-`F`, `type`, `code`, `odor_number`, `flow`,
`total_odor_flow`, `carrier1_out`, `carrier2_out`, and the final `payload`.

### Select the generated stimulus list in YAML

Set `Protocol.StimulusFile` to the generated TXT file. Relative paths are
resolved from the repository root. You can also use a Windows Documents path
with `%USERPROFILE%`, which the launcher expands before opening Bonsai:

```yaml
Protocol:
  StimulusFile: "%USERPROFILE%/Documents/odor_stimuli/stim_3device_9x25_06062026.txt"
```

When `scripts\run_experiment.ps1` opens Bonsai, it reads this file and assigns the full
contents to `Odor loop.Expression`. To preserve the expression's required double
quotes, the launcher creates a temporary `3device1blank.runtime.bonsai` beside
the main workflow, opens that copy, and removes it when Bonsai closes. The source
workflow is not overwritten. Manual copy/paste is not needed. Keep the matching
CSV beside the experiment data and compare its first few trials before connecting
odors.

## Configure experiments with YAML

Experiment metadata and runtime parameters are stored in YAML files under
`experiments/`. The launcher validates a YAML file and applies its values to the
externalized properties in `3device1blank.bonsai` before Bonsai opens.

### Launch with the YAML file picker

For normal use, double-click `start_experiment.bat` in the project root. It opens
a file picker starting in `experiments/`. Select the session YAML, and Bonsai
will open with all YAML parameters and the stimulus expression applied.

This is open-only/view-only: it does **not** start the workflow.

You can also pass a YAML path from a terminal:

```powershell
.\start_experiment.bat experiments\example.yaml
```

Use this mode to inspect `Define Device`, `Initialize Device`, `Odor loop`, and
`Logging` before every experiment. Close Bonsai when finished; the temporary
runtime workflow is removed automatically.

### One-time setup

The repository includes a local `Bonsai.Sgen` tool manifest, the JSON Schema,
generated Bonsai operators, and the extensions project. Restore and build them
from PowerShell in the repository root:

```powershell
dotnet tool restore
dotnet bonsai.sgen schemas\experiment.schema.json -o Extensions --serializer yaml --namespace OdorExperiment
dotnet build Extensions\Extensions.csproj
```

In Bonsai, select **Tools > Reload Extensions** after regenerating or rebuilding
the extension.

### Create a session configuration

Copy the example instead of editing it in place:

```powershell
Copy-Item experiments\example.yaml experiments\2026-07-01_mouse-001.yaml
```

Edit the copied file. Its four sections are:

- `Metadata`: experiment ID, subject, operator, start time, and notes.
- `Hardware`: the three olfactometer COM ports and White Rabbit COM port.
- `Controls`: keyboard shortcuts for flow, PPS, and experiment start.
- `Protocol`: stimulus file, trial count, timing in seconds, ISI bounds, and flow values.
- `Output`: data directory and optional webhook.

Logging output is configured in the `Output` section. The example writes to the
Windows Documents folder. The launcher expands `%USERPROFILE%` before passing
the path to Bonsai:

```yaml
Output:
  DataDirectory: "%USERPROFILE%/Documents/odor_experiment_logs"
  Webhook: ""
```

Timing values in YAML are written as seconds:

```yaml
Protocol:
  TrialCount: 90
  ChargeSeconds: 30
  DeliverySeconds: 4
  FlushSeconds: 1
  RechargeSeconds: 1
  FlowAdjustmentSeconds: 3
  TimeBeforeOdorSeconds: 0
  IsiMinimumSeconds: 20
  IsiMaximumSeconds: 30
```

Flow values are integers from `0` to `1000`. `MainFlow`, `ControlFlow`, and
`FlushFlow` still control the three channel-4 carrier/flush outputs. The per-odor
channel flow values map directly to the Bonsai externalized properties:

```yaml
Protocol:
  MainFlow: 925
  ControlFlow: 958
  FlushFlow: 986
  D1C0Flow: 0
  D1C1Flow: 0
  D1C2Flow: 0
  D1C3Flow: 0
  D2C0Flow: 0
  D2C1Flow: 0
  D2C2Flow: 0
  D2C3Flow: 0
  D3C0Flow: 0
  D3C1Flow: 0
  D3C2Flow: 0
  D3C3Flow: 0
```

Keyboard controls are also configured in YAML:

```yaml
Controls:
  StartFlow: "Shift+F"
  DisableFlow: "Shift+D"
  StartPps: "Shift+W"
  EndPps: "Shift+Q"
  StartExperiment: "Shift+Space"
```

Use Bonsai chord syntax such as `Shift+W`, `Ctrl+P`, or `Shift+Space`. Each action
must have a distinct shortcut. Run with `-OpenOnly` after changing a shortcut and
confirm the assigned value in the Properties panel.

The launcher converts these numbers to the `00:00:00` `TimeSpan` format expected
by Bonsai command-line properties. Do not write `PT30S` in a Bonsai property.

### Validate before opening Bonsai

Check the file and print every property that will be assigned:

```powershell
.\scripts\run_experiment.ps1 experiments\2026-07-01_mouse-001.yaml -ValidateOnly
```

Validation rejects missing required values, malformed COM ports, negative
durations, flow values outside 0–1000, and an ISI maximum below its minimum. A
trial count mismatch or non-sequential stimulus TXT produces a warning but does
not prevent Bonsai from opening; `Protocol.TrialCount` remains the value assigned
to `Odor loop.Count`.

### Inspect parameters without running hardware

Open `3device1blank.bonsai` with the YAML values applied, but do not start the
workflow:

```powershell
.\scripts\run_experiment.ps1 experiments\2026-07-01_mouse-001.yaml -OpenOnly
```

Select `Define Device`, `Initialize Device`, `Odor loop`, and `Logging` in the
Bonsai editor to inspect their assigned properties.

### Open the experiment

Double-click `start_experiment.bat` and choose the session YAML. Or from a
terminal, open the workflow in the Bonsai editor with the YAML values applied:

```powershell
.\start_experiment.bat experiments\2026-07-01_mouse-001.yaml
```

Always stop the workflow before editing YAML. Restart it through the launcher to
apply changes; editing the YAML does not update an already-running workflow.

## White Rabbit and SpikeGLX startup sequence

The White Rabbit auxiliary output is placed in PPS mode when the Bonsai workflow
launches. Use the following order so SpikeGLX is armed while PPS is off and both
recordings contain the synchronization pulses.

1. Open the experiment in Bonsai, but do not start the odor trials yet:

   ```powershell
   .\start_experiment.bat experiments\example.yaml
   ```

2. Confirm that the White Rabbit device connected at `Hardware.WhiteRabbitPort`
   is online. PPS starts automatically when the workflow initializes.
3. Use the key assigned to `Initialize Device.EndPPS` to turn **PPS off**.
4. In SpikeGLX, configure/confirm the White Rabbit PPS signal on the intended
   synchronization input, then start SpikeGLX recording first.
5. In the Bonsai control window, click **Logging** to start Bonsai logging.
6. Use the key assigned to `Initialize Device.StartPPS` to turn **PPS on** again.
   Confirm that PPS edges are visible in SpikeGLX before continuing.
7. Use the key assigned to `Initialize Device.StartFlow` to enable olfactometer
   flow. Confirm stable flow before odor delivery.
8. Use the key assigned to `Odor loop.Start_experiment` to begin the trials. The
   current experiment-start binding is `Shift+Space`.

The PPS, flow, and experiment controls come from the YAML `Controls` section. To
verify their bindings, open with `-OpenOnly`, select `Initialize Device` or
`Odor loop`, and check `StartPPS`, `EndPPS`, `StartFlow`, `DisableFlow`, and
`Start_experiment` in the Properties panel. Verify these keys before recording;
do not rely on memory after changing the YAML.

### End the experiment

Click the Bonsai **Stop** button. The workflow automatically performs its
shutdown sequence, including stopping PPS, stopping Bonsai logging, and disabling
olfactometer flow. Do not manually repeat those steps unless the automatic
shutdown reports an error.

After the Bonsai shutdown completes, stop SpikeGLX recording last so the final
PPS transition and experiment end remain captured in the SpikeGLX file.

Before each session, verify that PPS is absent after `EndPPS`, present after
`StartPPS`, and recorded on the expected SpikeGLX synchronization channel.

### Parameters applied from YAML

The launcher maps the stimulus expression, hardware ports, flows, timing, ISI
bounds, webhook, and output path into `3device1blank.bonsai` before it starts.

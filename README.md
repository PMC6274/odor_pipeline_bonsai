# Odor delivery with Bonsai

`3device_parallel_64mix.bonsai` is the main workflow for both single odors and
six-odor mixtures. Choose the trial sequence through a stimulus TXT file and
configure ports, timing, flow, and logging through YAML.

## Start here

1. Copy `experiments/example.yaml` to a session-specific YAML file.
2. Set the hardware COM ports, vacuum rate, flow values, timing, and output folder.
3. Double-click `start_experiment.bat` and select that YAML.
4. Confirm the properties in Bonsai before clicking Start.

The launcher opens the editor with the YAML values applied; it does not start
hardware. The supplied example and `64mix-launch-test.yaml` use one blank trial
for checking launch and parameter loading. They are not a complete odor protocol.

To validate without opening Bonsai:

```cmd
scripts\validate_experiment.bat experiments\example.yaml
```

To open a specific configuration:

```cmd
start_experiment.bat experiments\64mix-launch-test.yaml
```

Stop and close Bonsai before editing YAML, then launch again to load the changes.
The launcher uses a temporary `.runtime.bonsai` copy and removes it when the editor
closes. The source workflow is preserved.

## Folder layout

| Location | Purpose |
| --- | --- |
| `3device_parallel_64mix.bonsai` | Main experiment workflow |
| `start_experiment.bat` | Main launcher with YAML file picker |
| `experiments/` | Current YAML configurations |
| `stimuli/` | Stimulus TXT files and matching CSV trial tables |
| `tools/stimulus_generator/` | GUI for single odors or all 64 mixtures |
| `tools/vacuum_test/` | Standalone vacuum demo with startup buffer and status replies |
| `Extensions/` | Required workflow helpers and C# configuration operators |
| `scripts/` | Launch, validation, and Windows setup helpers |
| `schemas/` | YAML configuration schema |
| `docs/` | Schema setup and hardware manual |
| `archive/legacy/` | Older workflows, generators, configurations, and reference files |
| `.bonsai/` | Local Bonsai installation and packages; keep this folder |

## Generate stimuli

Double-click `tools/stimulus_generator/run_mix_stim_list_gui.bat`.
The wrapper uses `F:\miniconda3\python.exe` on this computer. On another computer,
edit `PYTHON_EXE` in the batch file to your Python installation, which must include Tkinter.

Choose **Single odor only** for the six individual odors, or **Mixture all 64**
for every binary combination, including blank. Set blocks, shuffle, optional seed,
carrier flow, and flow per odor. Choose `stimuli/` as the output folder to keep
session lists in the project; the GUI otherwise defaults to your Documents folder.

The generated TXT payload is:

```text
A,B,C,D,E,F,carrier1_out,carrier2_out
```

A–C use odor codes 1, 2, 3 on device 1; D–F use codes 5, 6, 7 on device 2.
Zero means that odor is absent. For example, only A at odor flow 100 with a
499-per-side total gives `1,0,0,0,0,0,399,499`.

Set `Protocol.StimulusFile` to the TXT path and `Protocol.TrialCount` to the
number of generated trials: 6 × blocks for single odors or 64 × blocks for mixtures.
Keep the matching CSV with your session data. Relative paths resolve from the
project root; `%USERPROFILE%` is supported.

The generator's odor-flow value calculates carrier compensation. It does not set
the hardware odor-channel flows: configure the corresponding `D1C0Flow`–`D1C2Flow`
and `D2C0Flow`–`D2C2Flow` values in YAML consistently with the generator.
Older two-value or seven-value stimulus lists in the archive are incompatible
with the main workflow's eight-value format.

## YAML parameters

- `Metadata`: session identification and notes.
- `Hardware`: three olfactometer ports, White Rabbit port, and `VacuumPort`.
- `Controls`: keyboard shortcuts for flow, PPS, and experiment start.
- `Protocol`: stimulus path/count, timing in seconds, initial olfactometer flows,
  and `VacuumRateMlPerMinute`.
- `Output`: data directory and optional webhook.

Vacuum example (merge into the existing sections):

```yaml
Hardware:
  VacuumPort: COM5
Protocol:
  VacuumRateMlPerMinute: 4500
```

These map to `Define Device.vaccum port` and
`Initialize Device.Vacuum (ml/min)`. Press **V** with the workflow running to send
the rate over serial at 115200 baud. The rate must be an integer from 0 to 5000;
it is not subject to the olfactometer's 0–1000 limit.
Bonsai shutdown does not currently send a vacuum-off command; use the controller
to stop vacuum when finished.

An Uno can reset when the serial connection opens. Vacuum commands are held for
the first two seconds of workflow startup: an early V press is retained (the latest
value wins if pressed repeatedly), then later presses send immediately. This is a
startup grace period, not a hardware-ready handshake.

The sketch in `ardunio_code/flow_contorl.ino` now reports `READY`, `OK <flow>`,
`ERR COMMAND`, or DAC errors. Upload this sketch with Arduino IDE to enable the
replies, then inspect `Initialize Device > VacuumStatus` in Bonsai while running.
`OK` means the DAC acknowledged the write, not that airflow was measured.
Both workflows now send `!<rate>\r\n`. The `!` marker resets a partial Arduino
command before reading the new rate, preventing leftover bytes from rejecting
the first press. Upload the latest sketch together with this workflow update;
older firmware does not accept the marker. Plain numeric commands remain accepted
by the updated sketch for manual Serial Monitor testing.
Close Bonsai before uploading so Arduino IDE can use the port. The sketch retains
its existing 3000 ml/min power-up setpoint and accepts integer commands from 0 to 5000.

Offline startup-buffer check (no serial ports opened):

```powershell
powershell.exe -NoProfile -File scripts/test_vacuum_startup.ps1
```

`MainFlow`, `ControlFlow`, and `FlushFlow` initialize channel 4 on devices 1–3.
Per-trial carrier values then update channel 4 on devices 1 and 2.
`FlushSeconds` currently controls a delay through `not_flush_odor.bonsai`,
without operating flush valves.

## Recording controls

Default YAML shortcuts are Shift+F (enable flow), Shift+D (disable flow),
Shift+W (PPS on), Shift+Q (PPS off), and Shift+Space (start trials).
Verify these in Bonsai before recording. Starting the workflow initializes
hardware and PPS; it does not automatically start the odor trials.

For synchronized recording: turn PPS off, start SpikeGLX recording, start Bonsai
Logging, turn PPS on, enable flow, then start the odor trials. Verify pulses in
SpikeGLX before proceeding. Stop Bonsai before stopping SpikeGLX so the end of
synchronization is recorded. The workflow's shutdown sequence turns PPS off,
stops logging, and disables olfactometer flow.

## Setup and development

On a new Windows PC, run `scripts/setup_windows.cmd` to unblock downloaded files.
First copy the complete `.bonsai` installation from the working PC: Git excludes
the executable and packages. See `docs/DEPLOYMENT.md` for the folder layout and
how to select an existing Bonsai installation.
See `docs/SCHEMA_SETUP.md` for C# configuration generation and build instructions.
The archive is historical reference and is excluded from the normal launch path;
see its README before attempting to reuse an old workflow.

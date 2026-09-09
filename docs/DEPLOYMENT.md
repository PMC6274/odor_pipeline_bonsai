# Deploy on another Windows PC

## Copy the working Bonsai installation

Git and GitHub ZIP downloads contain `.bonsai/Bonsai.config`, but exclude
`Bonsai.exe` and the `Packages` folder. `setup_windows.cmd` only unblocks files;
it does not install Bonsai or restore packages.

Copy the **complete `.bonsai` folder** from the working acquisition PC into the
project folder on the destination PC. For example:

```text
D:\projects\finklab\odor_pipeline_bonsai\
  start_experiment.bat
  3device_parallel_64mix.bonsai
  .bonsai\
    Bonsai.exe
    Bonsai.config
    Packages\
      ...all packages from the working PC...
  experiments\
  Extensions\
  scripts\
```

The directory is named `.bonsai` (with a leading dot) and is **inside** the
project directory. Copying only the executable is insufficient. In particular,
the YAML launcher needs `Packages/YamlDotNet.16.3.0/lib/net47/YamlDotNet.dll`.

Run `scripts/setup_windows.cmd`, then `scripts/validate_experiment.bat`.
Update the YAML COM ports, stimulus paths, and output directory for the new PC.
Open `start_experiment.bat` and check the properties before running hardware.

## Use an existing Bonsai installation

You can point the launcher at another installation containing the same workflow
packages as the working PC. For a single run:

```powershell
.\scripts\run_experiment.cmd experiments\64mix-launch-test.yaml -BonsaiExe "D:\software\Bonsai\Bonsai.exe" -OpenOnly
```

For normal double-click launch, set the user environment variable once:

```powershell
[Environment]::SetEnvironmentVariable('ODOR_BONSAI_EXE', 'D:\software\Bonsai\Bonsai.exe', 'User')
```

Use your actual installation path. Sign out and back in so Explorer's launches
inherit the new variable. Both the experiment and vacuum-demo launchers use it.
An explicit `-BonsaiExe` takes precedence over the environment variable; otherwise
the project-local `.bonsai/Bonsai.exe` is the default.
The YAML library is loaded from the chosen installation, with the project-local
package as a fallback. This does not install missing workflow packages.

## Stimulus generator

Install or use Python with Tkinter. Edit `PYTHON_EXE` in
`tools/stimulus_generator/run_mix_stim_list_gui.bat` to that PC's Python executable.
The `F:\miniconda3\python.exe` path is specific to the current working PC.

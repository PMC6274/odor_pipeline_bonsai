# Experiment schema setup

The schema in `schemas/experiment.schema.json` defines both experiment metadata
and the parameters used to run the odor workflow. Each session should use a copy
of `experiments/example.yaml` so the exact configuration is saved with the data.

## Generate the Bonsai operators

From the repository root, run:

```powershell
dotnet tool restore
dotnet bonsai.sgen schemas/experiment.schema.json -o Extensions --serializer yaml --namespace OdorExperiment
```

This generates C# operators in `Extensions`. Do not edit the generated file by
hand; update the schema and run the command again instead.

The current checkout supplements the generated classes with `Extensions/VacuumConfig.cs`
because the vacuum fields were added on a machine without the .NET SDK. After
successfully regenerating from the updated schema, remove that supplemental file
before building to avoid duplicate properties.

Open the workflow in Bonsai and choose **Tools > Reload Extensions**. The toolbox
will then include the generated `DeserializeFromYaml` operator and the generated
experiment record operators.

## Load a session file in Bonsai

The intended workflow is:

1. Read the YAML file as text.
2. Pass the text to the generated `DeserializeFromYaml` operator.
3. Pass the result through `ValidateExperimentConfig`. A bad configuration
   throws an error here, before any hardware command should be allowed to run.
4. Publish the validated `ExperimentConfig` through a `BehaviorSubject`.
5. Select properties such as `Protocol.ChargeSeconds` and map them to the
   corresponding workflow nodes.
6. Copy the YAML file into the output directory at experiment start, preserving
   the exact parameters and metadata alongside the recorded data.

YAML structure and types are checked during deserialization. The
`ValidateExperimentConfig` operator then rejects missing text values, invalid
COM-port names, negative durations, an inverted ISI range, and flow values
outside 0-1000. Vacuum rate is checked separately as a finite, non-negative value in ml/min.

## Starting a new experiment

Copy `experiments/example.yaml`, give it a session-specific name, and edit only
the copied file. Use forward slashes in paths so the YAML remains portable.

## Run `3device_parallel_64mix.bonsai` from YAML

First validate a configuration without opening Bonsai:

```powershell
.\scripts\run_experiment.ps1 experiments\example.yaml -ValidateOnly
```

Then open the main workflow with the YAML parameters applied, without starting
the workflow:

```powershell
.\start_experiment.bat experiments\example.yaml
```

You can also use the explicit open-only helper:

```powershell
.\scripts\open_experiment.bat experiments\example.yaml
```

The launcher maps the stimulus TXT contents, hardware ports, timing, flow, ISI,
webhook, and output path onto the externalized properties already present in
`3device_parallel_64mix.bonsai`.

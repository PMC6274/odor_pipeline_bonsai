import json
from pathlib import Path
from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field, RootModel

class Trial(BaseModel):
    parameters: str
    result: Optional[str] = Field(default=None)

class TaskHardware(BaseModel):
    olfactometer1_port: str = Field(description="Serial port for the first olfactometer.")
    olfactometer2_port: str = Field(description="Serial port for the second olfactometer.")
    white_rabbit_port: str = Field(description="Serial port for the White Rabbit timing system.")

class OdorLoop(BaseModel):
    """Parameters for the odor loop. These are used to generate the Bonsai workflow."""
    check_valve_delay: float = Field(description="Delay after the check valve is opened before the odor is delivered, in seconds.")
    end_valve0_delay: float = Field(description="Delay after the end valve is opened before the odor is stopped, in seconds.")
    isi_upper_bound: float = Field(description="Inter-stimulus interval upper bound, in seconds.")
    isi_lower_bound: float = Field(description="Inter-stimulus interval lower bound, in seconds.")
    time_before_odor: float = Field(description="Time before odor delivery, in seconds.")
    trial_csv_path: str = Field(description="Path to the CSV file containing the trial parameters.")

class Task(BaseModel):
    name: str = Field(description="Name of the task.")
    logging_path: str = Field(description="Path to the directory where data will be saved.")
    hardware: TaskHardware = Field(description="Hardware configuration for the task.")
    odor_loop: OdorLoop = Field(description="Parameters for the odor loop.")
    trials: list[Trial] = Field(description="List of trials to be executed.")

if __name__ == "__main__":
    schema = Task.model_json_schema()
    Path("task.json").write_text(json.dumps(schema, indent=2))

# Vacuum controller test

Double-click `open_vacuum_test.bat` to open the standalone demo in Bonsai.
It uses COM5 at 115200 baud and a 3500 ml/min setpoint by default. It does not
load experiment YAML; edit CreateSerialPort.PortName and StringProperty.Value
directly for this test. Use integer rates from 0 to 5000.

1. Stop the main experiment workflow and close Arduino Serial Monitor so COM5
   is available to this demo.
2. In Bonsai, check the port and rate, then click Start.
3. With Bonsai focused, press **V** once. If pressed within the first two seconds,
   the latest requested rate waits until that startup interval ends. Later presses
   send immediately. No setpoint is sent unless V is pressed.
4. With the updated firmware uploaded, double-click `VacuumStatus` while running
   to inspect the most recent reply: `READY`, `OK 3500`, `ERR COMMAND`, or a DAC error.
5. Change the value and press V to test another rate. Use the vacuum controller
   to stop flow when finished; stopping this workflow does not send zero.

`OK` confirms an acknowledged DAC write, not measured airflow. If OK appears but
the flow does not change, check the DAC output and downstream controller.
The old sketch can use the startup buffer, but sends no status replies.

For firmware updates, open `ardunio_code/flow_contorl.ino` from the project root
in Arduino IDE, select Arduino Uno and its port, and upload after closing Bonsai.
If the IDE asks to place the sketch inside a matching `flow_contorl` folder,
allow it to do so. The sketch still sets 3000 ml/min after power-up/reset.

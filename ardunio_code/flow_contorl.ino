#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac;

// ============================================================
// Hardware / calibration
// ============================================================
constexpr uint8_t MCP4725_ADDR = 0x62;

// Measured maximum DAC output: ~4.90 V
constexpr uint16_t DAC_MAX_MV = 5000;

// GFC-17 command range: 0–5 V = 0–5000 mL/min
constexpr uint16_t MAX_FLOW_ML_MIN = 5000;

// Default flow after power-up / reset
constexpr uint16_t DEFAULT_FLOW_ML_MIN = 3000;

// Serial
constexpr uint32_t SERIAL_BAUD = 115200;

// 0xFFFF means "no flow has been written yet"
uint16_t currentFlow = 0xFFFF;

// ============================================================
// Fast integer flow -> DAC conversion
//
// For this GFC:
// 1000 mL/min = 1.000 V = 1000 mV
//
// MCP4725 measured full-scale:
// DAC code 4095 = 4900 mV
//
// Therefore:
// DAC = flow_mL_min * 4095 / 4900
// ============================================================
constexpr float DAC_MAX_VOLTAGE = 5.0000;

bool setFlow(uint16_t flow_mL_min)
{
  if (flow_mL_min > MAX_FLOW_ML_MIN) {
    return false;
  }

  // GFC-17:
  // 1000 mL/min requires exactly 1.000 V
  float targetVoltage = flow_mL_min / 1000.0;

  uint16_t dacCode;

  if (targetVoltage >= DAC_MAX_VOLTAGE) {
    dacCode = 4095;
  }
  else {
    dacCode = (uint16_t)(
      targetVoltage / DAC_MAX_VOLTAGE * 4095.0 + 0.5
    );
  }

  // Reapply even an unchanged setpoint: the DAC may have reset independently.
  // Only record success when the I2C write was acknowledged.
  if (!dac.setVoltage(dacCode, false)) {
    return false;
  }

  currentFlow = flow_mL_min;
  return true;
}

// ============================================================
// Ultra-lightweight serial parser
//
// Accepted Bonsai commands:
//   1200\n
//   1600\r
//   3000\r\n
//
// No String, no strtod/strtof, no timeout/blocking.
//
// Replies: OK <flow> after an acknowledged DAC write, ERR COMMAND for
// invalid input, or ERR DAC_WRITE for an I2C write failure.
// ============================================================
uint16_t rxValue = 0;
bool rxHasDigit = false;
bool rxInvalid = false;

uint16_t pendingFlow = 0;
bool pendingReady = false;

inline void resetParser()
{
  rxValue = 0;
  rxHasDigit = false;
  rxInvalid = false;
}

inline void finishCommand()
{
  if (rxHasDigit && !rxInvalid && rxValue <= MAX_FLOW_ML_MIN) {
    // Keep only the newest complete command in the current serial burst.
    pendingFlow = rxValue;
    pendingReady = true;
  }
  else if (rxHasDigit || rxInvalid) {
    Serial.println("ERR COMMAND");
  }

  resetParser();
}

void readSerialFast()
{
  while (Serial.available() > 0)
  {
    const char c = (char)Serial.read();

    if (c >= '0' && c <= '9')
    {
      if (!rxInvalid)
      {
        const uint16_t digit = (uint16_t)(c - '0');

        // Prevent overflow and reject values >5000 immediately.
        if (rxValue > 500 ||
            (rxValue == 500 && digit > 0))
        {
          rxInvalid = true;
        }
        else
        {
          rxValue = (uint16_t)(rxValue * 10U + digit);
          rxHasDigit = true;
        }
      }
    }
    else if (c == '\r' || c == '\n')
    {
      // Supports CR, LF, or CRLF.
      finishCommand();
    }
    else if (c == ' ' || c == '\t')
    {
      // Ignore whitespace.
    }
    else
    {
      // Any other character invalidates this line.
      rxInvalid = true;
    }
  }

  // If many commands arrived at once, execute only the newest one.
  if (pendingReady)
  {
    const uint16_t flow = pendingFlow;
    pendingReady = false;
    if (setFlow(flow)) {
      Serial.print("OK ");
      Serial.println(flow);
    }
    else {
      Serial.println("ERR DAC_WRITE");
    }
  }
}

// ============================================================
// Startup
// ============================================================
void setup()
{
  Serial.begin(SERIAL_BAUD);

  Wire.begin();

  // Adafruit MCP4725 setVoltage() uses fast I2C writes internally.
  // Wait until the DAC answers before setting the startup flow.
  while (true)
  {
    Wire.beginTransmission(MCP4725_ADDR);
    if (Wire.endTransmission() == 0) {
      break;
    }
    delay(5);
  }

  if (!dac.begin(MCP4725_ADDR)) {
    Serial.println("ERR DAC_INIT");
    // Do not enter loop() with an uninitialized DAC object.
    while (true) { delay(1000); }
  }

  // Default after power-up / USB reset
  if (!setFlow(DEFAULT_FLOW_ML_MIN)) {
    Serial.println("ERR DAC_WRITE");
  }
  Serial.println("READY");
}

// ============================================================
// Main loop
// ============================================================
void loop()
{
  readSerialFast();
}

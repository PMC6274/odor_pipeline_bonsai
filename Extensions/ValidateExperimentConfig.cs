using System;
using System.Reactive.Linq;
using System.Text.RegularExpressions;
using Bonsai;

namespace OdorExperiment
{
    [Combinator]
    [System.ComponentModel.Description("Validates experiment metadata and parameters before the workflow starts.")]
    public class ValidateExperimentConfig
    {
        static readonly Regex ComPortPattern = new Regex("^COM[0-9]+$", RegexOptions.IgnoreCase);

        public IObservable<ExperimentConfig> Process(IObservable<ExperimentConfig> source)
        {
            return source.Select(config =>
            {
                Validate(config);
                return config;
            });
        }

        static void Validate(ExperimentConfig config)
        {
            if (config == null) throw new ArgumentException("Experiment configuration is missing.");
            if (config.Metadata == null) throw new ArgumentException("Metadata section is missing.");
            if (config.Hardware == null) throw new ArgumentException("Hardware section is missing.");
            if (config.Protocol == null) throw new ArgumentException("Protocol section is missing.");
            if (config.Controls == null) throw new ArgumentException("Controls section is missing.");
            if (config.Output == null) throw new ArgumentException("Output section is missing.");

            RequireText(config.Metadata.ExperimentId, "Metadata.ExperimentId");
            RequireText(config.Metadata.SubjectId, "Metadata.SubjectId");
            RequireText(config.Metadata.Operator, "Metadata.Operator");

            RequireComPort(config.Hardware.Olfactometer1Port, "Hardware.Olfactometer1Port");
            RequireComPort(config.Hardware.Olfactometer2Port, "Hardware.Olfactometer2Port");
            RequireComPort(config.Hardware.Olfactometer3Port, "Hardware.Olfactometer3Port");
            RequireComPort(config.Hardware.WhiteRabbitPort, "Hardware.WhiteRabbitPort");

            RequireText(config.Controls.StartFlow, "Controls.StartFlow");
            RequireText(config.Controls.DisableFlow, "Controls.DisableFlow");
            RequireText(config.Controls.StartPps, "Controls.StartPps");
            RequireText(config.Controls.EndPps, "Controls.EndPps");
            RequireText(config.Controls.StartExperiment, "Controls.StartExperiment");

            RequireText(config.Protocol.StimulusFile, "Protocol.StimulusFile");
            if (config.Protocol.TrialCount < 1)
                throw new ArgumentException("Protocol.TrialCount must be at least 1.");
            RequireNonNegative(config.Protocol.ChargeSeconds, "Protocol.ChargeSeconds");
            RequireNonNegative(config.Protocol.DeliverySeconds, "Protocol.DeliverySeconds");
            RequireNonNegative(config.Protocol.FlushSeconds, "Protocol.FlushSeconds");
            RequireNonNegative(config.Protocol.RechargeSeconds, "Protocol.RechargeSeconds");
            RequireNonNegative(config.Protocol.FlowAdjustmentSeconds, "Protocol.FlowAdjustmentSeconds");
            RequireNonNegative(config.Protocol.TimeBeforeOdorSeconds, "Protocol.TimeBeforeOdorSeconds");
            RequireNonNegative(config.Protocol.IsiMinimumSeconds, "Protocol.IsiMinimumSeconds");
            RequireNonNegative(config.Protocol.IsiMaximumSeconds, "Protocol.IsiMaximumSeconds");
            if (config.Protocol.IsiMaximumSeconds < config.Protocol.IsiMinimumSeconds)
                throw new ArgumentException("Protocol.IsiMaximumSeconds must be greater than or equal to IsiMinimumSeconds.");

            RequireFlow(config.Protocol.MainFlow, "Protocol.MainFlow");
            RequireFlow(config.Protocol.ControlFlow, "Protocol.ControlFlow");
            RequireFlow(config.Protocol.FlushFlow, "Protocol.FlushFlow");
            RequireText(config.Output.DataDirectory, "Output.DataDirectory");
        }

        static void RequireText(string value, string name)
        {
            if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException(name + " is required.");
        }

        static void RequireComPort(string value, string name)
        {
            if (string.IsNullOrWhiteSpace(value) || !ComPortPattern.IsMatch(value))
                throw new ArgumentException(name + " must look like COM4 or COM24.");
        }

        static void RequireNonNegative(double value, string name)
        {
            if (double.IsNaN(value) || double.IsInfinity(value) || value < 0)
                throw new ArgumentException(name + " must be a finite, non-negative number.");
        }

        static void RequireFlow(int value, string name)
        {
            if (value < 0 || value > 1000) throw new ArgumentException(name + " must be between 0 and 1000.");
        }
    }
}

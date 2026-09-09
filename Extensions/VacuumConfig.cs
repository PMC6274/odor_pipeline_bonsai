// Supplement the schema-generated partial classes until Bonsai.Sgen is rerun.
// Remove this file when regenerating OdorExperiment.Generated.cs from the schema.
namespace OdorExperiment
{
    public partial class HardwareConfig
    {
        [YamlDotNet.Serialization.YamlMember(Alias = "VacuumPort")]
        public string VacuumPort { get; set; }
    }

    public partial class ProtocolConfig
    {
        [YamlDotNet.Serialization.YamlMember(Alias = "VacuumRateMlPerMinute")]
        public double? VacuumRateMlPerMinute { get; set; }
    }
}

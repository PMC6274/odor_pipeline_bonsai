# Offline check: exercise the installed Bonsai operator without opening serial ports.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$packages = Join-Path $root '.bonsai/Packages'
$references = @(
    "$packages/Rx-Interfaces.2.2.5/lib/net45/System.Reactive.Interfaces.dll",
    "$packages/Rx-Core.2.2.5/lib/net45/System.Reactive.Core.dll",
    "$packages/Rx-Linq.2.2.5/lib/net45/System.Reactive.Linq.dll",
    "$packages/Bonsai.Core.2.9.0/lib/net472/Bonsai.Core.dll"
)
foreach ($reference in $references) { [Reflection.Assembly]::LoadFrom($reference) | Out-Null }
Add-Type -ReferencedAssemblies $references -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Reactive.Subjects;

public static class VacuumStartupTest
{
    public static void Run()
    {
        using (var commands = new Subject<string>())
        using (var startup = new Subject<long>())
        {
            var sent = new List<string>();
            using (new Bonsai.Reactive.CombineLatest().Process(commands, startup)
                .Subscribe(value => sent.Add(value.Item1)))
            {
                commands.OnNext("3000");
                commands.OnNext("3500");
                if (sent.Count != 0) throw new Exception("Sent during startup.");
                startup.OnNext(0);
                startup.OnCompleted();
                if (sent.Count != 1 || sent[0] != "3500")
                    throw new Exception("Latest startup command was not released once.");
                commands.OnNext("4000");
                if (sent.Count != 2 || sent[1] != "4000")
                    throw new Exception("Later command was not sent immediately.");
            }
        }
        using (var commands = new Subject<string>())
        using (var startup = new Subject<long>())
        {
            int sent = 0;
            using (new Bonsai.Reactive.CombineLatest().Process(commands, startup)
                .Subscribe(value => sent++))
            {
                startup.OnNext(0);
                startup.OnCompleted();
                if (sent != 0) throw new Exception("Startup sent an unrequested command.");
                commands.OnNext("4500");
                if (sent != 1) throw new Exception("First post-startup command was lost.");
            }
        }
    }
}
'@
[VacuumStartupTest]::Run()
Write-Output 'PASS: startup buffers the latest command; later presses send immediately; no automatic flow command.'

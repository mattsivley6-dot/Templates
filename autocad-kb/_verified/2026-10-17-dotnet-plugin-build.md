# Building AutoCAD 2027 / MEP .NET plug-ins without the .NET SDK (2026-10-17)

## Facts (VERIFIED on the test PC)
- AutoCAD 2027 (release 26.0) plug-ins must target .NET 10.0 (ObjectARX migration guide, G:A6C680F2, G:4DA730AB). The .NET 10.0.13 runtime was installed; there was NO .NET SDK.
- PowerShell 7.6.7 runs on .NET 10.0.13 and ships the C# compiler (Microsoft.CodeAnalysis.CSharp 5.0) plus reference assemblies (`$PSHOME\ref`). Its `Add-Type -OutputAssembly <dll> -OutputType Library -ReferencedAssemblies ...` builds a .NET 10 class library.
- Built this way (no SDK): `ClaudeProbe.dll` referencing `accoremgd 26.0`, `acdbmgd 26.0`, `AecbPipeBaseMgd 8.9.64.0` and `System.Runtime 10.0`, with a `[CommandMethod("CLAUDEPROBE")]` that counts `Autodesk.Aec.Building.Piping.DatabaseServices.Pipe` objects. The MEP managed namespace resolved at compile time.
- Managed assemblies to reference: `C:\Program Files\Autodesk\AutoCAD 2027\accoremgd.dll`, `acdbmgd.dll`, `acmgd.dll`; MEP/AEC: `...\ACA\AecBaseMgd.dll`, `AecbBldSrvMgd.dll`, `AecbPipeBaseMgd.dll`, `AecbHvacBaseMgd.dll`, `AecbPlumbingBaseMgd.dll`, `AecbElecBaseMgd.dll`, `...\MEP\AecbPartBaseMgd.dll`, `AecbRuntimeCatalogMgd.dll`. Their API reference: the AutoCAD MEP managed API help (CHM).

## Loading is the blocker (VERIFIED)
- In the test: `SECURELOAD` = 1, `TRUSTEDPATHS` = empty, `LEGACYCODESEARCH` = 0.
- Core Console test: `_.FILEDIA 0`, `_.NETLOAD <temp folder>\ClaudeCore.dll` printed `Unable to load ...ClaudeCore.dll assembly.` and the command stayed unknown. (Inference: the untrusted folder is the cause; the console cannot show the security prompt, so it refuses. Not yet confirmed from a trusted folder.)
- Trusted by default: the AutoCAD install folders and `C:\Program Files\Autodesk\ApplicationPlugins` (bundles there load with no signature check), both need admin rights to write. `%APPDATA%\Autodesk\ApplicationPlugins` exists but is not trusted unless added.
- Options for the user to choose (a security setting, so the user makes the change): add one folder to Trusted Locations (Options > Files > Trusted Locations, or TRUSTEDPATHS), or install a signed bundle under Program Files\Autodesk\ApplicationPlugins. Never change SECURELOAD.
- MEP classes (pipes, parts) exist only when the MEP profile is loaded in full acad.exe; the Core Console does not load MEP (2026-10-16 test), so an MEP plug-in runs in the GUI session driven over COM (SendCommand "CLAUDEPROBE ").

## Build recipe (copy)
```powershell
$A = 'C:\Program Files\Autodesk\AutoCAD 2027'
Add-Type -TypeDefinition $src -OutputType Library -OutputAssembly C:\path\MyTool.dll `
  -ReferencedAssemblies @("$A\accoremgd.dll","$A\acdbmgd.dll","$A\acmgd.dll","$A\ACA\AecBaseMgd.dll","$A\ACA\AecbPipeBaseMgd.dll")
```
Sources of both probes: `scripts/ClaudeProbe.cs.txt`, `scripts/ClaudeCore.cs.txt`.

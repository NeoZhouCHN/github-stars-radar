#define AppName "GitHub Stars Radar"
#ifndef AppVersion
#define AppVersion "0.1.0"
#endif
#ifndef SourceDir
#define SourceDir "..\..\dist\windows-package\GitHubStarsRadar"
#endif
#ifndef OutputDir
#define OutputDir "..\..\dist"
#endif

[Setup]
AppId={{8F7867F4-4C7D-45D7-90B1-C2AE1DFD61A5}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=NeoZhouCHN
AppPublisherURL=https://github.com/NeoZhouCHN/github-stars-radar
AppSupportURL=https://github.com/NeoZhouCHN/github-stars-radar/issues
AppUpdatesURL=https://github.com/NeoZhouCHN/github-stars-radar/releases
DefaultDirName={localappdata}\GitHubStarsRadar
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=GitHubStarsRadarSetup-{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile={#SourceDir}\LICENSE
UninstallDisplayIcon={app}\github-stars-radar.exe

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\GitHub Stars Radar README"; Filename: "{app}\README.md"
Name: "{group}\GitHub Stars Radar Config"; Filename: "{app}\GitHubStarsRadarConfig.exe"
Name: "{group}\Uninstall GitHub Stars Radar"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\GitHubStarsRadarConfig.exe"; Description: "Open configuration helper"; Flags: postinstall nowait skipifsilent

; Inno Setup Installer Script voor Sint Maarten Campus Autologin Tool
; Vereist: Inno Setup 6 of hoger

[Setup]
AppName=Sint Maarten Campus Autologin Tool
AppVersion=1.0.7
AppPublisher=Sint Maarten Campus
AppPublisherURL=
DefaultDirName={pf}\SintMaartenCampusAutologin
DefaultGroupName=Sint Maarten Campus Autologin
OutputDir=installer_output
OutputBaseFilename=SintMaartenCampusAutologin_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\SintMaartenCampusAutologin.exe
SetupIconFile=
WizardImageFile=
WizardSmallImageFile=

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"

[Tasks]
Name: "desktopicon"; Description: "Snelkoppeling op bureaublad maken"; GroupDescription: "Aanvullende opties:"
Name: "startmenu"; Description: "Snelkoppeling in Start Menu maken"; GroupDescription: "Aanvullende opties:"; Flags: unchecked

[Files]
Source: "dist\SintMaartenCampusAutologin.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_autologin.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Sint Maarten Campus Autologin"; Filename: "{app}\start_autologin.bat"; WorkingDir: "{app}"; Comment: "Start Sint Maarten Campus Autologin Tool"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Sint Maarten Campus Autologin"; Filename: "{app}\start_autologin.bat"; WorkingDir: "{app}"; Tasks: desktopicon; Comment: "Start Sint Maarten Campus Autologin Tool"
Name: "{userappdata}\Microsoft\Windows\Start Menu\Programs\Sint Maarten Campus Autologin"; Filename: "{app}\start_autologin.bat"; WorkingDir: "{app}"; Tasks: startmenu; Comment: "Start Sint Maarten Campus Autologin Tool"

[Run]
Filename: "{app}\start_autologin.bat"; Description: "Start Sint Maarten Campus Autologin Tool nu"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure InitializeWizard;
begin
  WizardForm.LicenseLabel1.Caption := 'Sint Maarten Campus Autologin Tool' + #13#10 + 
    'Versie 1.0.7' + #13#10 + #13#10 +
    'Deze tool helpt bij automatische logins voor:' + #13#10 +
    '- Smartschool' + #13#10 +
    '- Microsoft Admin' + #13#10 +
    '- Google Admin' + #13#10 +
    '- Easy4U' + #13#10 + #13#10 +
    'Ook ondersteuning voor RDP en SSH verbindingen.';
end;

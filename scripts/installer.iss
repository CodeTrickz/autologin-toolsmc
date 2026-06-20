; Inno Setup Installer Script voor Sint Maarten Campus Autologin Tool
; Vereist: Inno Setup 6 of hoger

[Setup]
AppId={{7F6A6A2D-8A35-4DA8-B6F1-0A174011CAFE}
AppName=Sint Maarten Campus Autologin Tool
AppVersion=2.0.5-beta.4
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
CloseApplications=yes
CloseApplicationsFilter=SintMaartenCampusAutologin.exe
RestartApplications=no
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
var
  RemoveLocalDataOnUninstall: Boolean;

function IsExistingInstallation: Boolean;
begin
  Result := DirExists(ExpandConstant('{app}'));
end;

procedure StopRunningApplication;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{cmd}'), '/C taskkill /F /T /IM SintMaartenCampusAutologin.exe >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{cmd}'), '/C taskkill /F /T /IM chromedriver.exe >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(
    'powershell.exe',
    '-NoProfile -ExecutionPolicy Bypass -Command "$tokens=@(''' + ExpandConstant('{app}') + ''',''' + ExpandConstant('{localappdata}\SintMaartenCampusAutologin') + ''') | ForEach-Object { $_.ToLowerInvariant() }; Get-CimInstance Win32_Process | Where-Object { $_.Name -in @(''chrome.exe'',''msedgewebview2.exe'',''chromedriver.exe'') -and ($cmd=([string]$_.CommandLine).ToLowerInvariant()) -and ($tokens | Where-Object { $_ -and $cmd.Contains($_) }) } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"',
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  );
  Sleep(3000);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  if IsExistingInstallation then
    Log('Bestaande installatie gevonden. Applicatie wordt gestopt voor update.')
  else
    Log('Geen bestaande installatie gevonden. Nieuwe installatie wordt uitgevoerd.');

  StopRunningApplication;
  Result := '';
end;

function InitializeUninstall: Boolean;
begin
  RemoveLocalDataOnUninstall :=
    MsgBox(
      'Remove local credentials and configuration?' + #13#10 + #13#10 +
      'Default: NO' + #13#10 + #13#10 +
      'Kies Nee om encrypted credentials, configuratie en gebruikersvoorkeuren te bewaren.',
      mbConfirmation,
      MB_YESNO or MB_DEFBUTTON2
    ) = IDYES;
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    StopRunningApplication;

  if (CurUninstallStep = usPostUninstall) and RemoveLocalDataOnUninstall then
  begin
    DelTree(ExpandConstant('{localappdata}\SintMaartenCampusAutologin'), True, True, True);
  end;
end;

procedure InitializeWizard;
begin
  WizardForm.LicenseLabel1.Caption := 'Sint Maarten Campus Autologin Tool' + #13#10 + 
    'Versie 2.0.5-beta.4' + #13#10 + #13#10 +
    'Deze tool helpt bij automatische logins voor:' + #13#10 +
    '- Smartschool' + #13#10 +
    '- Microsoft Admin' + #13#10 +
    '- Google Admin' + #13#10 +
    '- Easy4U' + #13#10 + #13#10 +
    'Ook ondersteuning voor RDP en SSH verbindingen.';
end;

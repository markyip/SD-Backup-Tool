; SD Card Backup Tool Installer Script
; Created using Inno Setup

[Setup]
AppName=Photo Video Backup Tool
AppVersion=1.0.0
AppPublisher=SD Backup Tool Development Team
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={autopf}\Photo Video Backup Tool
DefaultGroupName=Photo Video Backup Tool
AllowNoIcons=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=Photo_Video_Backup_Tool_Installer_v1.0.0
SetupIconFile=..\assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LanguageDetectionMethod=locale
ShowLanguageDialog=auto

[Languages]
Name: "chinese_traditional"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"
Name: "chinese_simplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "..\dist\Photo Video Backup Tool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "Instructions.txt"

[Icons]
Name: "{group}\Photo Video Backup Tool"; Filename: "{app}\Photo Video Backup Tool.exe"
Name: "{group}\{cm:UninstallProgram,Photo Video Backup Tool}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Photo Video Backup Tool"; Filename: "{app}\Photo Video Backup Tool.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Photo Video Backup Tool"; Filename: "{app}\Photo Video Backup Tool.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\Photo Video Backup Tool.exe"; Description: "{cm:LaunchProgram,Photo Video Backup Tool}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\SDBackupTool"

[Messages]
chinese_traditional.WelcomeLabel1=Welcome to the [name] Setup Wizard
chinese_traditional.WelcomeLabel2=This wizard will guide you through the installation of [name/ver].%n%nIt is recommended that you close all other applications before continuing.
chinese_traditional.ClickNext=Click [Next] to continue, or [Cancel] to exit Setup.
chinese_traditional.SelectDirLabel3=Setup will install [name] into the following folder.
chinese_traditional.SelectDirBrowseLabel=To continue, click Next. If you would like to select a different folder, click Browse.
chinese_traditional.DiskSpaceGBLabel=At least [gb] GB of free disk space is required.
chinese_traditional.ToUNCPathname=Setup cannot install to a UNC path name. If you want to install to a network drive, you need to map a network drive letter.
chinese_traditional.InvalidPath=You must enter a full path with drive letter; for example:%n%nC:\APP%n%nor a UNC path in the form:%n%n\\server\share
chinese_traditional.InvalidDrive=The drive or UNC share you selected does not exist or is not accessible. Please select another.
chinese_traditional.DiskSpaceWarning=Setup requires at least %1 KB of free space to install, but the selected drive only has %2 KB available.%n%nDo you want to continue anyway?
chinese_traditional.DirNameTooLong=The folder name or path is too long.
chinese_traditional.InvalidDirName=The folder name is not valid.
chinese_traditional.BadDirName32=Folder names cannot contain any of the following characters:%n%n%1
chinese_traditional.DirExistsTitle=Folder Exists
chinese_traditional.DirExists=The folder:%n%n%1%n%nalready exists. Would you like to install to that folder anyway?
chinese_traditional.DirDoesntExistTitle=Folder Does Not Exist
chinese_traditional.DirDoesntExist=The folder:%n%n%1%n%ndoes not exist. Would you like the folder to be created?

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;
Unicode true
!include "LogicLib.nsh"
!include "MUI2.nsh"
!include "x64.nsh"

!define APP_NAME "Pong '76"
!ifndef APP_VERSION
!define APP_VERSION "0.1.0"
!endif
!define APP_EXE "target/x86_64-pc-windows-gnu/release/pong76.exe"

Name "${APP_NAME}"
OutFile "dist/Pong-76-Setup.exe"
InstallDir "$PROGRAMFILES64\Pong '76"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "InstallLocation"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function .onInit
    ${IfNot} ${RunningX64}
        MessageBox MB_ICONSTOP "Pong '76 requires 64-bit Windows."
        Abort
    ${EndIf}
FunctionEnd

Section "Pong '76" MainSection
    SetRegView 64
    SetShellVarContext all
    SetOutPath "$INSTDIR"
    File /oname=pong76.exe "${APP_EXE}"
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    CreateDirectory "$SMPROGRAMS\Pong '76"
    CreateShortcut "$SMPROGRAMS\Pong '76\Pong '76.lnk" "$INSTDIR\pong76.exe"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "DisplayIcon" "$INSTDIR\pong76.exe"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76" "NoRepair" 1
SectionEnd

Section "Uninstall"
    SetRegView 64
    SetShellVarContext all
    Delete "$SMPROGRAMS\Pong '76\Pong '76.lnk"
    RMDir "$SMPROGRAMS\Pong '76"
    Delete "$INSTDIR\pong76.exe"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pong76"
SectionEnd

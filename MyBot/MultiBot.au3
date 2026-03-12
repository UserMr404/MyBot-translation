#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Icon=images\MyBot.ico
#AutoIt3Wrapper_Outfile=MultiBot
#AutoIt3Wrapper_Compression=4
#AutoIt3Wrapper_UseUpx=y
#AutoIt3Wrapper_Res_Description=MultiBot for MyBot.run
#AutoIt3Wrapper_Res_Fileversion=1.0.0.0
#AutoIt3Wrapper_Run_Tidy=y
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****

#include "MyBot.run.version.au3"
#include <FileConstants.au3>
#include <MsgBoxConstants.au3>
#include <AutoItConstants.au3>
#include <ListBoxConstants.au3>
#include <GUIConstantsEx.au3>
#include <ButtonConstants.au3>
#include <GuiButton.au3>
#include <TrayConstants.au3>
#include <GUIConstantsEx.au3>
#include <GUIListBox.au3>
#include <Misc.au3>
#include <StaticConstants.au3>
#include <WindowsConstants.au3>
#include <ComboConstants.au3>
#include <WinAPIFiles.au3>
#include <Array.au3>
#include <ProcessConstants.au3>
#include <WinAPIProc.au3>
#include <WinAPISys.au3>
#include <GuiMenu.au3>
#include <InetConstants.au3>
#include <Misc.au3>
#include <WinAPI.au3>
#include <EditConstants.au3>
#include <ColorConstants.au3>
#include <ListViewConstants.au3>
#include <GuiListView.au3>
#include <GuiStatusBar.au3>
#include <ProgressConstants.au3>
#include <SendMessage.au3>

If _Singleton("MultiBot", 1) = 0 Then
    ; Find window even if hidden
    Local $hWnd = WinGetHandle("MultiBot")
    If @error Then
        ; Try by class if title doesn't work
        Local $aWinList = WinList("[CLASS:AutoIt v3 GUI]")
        For $i = 1 To $aWinList[0][0]
            If StringInStr(WinGetTitle($aWinList[$i][1]), "MultiBot") Or WinGetTitle($aWinList[$i][1]) = "" Then
                $hWnd = $aWinList[$i][1]
                ExitLoop
            EndIf
        Next
    EndIf
    
    If $hWnd <> 0 Then
        ; Restore window
        WinSetState($hWnd, "", @SW_SHOW)
        WinSetState($hWnd, "", @SW_RESTORE)
        WinActivate($hWnd)
    EndIf
    Exit
EndIf

Global $g_sBotFile = "MyBot.run.exe"
Global $g_sBotFileAU3 = "MyBot.run.au3"
Global $g_sVersion = "1.0"
Global $g_sDirProfiles = @ScriptDir & "\Profiles\MultiBot-Profiles.ini"
Global $g_bMinimizedToTray = False
Global $g_hGui_Main, $g_hGui_Profile, $g_hGui_Emulator, $g_hGui_Instance, $g_hGui_Dir, $g_hGui_Parameter, $g_hGUI_AutoStart, $g_hGUI_Edit, $g_hListview_Main, $g_hLst_AutoStart, $g_hBtn_StartAll, $g_hBtn_RestartAll, $g_hBtn_StopAll, $g_hBtn_StartEmu, $g_hBtn_RestartEmu, $g_hBtn_StopEmu, $g_hMenu, $g_hMenuItem_ProfileDir, $g_hMenuItem_StartupDir, $g_hContext_Main, $g_hTrayItem_Exit, $g_hTrayItem_MyBotDir, $g_hTrayItem_ProfileDir
Global $g_hListview_Instances
Global $g_aGuiPos_Main
Global $g_sTypedProfile, $g_sSelectedEmulator
Global $g_sIniProfile, $g_sIniEmulator, $g_sIniInstance, $g_sIniDir, $g_sIniParameters
Global $g_iParameters = 7
Global Enum $eEdit = 1000, $eDelete, $eStartVM, $eStopVM, $eRestartVM, $eStartBot, $eStopBot, $eRestartBot

If @OSArch = "X86" Then
	$Wow6432Node = ""
	$HKLM = "HKLM"
Else
	$Wow6432Node = "\Wow6432Node"
	$HKLM = "HKLM64"
EndIf

Opt("TrayMenuMode", 1)
Opt("TrayOnEventMode", 1)
TraySetState(2)
TraySetClick(16)

GUI_Main()

Func GUI_Main()

	$g_hGui_Main = GUICreate("MultiBot", 280, 370, -1, -1, -1, 0x00040000)
	GUISetIcon(@ScriptDir & "\images\MyBot.ico", -1, $g_hGui_Main)
	$g_hMenu = GUICtrlCreateMenu("Menu")
	$g_hMenuItem_StartupDir = GUICtrlCreateMenuItem("MyBot Directory", $g_hMenu)
	$g_hMenuItem_ProfileDir = GUICtrlCreateMenuItem("Profile Directory", $g_hMenu)
	$g_hListview_Main = GUICtrlCreateListView("", 8, 4, 264, 250, BitOR($LVS_REPORT, $LVS_SHOWSELALWAYS), -1)
	_GUICtrlListView_InsertColumn($g_hListview_Main, 1, "Setup", 264)
	$g_hBtn_Setup = GUICtrlCreateButton("New Setup", 8, 260, 264, 25, $WS_GROUP)
	GUICtrlSetTip(-1, "Use this Button to create a new Setup with your Profile, wished Emulator and Instance aswell as the Bot you want to use")
	$g_hBtn_StartAll = GUICtrlCreateButton("Start All Bots", 8, 290, 128, 25, $WS_GROUP)
	GUICtrlSetTip(-1, "Launch all configured bot profiles with a 1-second delay between each start")
	$g_hBtn_StopAll = GUICtrlCreateButton("Stop All Bots", 144, 290, 128, 25, $WS_GROUP)
	GUICtrlSetTip(-1, "Force-terminate all running MyBot.run.exe processes")
	$g_hBtn_StartEmu = GUICtrlCreateButton("Start All VMs", 8, 318, 128, 25, $WS_GROUP)
	GUICtrlSetTip(-1, "Start all configured BlueStacks5 instances")
	$g_hBtn_StopEmu = GUICtrlCreateButton("Stop All VMs", 144, 318, 128, 25, $WS_GROUP)
	GUICtrlSetTip(-1, "Stop all running BlueStacks5 instances")

	$g_hContext_Main = _GUICtrlMenu_CreatePopup()
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 0, "Start VM", $eStartVM)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 1, "Stop VM", $eStopVM)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 2, "Restart VM", $eRestartVM)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 3, "") ; Separator
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 4, "Start Bot", $eStartBot)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 5, "Stop Bot", $eStopBot)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 6, "Restart Bot", $eRestartBot)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 7, "") ; Separator
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 8, "Edit", $eEdit)
	_GUICtrlMenu_InsertMenuItem($g_hContext_Main, 9, "Delete", $eDelete)

	GUISetState(@SW_SHOW)

	TraySetIcon(@ScriptDir & "\images\MyBot.ico")
	TraySetOnEvent($TRAY_EVENT_PRIMARYDOWN, "TrayShow")
	$g_hTrayItem_MyBotDir = TrayCreateItem("MyBot Directory")
	TrayItemSetOnEvent($g_hTrayItem_MyBotDir, "TrayOpenMyBotDir")
	TrayItemSetState($g_hTrayItem_MyBotDir, 4) ; Disable checkbox
	$g_hTrayItem_ProfileDir = TrayCreateItem("Profile Directory")
	TrayItemSetOnEvent($g_hTrayItem_ProfileDir, "TrayOpenProfileDir")
	TrayItemSetState($g_hTrayItem_ProfileDir, 4) ; Disable checkbox
	TrayCreateItem("") ; Separator
	$g_hTrayItem_Exit = TrayCreateItem("Exit")
	TrayItemSetOnEvent($g_hTrayItem_Exit, "TrayExit")
	TrayItemSetState($g_hTrayItem_Exit, 4) ; Disable checkbox
	Sleep(100)
	TraySetToolTip("MultiBot")
	TraySetState(1)

	GUIRegisterMsg($WM_CONTEXTMENU, "WM_CONTEXTMENU")
	GUIRegisterMsg($WM_NOTIFY, "WM_NOTIFY")
	GUIRegisterMsg($WM_SIZE, "WM_SIZE")
	GUIRegisterMsg($WM_SYSCOMMAND, "WM_SYSCOMMAND")


	UpdateList_Main()

	If IniRead($g_sDirProfiles, "Options", "DisplayVersSent", "") = "" Then IniWrite($g_sDirProfiles, "Options", "DisplayVersSent", "1.0")

	While 1

		$aMsg = GUIGetMsg(1)
		Switch $aMsg[1]

			Case $g_hGui_Main
				Switch $aMsg[0]
					Case $GUI_EVENT_CLOSE
						$g_bMinimizedToTray = True
						GUISetState(@SW_HIDE, $g_hGui_Main)

					Case $g_hMenuItem_ProfileDir
						ShellExecute(@ScriptDir & "\Profiles\")

					Case $g_hMenuItem_StartupDir
						ShellExecute(@ScriptDir)

					Case $g_hBtn_Setup
						Local $bSetupStopped = False

						WinSetOnTop($g_hGui_Main, "", $WINDOWS_ONTOP)

						Do
							GUISetState(@SW_DISABLE, $g_hGui_Main)
							$g_aGuiPos_Main = WinGetPos($g_hGui_Main)
							$bSetupStopped = GUI_Profile()
							If $bSetupStopped Then ExitLoop
							$bSetupStopped = GUI_Emulator()
							If $bSetupStopped Then ExitLoop
							$bSetupStopped = GUI_Instance()
							If $bSetupStopped Then ExitLoop
							IniWrite($g_sDirProfiles, $g_sTypedProfile, "Dir", ".")
							$bSetupStopped = GUI_PARAMETER()
							If $bSetupStopped Then ExitLoop
						Until 1

						WinSetOnTop($g_hGui_Main, "", $WINDOWS_NOONTOP)
						If $bSetupStopped Then
						$bSetupStopped = False
						EndIf

						GUISetState(@SW_ENABLE, $g_hGui_Main)
						UpdateList_Main()

					Case $g_hBtn_StartAll
						StartAll()

					Case $g_hBtn_StopAll
						StopAll()

					Case $g_hBtn_StartEmu
						StartEmu()

					Case $g_hBtn_StopEmu
						StopEmu()

		EndSwitch

	EndSwitch

	WEnd
EndFunc   ;==>GUI_Main

Func GUI_Profile()
	$g_hGui_Profile = GUICreate("Profile", 255, 167, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	$hIpt_Profile = GUICtrlCreateInput("", 24, 72, 201, 21)
	$hBtn_Next = GUICtrlCreateButton("Next Step", 72, 120, 97, 25, $WS_GROUP)
	GUICtrlSetState($hBtn_Next, $GUI_DISABLE)
	GUICtrlCreateLabel("Enter the full profile name to continue", 24, 8, 204, 57)
	GUISetState()
	GUICtrlSetState($hIpt_Profile, $GUI_FOCUS)

	Local $bBtnEnabled = False


	While 1
		Local $aMsg = GUIGetMsg(1)
		Switch $aMsg[0]
			Case $GUI_EVENT_CLOSE
				$g_sTypedProfile = GUICtrlRead($hIpt_Profile)
				IniDelete($g_sDirProfiles, $g_sTypedProfile)
				GUIDelete($g_hGui_Profile)
				Return -1
			Case $hBtn_Next
				$g_sTypedProfile = GUICtrlRead($hIpt_Profile)
				If $g_sTypedProfile = "" Then
					ContinueLoop
				Else
					Local $aSections = IniReadSectionNames($g_sDirProfiles)
					If IsArray($aSections) Then
						For $i = 1 To $aSections[0]
							If $aSections[$i] = $g_sTypedProfile Then
								MsgBox($MB_OK, "Error", "Profile already exists: " & $g_sTypedProfile, 0, $g_hGui_Profile)
								ContinueLoop 2
							EndIf
						Next
					EndIf
					IniWrite($g_sDirProfiles, $g_sTypedProfile, "Profile", $g_sTypedProfile)
					IniWrite($g_sDirProfiles, $g_sTypedProfile, "BotVers", "")
					GUIDelete($g_hGui_Profile)
					Return 0
				EndIf
		EndSwitch

		If $bBtnEnabled Then ContinueLoop
		If GUICtrlRead($hIpt_Profile) Then
			ContinueLoop
		Else
			GUICtrlSetState($hBtn_Next, $GUI_ENABLE)
			$bBtnEnabled = True
		EndIf
	WEnd
EndFunc   ;==>GUI_Profile



Func GUI_Emulator()
	$g_hGui_Emulator = GUICreate("Emulator", 258, 167, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	$hCmb_Emulator = GUICtrlCreateCombo("BlueStacks5", 24, 72, 201, 21, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	$hBtn_Next = GUICtrlCreateButton("Next Step", 72, 120, 97, 25, $WS_GROUP)
	GUICtrlCreateLabel("Select your emulator", 24, 8, 204, 57)
	GUISetState()
	GUICtrlSetState($hCmb_Emulator, $GUI_FOCUS)



	While 1
		Local $aMsg = GUIGetMsg(1)
		Switch $aMsg[0]
			Case $GUI_EVENT_CLOSE
				IniDelete($g_sDirProfiles, $g_sTypedProfile)
				GUIDelete($g_hGui_Emulator)
				Return -1
			Case $hBtn_Next
				$g_sSelectedEmulator = GUICtrlRead($hCmb_Emulator)
				IniWrite($g_sDirProfiles, $g_sTypedProfile, "Emulator", $g_sSelectedEmulator)
				GUIDelete($g_hGui_Emulator)
				Return 0

		EndSwitch
	WEnd
EndFunc   ;==>GUI_Emulator



Func GUI_Instance()
	Local $hLbl_Instance = 0

	$g_hGui_Instance = GUICreate("Instance", 258, 167, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	$hIpt_Instance = GUICtrlCreateInput("", 24, 72, 201, 21)
	$hBtn_Next = GUICtrlCreateButton("Next Step", 72, 120, 97, 25, $WS_GROUP)
	$hLbl_Instance = GUICtrlCreateLabel("Please type in the Instance Name you want to use", 24, 8, 204, 57)
	GUISetState(@SW_HIDE, $g_hGui_Instance)

	Switch $g_sSelectedEmulator
		Case "BlueStacks", "BlueStacks2"
			Return
		Case "BlueStacks5"
			GUISetState(@SW_SHOW, $g_hGui_Instance)
			GUICtrlSetData($hLbl_Instance, "Enter your BlueStacks instance name. Example: Pie64, Pie64_1, Pie64_2, etc")
			GUICtrlSetData($hIpt_Instance, "Pie64_")
			GUICtrlSetState($hIpt_Instance, $GUI_FOCUS)
	EndSwitch

	While 1
		Local $aMsg = GUIGetMsg(1)
		Switch $aMsg[0]
			Case $GUI_EVENT_CLOSE
				GUIDelete($g_hGui_Instance)
				IniDelete($g_sDirProfiles, $g_sTypedProfile)
				Return -1
			Case $hBtn_Next
				$Inst = GUICtrlRead($hIpt_Instance)
				$Instances = LaunchConsole(GetInstanceMgrPath($g_sSelectedEmulator), "list vms", 1000)
				$Instance = StringRegExp($Instances, "(?i)Pie64(?:[_][0-9]*)?", 3)
				_ArrayUnique($Instance, 0, 0, 0, 0)

				If $g_sSelectedEmulator = "BlueStacks5" And UBound($Instance) = 0 Then
					$Instance = StringSplit("pie64", "|", 2)
					_ArrayDelete($Instance, 0)
				EndIf

				IniWrite($g_sDirProfiles, $g_sTypedProfile, "Instance", $Inst)
				GUIDelete($g_hGui_Instance)
				Return 0

		EndSwitch

		If _IsPressed("0D") And WinActive($g_hGui_Instance) Then
			$Inst = GUICtrlRead($hIpt_Instance)
			$Instances = LaunchConsole(GetInstanceMgrPath($g_sSelectedEmulator), "list vms", 1000)
			$Instance = StringRegExp($Instances, "(?i)Pie64(?:[_][0-9]*)?", 3)
			_ArrayUnique($Instance, 0, 0, 0, 0)

			If $g_sSelectedEmulator = "BlueStacks5" And UBound($Instance) = 0 Then
				$Instance = StringSplit("pie64", "|", 2)
				_ArrayDelete($Instance, 0)
			EndIf

			IniWrite($g_sDirProfiles, $g_sTypedProfile, "Instance", $Inst)
			GUIDelete($g_hGui_Instance)
			Return 0
		EndIf
	WEnd
EndFunc   ;==>GUI_Instance

Func GUI_DIR()
	$g_hGui_Dir = GUICreate("Directory", 258, 167, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	$hBtn_Folder = GUICtrlCreateButton("Choose Folder", 24, 72, 201, 21)
	$hBtn_Finish = GUICtrlCreateButton("Next", 72, 120, 97, 25, $WS_GROUP)
	GUICtrlSetState(-1, $GUI_DISABLE)
	GUICtrlCreateLabel("Select the MyBot folder containing MyBot.run.exe or .au3", 24, 8, 204, 57)
	GUISetState()

	Local $sFileSelectFolder = @ScriptDir

	If FileExists($sFileSelectFolder & "\" & $g_sBotFile) = 0 And FileExists($sFileSelectFolder & "\" & $g_sBotFileAU3) = 0 Then
		MsgBox($MB_OK, "Error", "MyBot.run.exe or .au3 not found in directory", 0, $g_hGui_Dir)
		IniDelete($g_sDirProfiles, $g_sTypedProfile)
		GUIDelete($g_hGui_Dir)
		Return -1
	Else
		GUICtrlSetState($hBtn_Finish, $GUI_ENABLE)
		GUICtrlSetState($hBtn_Folder, $GUI_DISABLE)
	EndIf



	While 1

		Switch GUIGetMsg()
			Case $GUI_EVENT_CLOSE
				IniDelete($g_sDirProfiles, $g_sTypedProfile)
				GUIDelete($g_hGui_Dir)
				Return -1

			Case $hBtn_Folder
				WinSetOnTop($g_hGui_Main, "", $WINDOWS_NOONTOP)
				Local $sFileSelectFolder = @ScriptDir
				WinSetOnTop($g_hGui_Main, "", $WINDOWS_ONTOP)

				If FileExists($sFileSelectFolder & "\" & $g_sBotFile) = 0 And FileExists($sFileSelectFolder & "\" & $g_sBotFileAU3) = 0 Then
					MsgBox($MB_OK, "Error", "MyBot.run.exe or .au3 not found in selected folder", 0, $g_hGui_Dir)
					ContinueLoop
				Else
					GUICtrlSetState($hBtn_Finish, $GUI_ENABLE)
				EndIf

			Case $hBtn_Finish

				IniWrite($g_sDirProfiles, $g_sTypedProfile, "Dir", ".")
				GUIDelete($g_hGui_Dir)
				ExitLoop


		EndSwitch
	WEnd




EndFunc   ;==>GUI_DIR

Func GUI_PARAMETER()
	Local $iEndResult

	$g_hGui_Parameter = GUICreate("Special Parameters", 280, 190, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	GUICtrlCreateLabel("Select options to run the bot with special parameters. These are optional.", 8, 8, 264, 37)
	$hChk_DebugMode = GUICtrlCreateCheckbox("Debug Mode", 8, 50)
	GUICtrlSetTip(-1, "Enable debug mode for detailed logging and troubleshooting")
	$hChk_DpiAwareness = GUICtrlCreateCheckbox("DPI Awareness", 8, 70)
	GUICtrlSetTip(-1, "Enable DPI awareness to properly scale the interface on high-DPI displays")
	$hChk_HideAndroid = GUICtrlCreateCheckbox("Hide Android", 8, 90)
	GUICtrlSetTip(-1, "Hide the Android emulator window during bot operation")
	$hChk_MiniGUIMode = GUICtrlCreateCheckbox("Mini GUI Mode", 8, 110)
	GUICtrlSetTip(-1, "Launch the bot in a compact mini GUI mode")
	$hChk_NoWatchdog = GUICtrlCreateCheckbox("No Watchdog", 140, 50)
	GUICtrlSetTip(-1, "Disable the watchdog process that monitors bot stability")
	$hChk_StartBotDocked = GUICtrlCreateCheckbox("Start Docked", 140, 70)
	GUICtrlSetTip(-1, "Automatically dock the bot window to the Android emulator on launch")
	$hChk_StartBotDockedAndShrinked = GUICtrlCreateCheckbox("Start Docked && Shrunk", 140, 90)
	GUICtrlSetTip(-1, "Automatically dock and shrink the bot window to the Android emulator on launch")


	$hBtn_Finish = GUICtrlCreateButton("Finish", 92, 150, 97, 25, $WS_GROUP)
	GUISetState()



	While 1

		Switch GUIGetMsg()
			Case $GUI_EVENT_CLOSE
				IniDelete($g_sDirProfiles, $g_sTypedProfile)
				GUIDelete($g_hGui_Parameter)
				Return -1


			Case $hBtn_Finish
				$iEndResult = ""
				$iEndResult &= (GUICtrlRead($hChk_DebugMode) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_DpiAwareness) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_HideAndroid) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_MiniGUIMode) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_NoWatchdog) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_StartBotDocked) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_StartBotDockedAndShrinked) = $GUI_CHECKED ? 1 : 0)
				IniWrite($g_sDirProfiles, $g_sTypedProfile, "Parameters", $iEndResult)
				GUIDelete($g_hGui_Parameter)
				ExitLoop


		EndSwitch
	WEnd




EndFunc   ;==>GUI_PARAMETER



Func GUI_Edit()

	Local $iEndResult

	$aLstbx_GetSelTxt = _GUICtrlListView_GetSelectedIndices($g_hListview_Main, True)
	$sLstbx_SelItem = _GUICtrlListView_GetItemText($g_hListview_Main, $aLstbx_GetSelTxt[1])
	ReadIni($sLstbx_SelItem)
	$g_sIniProfile = StringReplace($g_sIniProfile, '"', '')
	$sSelectedFolder = $g_sIniDir
	$g_hGUI_Edit = GUICreate("Edit INI", 258, 230, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	$hIpt_Profile = GUICtrlCreateInput($g_sIniProfile, 112, 8, 137, 21)
	$hCmb_Emulator = GUICtrlCreateCombo($g_sIniEmulator, 112, 40, 137, 21, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	$hIpt_Instance = GUICtrlCreateInput($g_sIniInstance, 112, 72, 137, 21)
	GUICtrlCreateLabel("Profile Name:", 8, 8, 95, 17)
	GUICtrlCreateLabel("Emulator:", 8, 40, 95, 17)
	GUICtrlCreateLabel("Instance:", 8, 72, 95, 17)

	$hChk_DebugMode = GUICtrlCreateCheckbox("Debug Mode", 8, 100)
	GUICtrlSetTip(-1, "Enable debug mode for detailed logging and troubleshooting")
	$hChk_DpiAwareness = GUICtrlCreateCheckbox("DPI Awareness", 8, 120)
	GUICtrlSetTip(-1, "Enable DPI awareness to properly scale the interface on high-DPI displays")
	$hChk_HideAndroid = GUICtrlCreateCheckbox("Hide Android", 8, 140)
	GUICtrlSetTip(-1, "Hide the Android emulator window during bot operation")
	$hChk_MiniGUIMode = GUICtrlCreateCheckbox("Mini GUI Mode", 8, 160)
	GUICtrlSetTip(-1, "Launch the bot in a compact mini GUI mode")
	$hChk_NoWatchdog = GUICtrlCreateCheckbox("No Watchdog", 110, 100)
	GUICtrlSetTip(-1, "Disable the watchdog process that monitors bot stability")
	$hChk_StartBotDocked = GUICtrlCreateCheckbox("Start Docked", 110, 120)
	GUICtrlSetTip(-1, "Automatically dock the bot window to the Android emulator on launch")
	$hChk_StartBotDockedAndShrinked = GUICtrlCreateCheckbox("Start Docked && Shrunk", 110, 140)
	GUICtrlSetTip(-1, "Automatically dock and shrink the bot window to the Android emulator on launch")

	If StringLen($g_sIniParameters) < $g_iParameters Then
		Local $iCount = $g_iParameters - StringLen($g_sIniParameters)
		For $i = 0 To $iCount
			$g_sIniParameters &= 0
		Next
	EndIf

	Local $aParameters = StringSplit($g_sIniParameters, "", 2)
	If $aParameters[0] = 1 Then GUICtrlSetState($hChk_DebugMode, $GUI_CHECKED)
	If $aParameters[1] = 1 Then GUICtrlSetState($hChk_DpiAwareness, $GUI_CHECKED)
	If $aParameters[2] = 1 Then GUICtrlSetState($hChk_HideAndroid, $GUI_CHECKED)
	If $aParameters[3] = 1 Then GUICtrlSetState($hChk_MiniGUIMode, $GUI_CHECKED)
	If $aParameters[4] = 1 Then GUICtrlSetState($hChk_NoWatchdog, $GUI_CHECKED)
	If $aParameters[5] = 1 Then GUICtrlSetState($hChk_StartBotDocked, $GUI_CHECKED)
	If $aParameters[6] = 1 Then GUICtrlSetState($hChk_StartBotDockedAndShrinked, $GUI_CHECKED)

	$hBtn_Save = GUICtrlCreateButton("Save", 76, 190, 97, 25, $WS_GROUP)
	GUISetState()



	Switch $g_sIniEmulator
		Case "BlueStacks5"
			GUICtrlSetData($hCmb_Emulator, "BlueStacks5")
		Case Else
			MsgBox($MB_OK, "Error", "Invalid config data - delete corrupted sections", 0, $g_hGUI_Edit)
	EndSwitch



	While 1

		Switch GUIGetMsg()
			Case $GUI_EVENT_CLOSE
				GUIDelete($g_hGUI_Edit)
				ExitLoop

			Case $hCmb_Emulator
				$sSelectedEmulator = GUICtrlRead($hCmb_Emulator)
				GUICtrlSetState($hIpt_Instance, $GUI_ENABLE)
				GUICtrlSetData($hIpt_Instance, "Pie64_")


			Case $hBtn_Save
				$sSelectedProfile = GUICtrlRead($hIpt_Profile)
				$sSelectedEmulator = GUICtrlRead($hCmb_Emulator)
				$sSelectedInstance = GUICtrlRead($hIpt_Instance)
				Local $iEndResult = ""
				$iEndResult &= (GUICtrlRead($hChk_DebugMode) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_DpiAwareness) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_HideAndroid) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_MiniGUIMode) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_NoWatchdog) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_StartBotDocked) = $GUI_CHECKED ? 1 : 0)
				$iEndResult &= (GUICtrlRead($hChk_StartBotDockedAndShrinked) = $GUI_CHECKED ? 1 : 0)
				IniDelete($g_sDirProfiles, $sLstbx_SelItem)
				IniWrite($g_sDirProfiles, $sSelectedProfile, "Profile", $sSelectedProfile)
				IniWrite($g_sDirProfiles, $sSelectedProfile, "Emulator", $sSelectedEmulator)
				IniWrite($g_sDirProfiles, $sSelectedProfile, "Instance", $sSelectedInstance)
				IniWrite($g_sDirProfiles, $sSelectedProfile, "Dir", ".")
				IniWrite($g_sDirProfiles, $sSelectedProfile, "Parameters", $iEndResult)
				GUIDelete($g_hGUI_Edit)
				ExitLoop
		EndSwitch

	WEnd
EndFunc   ;==>GUI_Edit


Func GUI_AutoStart()
	Local $sText = ""

	$g_hGUI_AutoStart = GUICreate("Auto Start Setup", 258, 187, $g_aGuiPos_Main[0], $g_aGuiPos_Main[1] + 150, -1, -1, $g_hGui_Main)
	$g_hLst_AutoStart = GUICtrlCreateList("", 8, 48, 241, 84, BitOR($LBS_SORT, $LBS_NOTIFY, $LBS_NOSEL))
	GUICtrlCreateLabel("Add or Remove a Profile from Autostart" & @CRLF & "These are currently in the Folder:", 8, 8, 220, 34)
	$hBtn_Add = GUICtrlCreateButton("Add", 8, 144, 97, 25, $WS_GROUP)
	$hBtn_Remove = GUICtrlCreateButton("Remove", 152, 144, 97, 25, $WS_GROUP)
	GUISetState()


	$Lstbx_Sel = _GUICtrlListView_GetSelectedIndices($g_hListview_Main, True)
	If $Lstbx_Sel[0] > 0 Then
		For $i = 1 To $Lstbx_Sel[0]
			$sLstbx_SelItem = _GUICtrlListView_GetItemText($g_hListview_Main, $Lstbx_Sel[$i])
			If $sLstbx_SelItem <> "" Then
				ReadIni($sLstbx_SelItem)
				If FileExists(@StartupDir & "\MyBot -" & $g_sIniProfile & ".lnk") = 0 Then
					GUICtrlSetState($hBtn_Add, $GUI_ENABLE)
					GUICtrlSetState($hBtn_Remove, $GUI_DISABLE)
				Else
					GUICtrlSetState($hBtn_Add, $GUI_DISABLE)
					GUICtrlSetState($hBtn_Remove, $GUI_ENABLE)
				EndIf
			EndIf
		Next
	EndIf


	UpdateList_AS()

	While 1

		Switch GUIGetMsg()

			Case $GUI_EVENT_CLOSE
				GUIDelete($g_hGUI_AutoStart)
				ExitLoop

			Case $hBtn_Add

				$Lstbx_Sel = _GUICtrlListView_GetSelectedIndices($g_hListview_Main, True)
				If $Lstbx_Sel[0] > 0 Then
					For $i = 1 To $Lstbx_Sel[0]
						$sLstbx_SelItem = _GUICtrlListView_GetItemText($g_hListview_Main, $Lstbx_Sel[$i])
						If $sLstbx_SelItem <> "" Then
							ReadIni($sLstbx_SelItem)
							If FileExists($g_sIniDir & "\" & $g_sBotFile) = 1 Then
								$g_sBotFile = $g_sBotFile
							ElseIf FileExists($g_sIniDir & "\" & $g_sBotFileAU3) = 1 Then
								$g_sBotFile = $g_sBotFileAU3
							EndIf

							FileCreateShortcut($g_sIniDir & "\" & $g_sBotFile, @StartupDir & "\MyBot -" & $g_sIniProfile & ".lnk", $g_sIniDir, $g_sIniProfile & " " & ($g_sIniEmulator = "BlueStacks3" ? "BlueStacks2" : $g_sIniEmulator) & " " & $g_sIniInstance, "Shortcut for Bot Profile:" & $g_sIniProfile)

							UpdateList_AS()
							If FileExists(@StartupDir & "\MyBot -" & $g_sIniProfile & ".lnk") = 0 Then
								GUICtrlSetState($hBtn_Remove, $GUI_DISABLE)
								GUICtrlSetState($hBtn_Add, $GUI_ENABLE)
							Else
								GUICtrlSetState($hBtn_Remove, $GUI_ENABLE)
								GUICtrlSetState($hBtn_Add, $GUI_DISABLE)
							EndIf
						EndIf
					Next
				EndIf



			Case $hBtn_Remove

				$Lstbx_Sel = _GUICtrlListView_GetSelectedIndices($g_hListview_Main, True)
				If $Lstbx_Sel[0] > 0 Then
					For $i = 1 To $Lstbx_Sel[0]
						$sLstbx_SelItem = _GUICtrlListView_GetItemText($g_hListview_Main, $Lstbx_Sel[$i])
						If $sLstbx_SelItem <> "" Then
							ReadIni($sLstbx_SelItem)
							If FileExists(@StartupDir & "\MyBot -" & $g_sIniProfile & ".lnk") = 1 Then
								FileDelete(@StartupDir & "\MyBot -" & $g_sIniProfile & ".lnk")
								GUICtrlSetData($g_hLst_AutoStart, "")

							EndIf

							UpdateList_AS()
							If FileExists(@StartupDir & "\MyBot -" & $g_sIniProfile & ".lnk") = 0 Then
								GUICtrlSetState($hBtn_Remove, $GUI_DISABLE)
								GUICtrlSetState($hBtn_Add, $GUI_ENABLE)
							Else
								GUICtrlSetState($hBtn_Remove, $GUI_ENABLE)
								GUICtrlSetState($hBtn_Add, $GUI_DISABLE)
							EndIf
						EndIf

					Next
				EndIf


		EndSwitch

	WEnd
EndFunc   ;==>GUI_AutoStart

Func RunSetup()
	$Lstbx_Sel = _GUICtrlListView_GetSelectedIndices($g_hListview_Main, True)
	If $Lstbx_Sel[0] > 0 Then
		For $i = 1 To $Lstbx_Sel[0]
			$sLstbx_SelItem = _GUICtrlListView_GetItemText($g_hListview_Main, $Lstbx_Sel[$i])
			If $sLstbx_SelItem <> "" Then
				ReadIni($sLstbx_SelItem)
				Local $sEmulator = $g_sIniEmulator
				If $g_sIniEmulator = "BlueStacks3" Then $sEmulator = "BlueStacks2"
				$aParameters = StringSplit($g_sIniParameters, "")
				Local $sSpecialParameter = ($aParameters[1] = 1 ? " /debug" : "") & ($aParameters[2] = 1 ? " /dpiaware" : "") & ($aParameters[3] = 1 ? " /hideandroid" : "") & ($aParameters[4] = 1 ? " /minigui" : "") & ($aParameters[5] = 1 ? " /nowatchdog" : "") & ($aParameters[6] = 1 ? " /dock1" : "") & ($aParameters[7] = 1 ? " /dock2" : "")
				Local $sInstance = $g_sIniInstance
				If FileExists($g_sIniDir & "\" & $g_sBotFile) = 1 Then
					ShellExecute($g_sBotFile, $g_sIniProfile & " " & $sEmulator & " " & $sInstance & $sSpecialParameter, $g_sIniDir)
				ElseIf FileExists($g_sIniDir & "\" & $g_sBotFileAU3) = 1 Then
					ShellExecute($g_sBotFileAU3, $g_sIniProfile & " " & $sEmulator & " " & $sInstance & $sSpecialParameter, $g_sIniDir)
				Else
					MsgBox($MB_OK, "No Bot found", "Couldn't find any Bot in the Directory, please check if you have the mybot.run.exe or the mybot.run.au3 in the Dir and if you selected the right Dir!", 0, $g_hGui_Main)
				EndIf
			EndIf
		Next
	EndIf
EndFunc   ;==>RunSetup

Func StartAll()
	Local $aSections = IniReadSectionNames($g_sDirProfiles)
	If IsArray($aSections) Then
		For $i = 1 To $aSections[0]
			If $aSections[$i] <> "Options" Then
				ReadIni($aSections[$i])
				Local $sEmulator = $g_sIniEmulator
				If $g_sIniEmulator = "BlueStacks3" Then $sEmulator = "BlueStacks2"
				Local $sInstance = $g_sIniInstance
				$aParameters = StringSplit($g_sIniParameters, "")
				Local $sSpecialParameter = ($aParameters[1] = 1 ? " /debug" : "") & ($aParameters[2] = 1 ? " /dpiaware" : "") & ($aParameters[3] = 1 ? " /hideandroid" : "") & ($aParameters[4] = 1 ? " /minigui" : "") & ($aParameters[5] = 1 ? " /nowatchdog" : "") & ($aParameters[6] = 1 ? " /dock1" : "") & ($aParameters[7] = 1 ? " /dock2" : "")
				If FileExists($g_sIniDir & "\" & $g_sBotFile) = 1 Then
					ShellExecute($g_sBotFile, $g_sIniProfile & " " & $sEmulator & " " & $sInstance & $sSpecialParameter, $g_sIniDir)
				ElseIf FileExists($g_sIniDir & "\" & $g_sBotFileAU3) = 1 Then
					ShellExecute($g_sBotFileAU3, $g_sIniProfile & " " & $sEmulator & " " & $sInstance & $sSpecialParameter, $g_sIniDir)
				Else
					MsgBox($MB_OK, "Error", "MyBot.run not found for profile: " & $g_sIniProfile, 0, $g_hGui_Main)
				EndIf
				Sleep(1000) ; Delay between profiles
			EndIf
		Next
	EndIf
EndFunc   ;==>StartAll

Func StopAll()
	Local $aProcesses = ProcessList("mybot.run.exe")
	For $i = 1 To $aProcesses[0][0]
		ProcessClose($aProcesses[$i][1])
	Next
EndFunc   ;==>StopAll

Func RestartAll()
	StopAll()
	Sleep(2000)
	StartAll()
EndFunc   ;==>RestartAll

Func CreateShortcut()
	Local $iCreatedSC = 0, $sBotFileName, $hSC
	$Lstbx_Sel = _GUICtrlListView_GetSelectedIndices($g_hListview_Main, True)
	If $Lstbx_Sel[0] > 0 Then
		For $i = 1 To $Lstbx_Sel[0]
			$sLstbx_SelItem = _GUICtrlListView_GetItemText($g_hListview_Main, $Lstbx_Sel[$i])
			If $sLstbx_SelItem <> "" Then
				ReadIni($sLstbx_SelItem)
				Local $sEmulator = $g_sIniEmulator
				If $g_sIniEmulator = "BlueStacks3" Then $sEmulator = "BlueStacks2"
				$aParameters = StringSplit($g_sIniParameters, "")
				Local $sSpecialParameter = ($aParameters[1] = 1 ? " /debug" : "") & ($aParameters[2] = 1 ? " /dpiaware" : "") & ($aParameters[3] = 1 ? " /hideandroid" : "") & ($aParameters[4] = 1 ? " /minigui" : "") & ($aParameters[5] = 1 ? " /nowatchdog" : "") & ($aParameters[6] = 1 ? " /dock1" : "") & ($aParameters[7] = 1 ? " /dock2" : "")
				If FileExists($g_sIniDir & "\" & $g_sBotFile) Then
					$sBotFileName = $g_sBotFile
				ElseIf FileExists($g_sIniDir & "\" & $g_sBotFileAU3) Then
					$sBotFileName = $g_sBotFileAU3
				Else
					MsgBox($MB_OK, "No Bot found", "Couldn't find any Bot in the Directory, please check if you have the mybot.run.exe or the mybot.run.au3 in the Dir and if you selected the right Dir!", 0, $g_hGui_Main)
				EndIf
				$hSC = FileCreateShortcut($g_sIniDir & "\" & $sBotFileName, @DesktopDir & "\MyBot -" & $g_sIniProfile & ".lnk", $g_sIniDir, $g_sIniProfile & " " & $sEmulator & " " & $g_sIniInstance & $sSpecialParameter, "Shortcut for Bot Profile:" & $g_sIniProfile)
				If $hSC = 1 Then $iCreatedSC += 1

			EndIf

		Next
		If $iCreatedSC = 1 Then
		ElseIf $iCreatedSC > 1 Then
		EndIf
		$iCreatedSC = 0
	EndIf
EndFunc   ;==>CreateShortcut

Func UpdateList_Main()
	Local $j = 0, $aSections

	_GUICtrlListView_BeginUpdate($g_hListview_Main)
	_GUICtrlListView_DeleteAllItems($g_hListview_Main)
	$aSections = IniReadSectionNames($g_sDirProfiles)
	_ArraySort($aSections, 0, 1)
	For $i = 1 To UBound($aSections, 1) - 1
		If $aSections[$i] <> "Options" Then
			_GUICtrlListView_AddItem($g_hListview_Main, $aSections[$i])
			$j += 1
		EndIf
	Next
	_GUICtrlListView_EndUpdate($g_hListview_Main)
EndFunc   ;==>UpdateList_Main



Func UpdateList_AS()
	Local $aSections

	GUICtrlSetData($g_hLst_AutoStart, "")
	$aSections = IniReadSectionNames($g_sDirProfiles)
	If @error <> 0 Then
	Else
		For $i = 1 To $aSections[0]
			$sProfiles = IniRead($g_sDirProfiles, $aSections[$i], "Profile", "")
			If FileExists(@StartupDir & "\MyBot -" & $sProfiles & ".lnk") Then
				GUICtrlSetData($g_hLst_AutoStart, $sProfiles)
			EndIf
		Next
	EndIf

EndFunc   ;==>UpdateList_AS

Func ReadIni($sSelectedProfile)

	$g_sIniProfile = IniRead($g_sDirProfiles, $sSelectedProfile, "Profile", "")
	If StringRegExp($g_sIniProfile, " ") = 1 Then
		$g_sIniProfile = '"' & $g_sIniProfile & '"'
	EndIf
	$g_sIniEmulator = IniRead($g_sDirProfiles, $sSelectedProfile, "Emulator", "")
	$g_sIniInstance = IniRead($g_sDirProfiles, $sSelectedProfile, "Instance", "")
	$g_sIniDir = @ScriptDir ; Use script directory

	Local $iParam
	For $i = 0 To $g_iParameters
		$iParam &= 0
	Next
	$g_sIniParameters = IniRead($g_sDirProfiles, $sSelectedProfile, "Parameters", $iParam)

EndFunc   ;==>ReadIni



Func WM_CONTEXTMENU($hWnd, $msg, $wParam, $lParam)
	Local $tPoint = _WinAPI_GetMousePos(True, GUICtrlGetHandle($g_hListview_Main))
	Local $iY = DllStructGetData($tPoint, "Y")

	$lst2 = _GUICtrlListView_GetItemCount($g_hListview_Main)
	If $lst2 > 0 Then
		For $i = 0 To 50
			$iLstbx_GetSel = _GUICtrlListView_GetSelectedCount($g_hListview_Main)
			If $iLstbx_GetSel > 1 Then
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 0)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 1)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 2)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 4)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 5)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 6)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 8)
				_GUICtrlMenu_SetItemDisabled($g_hContext_Main, 9)
			ElseIf $iLstbx_GetSel < 2 Then
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 0)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 1)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 2)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 4)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 5)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 6)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 8)
				_GUICtrlMenu_SetItemEnabled($g_hContext_Main, 9)
			EndIf

			Local $aRect = _GUICtrlListView_GetItemRect($g_hListview_Main, $i)
			If ($iY >= $aRect[1]) And ($iY <= $aRect[3]) Then _ContextMenu($i)
		Next
		Return $GUI_RUNDEFMSG

	ElseIf _GUICtrlListView_GetItemCount($g_hListview_Main) < 1 Then
		Return
	EndIf
EndFunc   ;==>WM_CONTEXTMENU



Func _ContextMenu($sItem)
	Switch _GUICtrlMenu_TrackPopupMenu($g_hContext_Main, GUICtrlGetHandle($g_hListview_Main), -1, -1, 1, 1, 2)
		Case $eStartVM
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			StartEmuProfile($sProfile)

		Case $eStopVM
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			StopEmuProfile($sProfile)

		Case $eRestartVM
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			RestartEmuProfile($sProfile)

		Case $eStartBot
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			StartBotProfile($sProfile)

		Case $eStopBot
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			StopBotProfile($sProfile)

		Case $eRestartBot
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			RestartBotProfile($sProfile)

		Case $eEdit
			GUISetState(@SW_DISABLE, $g_hGui_Main)
			$g_aGuiPos_Main = WinGetPos($g_hGui_Main)
			GUI_Edit()
			UpdateList_Main()
			GUISetState(@SW_ENABLE, $g_hGui_Main)

		Case $eDelete
			$sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $sItem)
			IniDelete($g_sDirProfiles, $sProfile)
			If FileExists(@StartupDir & "\MyBot -" & $sProfile & ".lnk") Then FileDelete(@StartupDir & "\MyBot -" & $sProfile & ".lnk")
			UpdateList_Main()

	EndSwitch
EndFunc   ;==>_ContextMenu


Func WM_NOTIFY($hWnd, $iMsg, $iwParam, $ilParam)

	Local $hWndFrom, $iCode, $tNMHDR, $hWndListView
	$hWndListView = $g_hListview_Main
	If Not IsHWnd($g_hListview_Main) Then $hWndListView = GUICtrlGetHandle($g_hListview_Main)

	$tNMHDR = DllStructCreate($tagNMHDR, $ilParam)
	$hWndFrom = HWnd(DllStructGetData($tNMHDR, "hWndFrom"))
	$iCode = DllStructGetData($tNMHDR, "Code")
	Switch $hWndFrom
		Case $hWndListView
			Switch $iCode

				Case $NM_DBLCLK
					Local $tInfo = DllStructCreate($tagNMITEMACTIVATE, $ilParam)

					$Index = DllStructGetData($tInfo, "Index")

					$subitemNR = DllStructGetData($tInfo, "SubItem")
					If $Index <> -1 Then
						If _IsPressed(10) Then
							$Lstbx_Sel = _GUICtrlListView_GetItemText($g_hListview_Main, $Index)
							ReadIni($Lstbx_Sel)
							ToolTip("Profile: " & $g_sIniProfile & @CRLF & "Emulator: " & $g_sIniEmulator & @CRLF & "Instance: " & $g_sIniInstance & @CRLF & "Directory: " & $g_sIniDir)
							Do
								Sleep(100)
							Until _IsPressed(10) = False
							ToolTip("")
						Else
							RunSetup()
						EndIf
					EndIf

			EndSwitch
	EndSwitch
	Return $GUI_RUNDEFMSG
EndFunc   ;==>WM_NOTIFY

#Region Android
Func GetBlueStacksPath()
	$sBlueStacksPath = RegRead($HKLM & "\SOFTWARE\BlueStacks\", "InstallDir")
	$sPlusMode = RegRead($HKLM & "\SOFTWARE\BlueStacks\", "Engine") = "plus"
	$sFrontend = "HD-Frontend.exe"
	If $sPlusMode Then $sFrontend = "HD-Plus-Frontend.exe"
	If $sBlueStacksPath = "" And FileExists(@ProgramFilesDir & "\BlueStacks\" & $sFrontend) = 1 Then
		$sBlueStacksPath = @ProgramFilesDir & "\BlueStacks\"
	EndIf

	Return $sBlueStacksPath
EndFunc   ;==>GetBlueStacksPath

Func GetBlueStacks5Path()
	Local $sBS5Path = ""
	
	; Check registry
	$sBS5Path = RegRead("HKLM\SOFTWARE\BlueStacks_nxt", "InstallDir")
	If $sBS5Path <> "" And FileExists($sBS5Path & "HD-Player.exe") Then Return $sBS5Path
	
	; Check 64-bit registry
	$sBS5Path = RegRead("HKLM64\SOFTWARE\BlueStacks_nxt", "InstallDir")
	If $sBS5Path <> "" And FileExists($sBS5Path & "HD-Player.exe") Then Return $sBS5Path
	
	; Check common paths
	Local $aPaths[] = [@ProgramFilesDir & "\BlueStacks_nxt\", _
						@ProgramFilesDir & "\BlueStacks X\", _
						"C:\Program Files\BlueStacks_nxt\", _
						"C:\Program Files (x86)\BlueStacks_nxt\"]
	
	For $sPath In $aPaths
		If FileExists($sPath & "HD-Player.exe") Then Return $sPath
	Next
	
	Return "" ; Not found
EndFunc   ;==>GetBlueStacks5Path

Func IsAndroidInstalled($sAndroid)
	Local $sPath, $sFile, $bIsInstalled = False

	If $sAndroid = "BlueStacks5" Then
		$sPath = GetBlueStacksPath()
		$sFile = "HD-Player.exe"
		If FileExists($sPath & $sFile) = 1 Then $bIsInstalled = True
	EndIf

	Return $bIsInstalled
EndFunc   ;==>IsAndroidInstalled

Func GetInstanceMgrPath($sAndroid)
	Local $sManagerPath

	Switch $sAndroid
		Case "BlueStacks5"
			$sManagerPath = GetBlueStacksPath() & "BstkVMMgr.exe"
	EndSwitch

	Return $sManagerPath

EndFunc   ;==>GetInstanceMgrPath
#EndRegion Android
#Region CMD
Func LaunchConsole($sCMD, $sParameter, $bProcessKilled, $iTimeOut = 10000)


	Local $sData, $iPID, $hTimer

	If StringLen($sParameter) > 0 Then $sCMD &= " " & $sParameter

	$hTimer = TimerInit()
	$bProcessKilled = False

	$iPID = Run($sCMD, "", @SW_HIDE, $STDERR_MERGED)
	If $iPID = 0 Then
		Return
	EndIf

	Local $hProcess
	If _WinAPI_GetVersion() >= 6.0 Then
		$hProcess = _WinAPI_OpenProcess($PROCESS_QUERY_LIMITED_INFORMATION, 0, $iPID)
	Else
		$hProcess = _WinAPI_OpenProcess($PROCESS_QUERY_INFORMATION, 0, $iPID)
	EndIf

	$sData = ""
	$iDelaySleep = 100
	Local $iTimeOut_Sec = Round($iTimeOut / 1000)

	While True
		If $hProcess Then
			_WinAPI_WaitForSingleObject($hProcess, $iDelaySleep)
		Else
			Sleep($iDelaySleep)
		EndIf
		$sData &= StdoutRead($iPID)
		If @error Then ExitLoop
		If ($iTimeOut > 0 And TimerDiff($hTimer) > $iTimeOut) Then ExitLoop
	WEnd

	If $hProcess Then
		_WinAPI_CloseHandle($hProcess)
		$hProcess = 0
	EndIf

	CleanLaunchOutput($sData)

	If ProcessExists($iPID) Then
		If ProcessClose($iPID) = 1 Then
			$bProcessKilled = True
		EndIf
	EndIf
	StdioClose($iPID)
	Return $sData
EndFunc   ;==>LaunchConsole

Func CleanLaunchOutput(ByRef $output)

	$output = StringReplace($output, @CR & @CR, "")
	$output = StringReplace($output, @CRLF & @CRLF, "")
	If StringRight($output, 1) = @LF Then $output = StringLeft($output, StringLen($output) - 1)
	If StringRight($output, 1) = @CR Then $output = StringLeft($output, StringLen($output) - 1)
EndFunc   ;==>CleanLaunchOutput

Func StartEmu()
	Local $iCount = _GUICtrlListView_GetItemCount($g_hListview_Main)
	For $i = 0 To $iCount - 1
		Local $sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $i)
		ReadIni($sProfile)
		Local $sCmd = ""
		Switch $g_sIniEmulator
			Case "BlueStacks5"
				Local $sBS5Path = GetBlueStacks5Path()
				If $sBS5Path <> "" Then
					$sCmd = $sBS5Path & "HD-Player.exe"
					ShellExecute($sCmd, "--instance " & $g_sIniInstance)
				EndIf
		EndSwitch
		Sleep(1000)
	Next
EndFunc

Func StopEmu()
	; Stop only BlueStacks instances associated with profiles
	Local $iCount = _GUICtrlListView_GetItemCount($g_hListview_Main)
	For $i = 0 To $iCount - 1
		Local $sProfile = _GUICtrlListView_GetItemText($g_hListview_Main, $i)
		StopEmuProfile($sProfile)
	Next
EndFunc

Func StartEmuProfile($sProfile)
	ReadIni($sProfile)
	Local $sCmd = ""
	Switch $g_sIniEmulator
		Case "BlueStacks5"
			Local $sBS5Path = GetBlueStacks5Path()
			If $sBS5Path <> "" Then
				$sCmd = $sBS5Path & "HD-Player.exe"
				ShellExecute($sCmd, "--instance " & $g_sIniInstance)
			Else
				MsgBox($MB_OK, "Error", "BlueStacks 5 not found - verify installation", 0, $g_hGui_Main)
			EndIf
	EndSwitch
EndFunc

Func StopEmuProfile($sProfile)
	ReadIni($sProfile)
	Switch $g_sIniEmulator
		Case "BlueStacks5"
			; Stop the specific BlueStacks instance using WMI
			Local $objWMIService = ObjGet("winmgmts:\\.\root\cimv2")
			Local $colProcesses = $objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'HD-Player.exe'")
			
			For $objProcess In $colProcesses
				Local $sCmdLine = $objProcess.CommandLine
				If StringInStr($sCmdLine, "--instance " & $g_sIniInstance) > 0 Or _
				   StringInStr($sCmdLine, '--instance "' & $g_sIniInstance & '"') > 0 Then
					$objProcess.Terminate()
					Sleep(500)
					ExitLoop
				EndIf
			Next
	EndSwitch
EndFunc

Func RestartEmuProfile($sProfile)
	StopEmuProfile($sProfile)
	Sleep(3000)
	StartEmuProfile($sProfile)
EndFunc

Func StartBotProfile($sProfile)
	ReadIni($sProfile)
	Local $sEmulator = $g_sIniEmulator
	If $g_sIniEmulator = "BlueStacks3" Then $sEmulator = "BlueStacks2"
	$aParameters = StringSplit($g_sIniParameters, "")
	Local $sSpecialParameter = ($aParameters[1] = 1 ? " /debug" : "") & ($aParameters[2] = 1 ? " /dpiaware" : "") & ($aParameters[3] = 1 ? " /hideandroid" : "") & ($aParameters[4] = 1 ? " /minigui" : "") & ($aParameters[5] = 1 ? " /nowatchdog" : "") & ($aParameters[6] = 1 ? " /dock1" : "") & ($aParameters[7] = 1 ? " /dock2" : "")
	Local $sInstance = $g_sIniInstance
	If FileExists($g_sIniDir & "\\" & $g_sBotFile) = 1 Then
		ShellExecute($g_sBotFile, $g_sIniProfile & " " & $sEmulator & " " & $sInstance & $sSpecialParameter, $g_sIniDir)
	ElseIf FileExists($g_sIniDir & "\\" & $g_sBotFileAU3) = 1 Then
		ShellExecute($g_sBotFileAU3, $g_sIniProfile & " " & $sEmulator & " " & $sInstance & $sSpecialParameter, $g_sIniDir)
	Else
		MsgBox($MB_OK, "Error", "MyBot.run.exe or .au3 not found in profile directory", 0, $g_hGui_Main)
	EndIf
EndFunc

Func StopBotProfile($sProfile)
	ReadIni($sProfile)
	; Find and close MyBot.run.exe process for this specific profile
	Local $objWMIService = ObjGet("winmgmts:\\.\root\cimv2")
	Local $colProcesses = $objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'MyBot.run.exe'")
	
	For $objProcess In $colProcesses
		Local $sCmdLine = $objProcess.CommandLine
		; Check if this process belongs to this profile
		If StringInStr($sCmdLine, $g_sIniProfile) > 0 Or _
		   StringInStr($sCmdLine, '"' & $g_sIniProfile & '"') > 0 Then
			$objProcess.Terminate()
			Sleep(500)
			ExitLoop
		EndIf
	Next
EndFunc

Func RestartBotProfile($sProfile)
	StopBotProfile($sProfile)
	Sleep(2000)
	StartBotProfile($sProfile)
EndFunc

Func RestartEmu()
	StopEmu()
	Sleep(2000)
	StartEmu()
EndFunc

Func _TrayEvent($iEvent = $TRAY_EVENT_PRIMARYDOWN)
	If $iEvent = $TRAY_EVENT_PRIMARYDOWN Then
		If $g_bMinimizedToTray Then
			$g_bMinimizedToTray = False
			GUISetState(@SW_RESTORE, $g_hGui_Main)
			WinActivate($g_hGui_Main)
		Else
			$g_bMinimizedToTray = True
			GUISetState(@SW_MINIMIZE, $g_hGui_Main)
		EndIf
	EndIf
EndFunc

Func WM_SIZE($hWnd, $iMsg, $wParam, $lParam)
	If $hWnd = $g_hGui_Main Then
		If BitAND($wParam, 1) Then ; Minimized
			$g_bMinimizedToTray = True
			; Keep in taskbar
			Return $GUI_RUNDEFMSG
		ElseIf $wParam = 0 And $g_bMinimizedToTray Then ; Restored
			; Restore window
			$g_bMinimizedToTray = False
			GUISetState(@SW_RESTORE, $g_hGui_Main)
			WinActivate($g_hGui_Main)
			Return 0
		EndIf
	EndIf
	Return $GUI_RUNDEFMSG
EndFunc

Func WM_SYSCOMMAND($hWnd, $iMsg, $wParam, $lParam)
	If $hWnd = $g_hGui_Main Then
		If $wParam = 0xF020 Then ; SC_MINIMIZE
			$g_bMinimizedToTray = True
			; Minimize to taskbar
			Return $GUI_RUNDEFMSG
		ElseIf $wParam = 0xF120 Then ; SC_RESTORE
			; Restore from taskbar
			$g_bMinimizedToTray = False
			Return $GUI_RUNDEFMSG
		EndIf
	EndIf
	Return $GUI_RUNDEFMSG
EndFunc

Func TrayShow()
	$g_bMinimizedToTray = False
	GUISetState(@SW_SHOW, $g_hGui_Main)
	GUISetState(@SW_RESTORE, $g_hGui_Main)
	WinActivate($g_hGui_Main)
EndFunc

Func TrayStartAll()
	StartAll()
EndFunc

Func TrayRestartAll()
	RestartAll()
EndFunc

Func TrayStopAll()
	StopAll()
EndFunc

Func TrayStartEmu()
	StartEmu()
EndFunc

Func TrayRestartEmu()
	RestartEmu()
EndFunc

Func TrayStopEmu()
	StopEmu()
EndFunc

Func TrayExit()
	_Exit()
EndFunc

Func TrayOpenMyBotDir()
	ShellExecute(@ScriptDir)
	TrayItemSetState($g_hTrayItem_MyBotDir, $TRAY_UNCHECKED)
EndFunc

Func TrayOpenProfileDir()
	ShellExecute(@ScriptDir & "\Profiles\")
	TrayItemSetState($g_hTrayItem_ProfileDir, $TRAY_UNCHECKED)
EndFunc

Func ShowTrayMenu()
	Local $aMousePos = MouseGetPos()
	Local $hTrayGui = GUICreate("Tray Menu", 120, 200, $aMousePos[0], $aMousePos[1] - 200, $WS_POPUP, $WS_EX_TOPMOST)
	GUISetBkColor(0xFFFFFF, $hTrayGui)
	Local $btnStartAll = GUICtrlCreateButton("Start All Bots", 10, 10, 100, 25)
	Local $btnRestartAll = GUICtrlCreateButton("Restart All Bots", 10, 40, 100, 25)
	Local $btnStopAll = GUICtrlCreateButton("Stop All Bots", 10, 70, 100, 25)
	Local $btnStartEmu = GUICtrlCreateButton("Start All VMs", 10, 100, 100, 25)
	Local $btnRestartEmu = GUICtrlCreateButton("Restart All VMs", 10, 130, 100, 25)
	Local $btnStopEmu = GUICtrlCreateButton("Stop All VMs", 10, 160, 100, 25)
	GUISetState(@SW_SHOW, $hTrayGui)

	While 1
		Switch GUIGetMsg()
			Case $GUI_EVENT_CLOSE
				GUIDelete($hTrayGui)
				Return
			Case $btnStartAll
				TrayStartAll()
				GUIDelete($hTrayGui)
				Return
			Case $btnRestartAll
				TrayRestartAll()
				GUIDelete($hTrayGui)
				Return
			Case $btnStopAll
				TrayStopAll()
				GUIDelete($hTrayGui)
				Return
			Case $btnStartEmu
				TrayStartEmu()
				GUIDelete($hTrayGui)
				Return
			Case $btnRestartEmu
				TrayRestartEmu()
				GUIDelete($hTrayGui)
				Return
			Case $btnStopEmu
				TrayStopEmu()
				GUIDelete($hTrayGui)
				Return
		EndSwitch
	WEnd
EndFunc

Func _Exit()
	Exit
EndFunc

#EndRegion CMD

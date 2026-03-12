; #FUNCTION# ====================================================================================================================
; Name ..........: MBR GUI Design
; Description ...: This file creates the "Search" tab under the "Options" tab under the "Search & Attack" tab under the "Attack Plan" tab
; Syntax ........:
; Parameters ....: None
; Return values .: None
; Author ........:
; Modified ......: CodeSlinger69 (2017)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================
#include-once
#include <GuiSlider.au3>

Global $g_hChkSearchReduction = 0, $g_hTxtSearchReduceCount = 0, $g_hTxtSearchReduceGold = 0, $g_hTxtSearchReduceElixir = 0, $g_hTxtSearchReduceGoldPlusElixir = 0, _
	   $g_hTxtSearchReduceDark = 0, $g_hTxtSearchReduceTrophy = 0
Global $g_hTxtVSDelayMin = 0, $g_hTxtVSDelayMax = 0
Global $g_hChkEnableTournament = 0
Global $g_hChkAttackNow = 0, $g_hCmbAttackNowDelay = 0, $g_hLblAttackNow = 0, $g_hLblAttackNowSec = 0, $g_hChkRestartSearchLimit = 0, $g_hTxtRestartSearchlimit = 0, $g_hChkAlertSearch = 0

Global $g_hChkRestartSearchPickupHero = 0

Func CreateAttackSearchOptionsSearch()

	Local $sTxtTip = ""
	Local $x = 25, $y = 45
	GUICtrlCreateGroup(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "Group_01", "Search Reduction"), $x - 20, $y - 20, 223, 165)
	$x -= 13
		$g_hChkSearchReduction = GUICtrlCreateCheckbox(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkSearchReduction", "Enable Search Reduction"), $x, $y - 4, -1, -1)
			_GUICtrlSetTip(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkSearchReduction_Info_01", "Check this if you want the search values to automatically be lowered after a certain amount of searches."))
			GUICtrlSetState(-1, $GUI_UNCHECKED)
			GUICtrlSetOnEvent(-1, "chkSearchReduction")

	$y += 15
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceCount", "Reduce targets every"), $x, $y + 3, -1, -1)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceCount_Info_01", "Enter the No. of searches to wait before each reduction occurs.")
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtSearchReduceCount = GUICtrlCreateInput("20", $x + 115, $y + 2, 40, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 3)
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR Global GUI Design", "search(es).", -1), $x + 160, $y + 3, -1, -1)

	$y += 21
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceGold", "- Reduce Gold"), $x, $y + 3, -1, 17)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceGold_Info_01", "Lower value for Gold by this amount on each step.")
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtSearchReduceGold = GUICtrlCreateInput("2000", $x + 115, $y, 40, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 5)
		_GUICtrlCreateIcon($g_sLibIconPath, $eIcnGold, $x + 160, $y, 16, 16)
			_GUICtrlSetTip(-1, $sTxtTip)

	$y += 21
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceElixir", "- Reduce Elixir"), $x, $y + 3, -1, 17)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceElixir_Info_01", "Lower value for Elixir by this amount on each step.")
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtSearchReduceElixir = GUICtrlCreateInput("2000", $x + 115, $y, 40, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 5)
		_GUICtrlCreateIcon($g_sLibIconPath, $eIcnElixir, $x + 160, $y, 16, 16)
			_GUICtrlSetTip(-1, $sTxtTip)

	$y += 21
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceGoldPlusElixir", "- Reduce Gold + Elixir"), $x, $y + 3, -1, 17)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceGoldPlusElixir_Info_01", "Lower total sum for G+E by this amount on each step.")
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtSearchReduceGoldPlusElixir = GUICtrlCreateInput("4000", $x + 115, $y, 40, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 5)
		_GUICtrlCreateIcon($g_sLibIconPath, $eIcnGold, $x + 160, $y + 1, 16, 16)
			_GUICtrlSetTip(-1, $sTxtTip)
		GUICtrlCreateLabel("+", $x + 176, $y + 1, -1, -1)
			_GUICtrlSetTip(-1, $sTxtTip)
		_GUICtrlCreateIcon($g_sLibIconPath, $eIcnElixir, $x + 182, $y + 1, 16, 16)
			_GUICtrlSetTip(-1, $sTxtTip)

	$y += 21
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceDark", "- Reduce Dark Elixir"), $x, $y + 3, -1, 17)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceDark_Info_01", "Lower value for Dark Elixir by this amount on each step.")
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtSearchReduceDark = GUICtrlCreateInput("100", $x + 115, $y, 40, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 3)
		_GUICtrlCreateIcon($g_sLibIconPath, $eIcnDark, $x + 160, $y, 16, 16)
			_GUICtrlSetTip(-1, $sTxtTip)

	$y += 21
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceTrophy", "- Reduce Trophies"), $x, $y + 3, -1, 17)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblSearchReduceTrophy_Info_01", "Lower value for Trophies by this amount on each step.")
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtSearchReduceTrophy = GUICtrlCreateInput("2", $x + 115, $y, 40, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 1)
		_GUICtrlCreateIcon($g_sLibIconPath, $eIcnTrophy, $x + 160, $y, 16, 16)
			_GUICtrlSetTip(-1, $sTxtTip)
	GUICtrlCreateGroup("", -99, -99, 1, 1)

	$x = 25
	$y = 212
	GUICtrlCreateGroup(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "Group_02", "Village Search Delay"), $x - 20, $y - 20, 180, 72)
		Local $sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblMinVSDelay_Info_01", "Use this slider to change the time to wait between Next clicks when searching for a Village to Attack.") & @CRLF & _
				   GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblMinVSDelay_Info_02", "This might compensate for Out of Sync errors on some PC's.") & @CRLF & _
				   GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblMinVSDelay_Info_03", "NO GUARANTEES! This will not always have the same results!")
		GUICtrlCreateLabel("Min Delay:", $x - 15, $y, -1, -1)
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtVSDelayMin = GUICtrlCreateSlider($x + 50, $y, 100, 20, BitOR($TBS_HORZ, $TBS_AUTOTICKS, $TBS_TOOLTIPS))
			_GUICtrlSetTip(-1, $sTxtTip)
			_GUICtrlSlider_SetRange(-1, 0, 10)
			GUICtrlSetData(-1, 1)

	$y += 25
		$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblMaxVSDelay_Info_01", "Enable random village search delay value by setting") & @CRLF & _
					   GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblMaxVSDelay_Info_02", "bottom Max slide value higher than the top minimum slide")
		GUICtrlCreateLabel("Max Delay:", $x - 15, $y, -1, -1)
			_GUICtrlSetTip(-1, $sTxtTip)
		$g_hTxtVSDelayMax = GUICtrlCreateSlider($x + 50, $y, 100, 20, BitOR($TBS_HORZ, $TBS_AUTOTICKS, $TBS_TOOLTIPS))
			_GUICtrlSetTip(-1, $sTxtTip)
			_GUICtrlSlider_SetRange(-1, 0, 10)
			GUICtrlSetData(-1, 4)
	GUICtrlCreateGroup("", -99, -99, 1, 1)

	$x = 253
	$y = 45
	GUICtrlCreateGroup(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "Group_03", "Search Options"), $x - 20, $y - 20, 189, 165)
		$g_hChkRestartSearchLimit = GUICtrlCreateCheckbox( GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkRestartSearchLimit", "Restart every") & ":", $x - 15, $y - 4, -1, -1)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkRestartSearchLimit_Info_01", "Return To Base after x searches and restart to search enemy villages.")
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetState(-1, $GUI_CHECKED)
			GUICtrlSetOnEvent(-1, "chkRestartSearchLimit")
		$g_hTxtRestartSearchlimit = GUICtrlCreateInput("50", $x, $y + 15, 25, 18, BitOR($GUI_SS_DEFAULT_INPUT, $ES_CENTER, $ES_NUMBER))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetLimit(-1, 3)
			;GUICtrlSetState(-1, $GUI_DISABLE)  ; Only needed when unchecked at bot start
		GUICtrlCreateLabel(GetTranslatedFileIni("MBR Global GUI Design", "search(es).", -1), $x + 32, $y + 17, -1, -1)

	$y += 25
		$g_hChkAttackNow = GUICtrlCreateCheckbox(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkAttackNow", "Attack Now! option."), $x - 15, $y + 11, -1, -1)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkAttackNow_Info_01", "Check this if you want the option to have an 'Attack Now!' button next to") & @CRLF & _
					   GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkAttackNow_Info_02", "the Start and Pause buttons to bypass the dead base or all base search values.") & @CRLF & _
					   GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "ChkAttackNow_Info_03", "The Attack Now! button will only appear when searching for villages to Attack.")
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetOnEvent(-1, "chkAttackNow")
		$g_hLblAttackNow = GUICtrlCreateLabel(GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblAttackNow", "Add") & ":", $x - 10, $y + 35, 27, -1, $SS_RIGHT)
			$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Options-Search", "LblAttackNow_Info_01", "Add this amount of reaction time to slow down the search.")
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetState(-1, $GUI_DISABLE)
		$g_hCmbAttackNowDelay = GUICtrlCreateCombo("", $x + 15, $y + 32, 35, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetData(-1, "0|1|2|3|4|5", "3") ; default value 3
			GUICtrlSetState(-1, $GUI_DISABLE)
		$g_hLblAttackNowSec = GUICtrlCreateLabel(GetTranslatedFileIni("MBR Global GUI Design", "sec.", -1), $x + 55, $y + 35, -1, -1)
			_GUICtrlSetTip(-1, $sTxtTip)
			GUICtrlSetState(-1, $GUI_DISABLE)

EndFunc   ;==>CreateAttackSearchOptionsSearch

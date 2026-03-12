; #FUNCTION# ====================================================================================================================
; Name ..........: MBR GUI Design
; Description ...: This file creates the "Attack" tab under the "DeadBase" tab under the "Search & Attack" tab under the "Attack Plan" tab
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

; Attack with
Global $g_hCmbDBAlgorithm = 0, $g_hCmbDBSelectTroop = 0, $g_hChkDBKingAttack = 0, $g_hChkDBQueenAttack = 0, $g_hChkDBWardenAttack = 0, $g_hChkDBDropCC = 0

Global $g_hPicDBKingAttack = 0, $g_hPicDBQueenAttack = 0, $g_hPicDBWardenAttack = 0, $g_hPicDBDropCC = 0

Global $g_hCmbDBSiege = 0, $g_hCmbDBWardenMode = 0, $g_hChkDBChampionAttack = 0, $g_hPicDBChampionAttack = 0
Global $g_hChkDBPrinceAttack = 0, $g_hPicDBPrinceAttack = 0
Global $g_hChkDBDragonDukeAttack = 0, $g_hPicDBDragonDukeAttack = 0

Func CreateAttackSearchDeadBaseAttack()
	Local $sTxtTip = ""
	Local $x = 25, $y = 40
	GUICtrlCreateGroup(GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Group_01", "Attack Mode"), $x - 20, $y - 15, 146, 182)
	$x -= 15
	$y += 2
	$g_hCmbDBAlgorithm = GUICtrlCreateCombo("", $x, $y, 135, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	_GUICtrlSetTip(-1, "")
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_01", "Standard Attack") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_02", "Scripted Attack") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_04", "SmartFarm Attack"), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_01", -1))
	GUICtrlSetOnEvent(-1, "cmbDBAlgorithm")

	$y += 27
	$g_hCmbDBSelectTroop = GUICtrlCreateCombo("", $x, $y, 135, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_01", "Use All Troops") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_02", "Use Troops in Barracks") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_03", "Barb Only") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_04", "Arch Only") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_05", "B+A") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_06", "B+Gob") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_07", "A+Gob") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_08", "B+A+Gi") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_09", "B+A+Gob+Gi") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_10", "B+A+Hog Rider") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_11", "B+A+Minion"), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_01", -1))
	_GUICtrlSetTip(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Info_01", "Select the troops to use in attacks"))

	$y += 27
	$g_hPicDBKingAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnKing, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-King_Info_01", "Use your King when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-King_Info_02", "Enabled with TownHall 7 and higher")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBKingAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$x += 46
	$g_hPicDBQueenAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnQueen, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Queen_Info_01", "Use your Queen when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Queen_Info_02", "Enabled with TownHall 8 and higher")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBQueenAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$x += 46
	$g_hPicDBPrinceAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnPrince, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Prince_Info_01", "Use your Prince when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Prince_Info_02", "Enabled with TownHall 9 and higher")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBPrinceAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$y += 27
	$x -= 92
	$g_hPicDBWardenAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnWarden, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Warden_Info_01", "Use your Warden when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Warden_Info_02", "Enabled with Townhall 11")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBWardenAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)
	GUICtrlSetOnEvent(-1, "chkDBWardenAttack")

	$x += 46
	$g_hCmbDBWardenMode = GUICtrlCreateCombo("", $x, $y, 90, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_01", "Ground mode") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_02", "Air mode") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_03", "Default mode"), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_03", -1))
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Tip", "Select Grand Warden's mode 'Ground' or 'Air'" & @CRLF & _
			"The Bot will always check Grand Warden's mode before every attack" & @CRLF & _
			"Choose 'Default mode' to bypass Grand Warden check")
	_GUICtrlSetTip(-1, $sTxtTip)

	$y += 27
	$x -= 46
	$g_hPicDBChampionAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnChampion, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Champion_Info_01", "Use your Champion when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Champion_Info_02", "Enabled with TownHall 13 and higher")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBChampionAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$x += 46
	$g_hPicDBDragonDukeAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnDragonDuke, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-DragonDuke_Info_01", "Use your Dragon Duke when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-DragonDuke_Info_02", "Enabled with TownHall 15 and higher")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBDragonDukeAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$y += 27
	$x -= 46
	$g_hPicDBDropCC = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnCC, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Clan Castle_Info_01", "Drop your Clan Castle in battle if it contains troops.")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkDBDropCC = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)
	GUICtrlSetOnEvent(-1, "chkDBDropCC")

	$x += 46
	$g_hCmbDBSiege = GUICtrlCreateCombo("", $x, $y, 92, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_01", "Castle only") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_02", "Wall Wrecker") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_03", "Battle Blimp") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_04", "Stone Slammer") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_07", "Siege Barracks") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_08", "Log Launcher") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_09", "Flame Flinger") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_10", "Battle Drill") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_11", "Troop Launcher") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_05", "Any Siege") & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_06", "Default"), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_06", -1))
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Tip", "Select Castle or Siege to be used." & @CRLF & _
			"The Bot will always check Castle/Siege type before every attack." & @CRLF & _
			"Choose 'Default' to bypass Castle/Siege check")
	_GUICtrlSetTip(-1, $sTxtTip)

	GUICtrlCreateGroup("", -99, -99, 1, 1)
EndFunc   ;==>CreateAttackSearchDeadBaseAttack

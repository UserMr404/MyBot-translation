; #FUNCTION# ====================================================================================================================
; Name ..........: MBR GUI Design
; Description ...: This file creates the "Attack" tab under the "ActiveBase" tab under the "Search & Attack" tab under the "Attack Plan" tab
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
Global $g_hCmbABAlgorithm = 0, $g_hCmbABSelectTroop = 0, $g_hChkABKingAttack = 0, $g_hChkABQueenAttack = 0, $g_hChkABWardenAttack = 0, $g_hChkABDropCC = 0

Global $g_hGrpABAttack = 0, $g_hPicABKingAttack = 0, $g_hPicABQueenAttack = 0, $g_hPicABWardenAttack = 0, $g_hPicABDropCC = 0

Global $g_hCmbABSiege = 0, $g_hCmbABWardenMode = 0, $g_hChkABChampionAttack = 0, $g_hPicABChampionAttack = 0
Global $g_hChkABPrinceAttack = 0, $g_hPicABPrinceAttack = 0
Global $g_hChkABDragonDukeAttack = 0, $g_hPicABDragonDukeAttack = 0

Func CreateAttackSearchActiveBaseAttack()
	Local $sTxtTip = ""
	Local $x = 25, $y = 40
	$g_hGrpABAttack = GUICtrlCreateGroup(GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Group_01", "Attack Mode"), $x - 20, $y - 15, 146, 182)
	$x -= 15
	$y += 2
	$g_hCmbABAlgorithm = GUICtrlCreateCombo("", $x, $y, 135, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	_GUICtrlSetTip(-1, "")
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_01", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_02", -1), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Algorithm_Item_01", -1))
	GUICtrlSetOnEvent(-1, "cmbABAlgorithm")

	$y += 27
	$g_hCmbABSelectTroop = GUICtrlCreateCombo("", $x, $y, 135, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_01", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_02", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_03", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_04", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_05", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_06", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_07", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_08", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_09", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_10", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_11", -1), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Item_01", -1))
	_GUICtrlSetTip(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-SelectTroop_Info_01", -1))

	$y += 27
	$g_hPicABKingAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnKing, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-King_Info_01", -1) & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-King_Info_02", -1)
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABKingAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$x += 46
	$g_hPicABQueenAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnQueen, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Queen_Info_01", -1) & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Queen_Info_02", -1)
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABQueenAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$x += 46
	$g_hPicABPrinceAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnPrince, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Prince_Info_01", -1) & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Prince_Info_02", -1)
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABPrinceAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$y += 27
	$x -= 92
	$g_hPicABWardenAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnWarden, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Warden_Info_01", -1) & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Warden_Info_02", -1)
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABWardenAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)
	GUICtrlSetOnEvent(-1, "chkABWardenAttack")

	$x += 46
	$g_hCmbABWardenMode = GUICtrlCreateCombo("", $x, $y, 90, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_01", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_02", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_03", -1), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Item_03", -1))
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-WardenMode_Tip", -1)
	_GUICtrlSetTip(-1, $sTxtTip)

	$y += 27
	$x -= 46
	$g_hPicABChampionAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnChampion, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Champion_Info_01", -1) & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Champion_Info_02", -1)
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABChampionAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$x += 46
	$g_hPicABDragonDukeAttack = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnDragonDuke, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-DragonDuke_Info_01", "Use your Dragon Duke when Attacking...") & @CRLF & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-DragonDuke_Info_02", "Enabled with TownHall 15 and higher")
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABDragonDukeAttack = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)

	$y += 27
	$x -= 46
	$g_hPicABDropCC = _GUICtrlCreateIcon($g_sLibIconPath, $eIcnCC, $x, $y, 24, 24)
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Chk-Use-Clan Castle_Info_01", -1)
	_GUICtrlSetTip(-1, $sTxtTip)
	$g_hChkABDropCC = GUICtrlCreateCheckbox("", $x + 27, $y, 17, 17)
	_GUICtrlSetTip(-1, $sTxtTip)
	GUICtrlSetOnEvent(-1, "chkABDropCC")

	$x += 46
	$g_hCmbABSiege = GUICtrlCreateCombo("", $x, $y, 90, 25, BitOR($CBS_DROPDOWNLIST, $CBS_AUTOHSCROLL))
	GUICtrlSetData(-1, GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_01", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_02", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_03", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_04", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_07", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_08", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_09", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_10", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_11", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_05", -1) & "|" & _
			GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_06", -1), GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Item_06", -1))
	$sTxtTip = GetTranslatedFileIni("MBR GUI Design Child Attack - Attack", "Cmb-Siege_Tip", -1)
	_GUICtrlSetTip(-1, $sTxtTip)

	GUICtrlCreateGroup("", -99, -99, 1, 1)
EndFunc   ;==>CreateAttackSearchActiveBaseAttack

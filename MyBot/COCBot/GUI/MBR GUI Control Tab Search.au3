; #FUNCTION# ====================================================================================================================
; Name ..........: MBR GUI Control
; Description ...: This file Includes all functions to current GUI
; Syntax ........:
; Parameters ....: None
; Return values .: None
; Author ........: GkevinOD (2014)
; Modified ......: Hervidero (2015), CodeSlinger69 [2017], MonkeyHunter (03-2017)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================
#include-once

Func cmbDBGoldElixir()
	If _GUICtrlComboBox_GetCurSel($g_hCmbDBMeetGE) < 2 Then
		GUICtrlSetState($g_hTxtDBMinGold, $GUI_SHOW)
		GUICtrlSetState($g_hPicDBMinGold, $GUI_SHOW)
		GUICtrlSetState($g_hTxtDBMinElixir, $GUI_SHOW)
		GUICtrlSetState($g_hPicDBMinElixir, $GUI_SHOW)
		GUICtrlSetState($g_hTxtDBMinGoldPlusElixir, $GUI_HIDE)
		GUICtrlSetState($g_hPicDBMinGPEGold, $GUI_HIDE)
	Else
		GUICtrlSetState($g_hTxtDBMinGold, $GUI_HIDE)
		GUICtrlSetState($g_hPicDBMinGold, $GUI_HIDE)
		GUICtrlSetState($g_hTxtDBMinElixir, $GUI_HIDE)
		GUICtrlSetState($g_hPicDBMinElixir, $GUI_HIDE)
		GUICtrlSetState($g_hTxtDBMinGoldPlusElixir, $GUI_SHOW)
		GUICtrlSetState($g_hPicDBMinGPEGold, $GUI_SHOW)
	EndIf
EndFunc   ;==>cmbDBGoldElixir

Func chkDBMeetDE()
	_GUICtrlEdit_SetReadOnly($g_hTxtDBMinDarkElixir, GUICtrlRead($g_hChkDBMeetDE) = $GUI_CHECKED ? False : True)
EndFunc   ;==>chkDBMeetDE

Func chkDBMeetTrophy()
	_GUICtrlEdit_SetReadOnly($g_hTxtDBMinTrophy, GUICtrlRead($g_hChkDBMeetTrophy) = $GUI_CHECKED ? False : True)
	_GUICtrlEdit_SetReadOnly($g_hTxtDBMaxTrophy, GUICtrlRead($g_hChkDBMeetTrophy) = $GUI_CHECKED ? False : True)
EndFunc   ;==>chkDBMeetTrophy

Func chkDBMeetTH()
	GUICtrlSetState($g_hCmbDBTH, GUICtrlRead($g_hChkDBMeetTH) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
EndFunc   ;==>chkDBMeetTH

Func chkDBMeetDeadEagle()
	If GUICtrlRead($g_hChkDBMeetDeadEagle) = $GUI_CHECKED Then
		$g_bChkDeadEagle = True
		$g_iDeadEagleSearch = GUICtrlRead($g_hTxtDeadEagleSearch)
	Else
		$g_bChkDeadEagle = False
	EndIf

	SetLog("$g_bChkDeadEagle :" & $g_bChkDeadEagle)
EndFunc

Func chkDBWeakBase()
	GUICtrlSetState($g_ahCmbWeakMortar[$DB], GUICtrlRead($g_ahChkMaxMortar[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakWizTower[$DB], GUICtrlRead($g_ahChkMaxWizTower[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakAirDefense[$DB], GUICtrlRead($g_ahChkMaxAirDefense[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakXBow[$DB], GUICtrlRead($g_ahChkMaxXBow[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakInferno[$DB], GUICtrlRead($g_ahChkMaxInferno[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakEagle[$DB], GUICtrlRead($g_ahChkMaxEagle[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakScatter[$DB], GUICtrlRead($g_ahChkMaxScatter[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakMonolith[$DB], GUICtrlRead($g_ahChkMaxMonolith[$DB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
EndFunc   ;==>chkDBWeakBase

Func cmbABGoldElixir()
	If _GUICtrlComboBox_GetCurSel($g_hCmbABMeetGE) < 2 Then
		GUICtrlSetState($g_hTxtABMinGold, $GUI_SHOW)
		GUICtrlSetState($g_hPicABMinGold, $GUI_SHOW)
		GUICtrlSetState($g_hTxtABMinElixir, $GUI_SHOW)
		GUICtrlSetState($g_hPicABMinElixir, $GUI_SHOW)
		GUICtrlSetState($g_hTxtABMinGoldPlusElixir, $GUI_HIDE)
		GUICtrlSetState($g_hPicABMinGPEGold, $GUI_HIDE)
	Else
		GUICtrlSetState($g_hTxtABMinGold, $GUI_HIDE)
		GUICtrlSetState($g_hPicABMinGold, $GUI_HIDE)
		GUICtrlSetState($g_hTxtABMinElixir, $GUI_HIDE)
		GUICtrlSetState($g_hPicABMinElixir, $GUI_HIDE)
		GUICtrlSetState($g_hTxtABMinGoldPlusElixir, $GUI_SHOW)
		GUICtrlSetState($g_hPicABMinGPEGold, $GUI_SHOW)
	EndIf
EndFunc   ;==>cmbABGoldElixir

Func chkABMeetDE()
	_GUICtrlEdit_SetReadOnly($g_hTxtABMinDarkElixir, GUICtrlRead($g_hChkABMeetDE) = $GUI_CHECKED ? False : True)
EndFunc   ;==>chkABMeetDE

Func chkABMeetTrophy()
	_GUICtrlEdit_SetReadOnly($g_hTxtABMinTrophy, GUICtrlRead($g_hChkABMeetTrophy) = $GUI_CHECKED ? False : True)
	_GUICtrlEdit_SetReadOnly($g_hTxtABMaxTrophy, GUICtrlRead($g_hChkABMeetTrophy) = $GUI_CHECKED ? False : True)
EndFunc   ;==>chkABMeetTrophy

Func chkABMeetTH()
	GUICtrlSetState($g_hCmbABTH, GUICtrlRead($g_hChkABMeetTH) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
EndFunc   ;==>chkABMeetTH

Func chkABWeakBase()
	GUICtrlSetState($g_ahCmbWeakMortar[$LB], GUICtrlRead($g_ahChkMaxMortar[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakWizTower[$LB], GUICtrlRead($g_ahChkMaxWizTower[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakAirDefense[$LB], GUICtrlRead($g_ahChkMaxAirDefense[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakXBow[$LB], GUICtrlRead($g_ahChkMaxXBow[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakInferno[$LB], GUICtrlRead($g_ahChkMaxInferno[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakEagle[$LB], GUICtrlRead($g_ahChkMaxEagle[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakScatter[$LB], GUICtrlRead($g_ahChkMaxScatter[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
	GUICtrlSetState($g_ahCmbWeakMonolith[$LB], GUICtrlRead($g_ahChkMaxMonolith[$LB]) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
EndFunc   ;==>chkABWeakBase

Func chkRestartSearchLimit()
	GUICtrlSetState($g_hTxtRestartSearchlimit, GUICtrlRead($g_hChkRestartSearchLimit) = $GUI_CHECKED ? $GUI_ENABLE : $GUI_DISABLE)
EndFunc   ;==>chkRestartSearchLimit

Func chkEnableRankedBattle()
	; No additional controls to enable/disable
EndFunc   ;==>chkEnableRankedBattle

Func chkEnableRevengeBattle()
	$g_bEnableRevengeBattle = (GUICtrlRead($g_hChkEnableRevengeBattle) = $GUI_CHECKED)
EndFunc   ;==>chkEnableRevengeBattle

Func chkRankedBattleWaitForCastle()
	$g_bSearchCastleWaitEnable = (GUICtrlRead($g_hChkRankedBattleWaitForCastle) = $GUI_CHECKED)
	; Save automatically
	IniWrite($g_sProfileConfigPath, "search", "ChkCastleWait", $g_bSearchCastleWaitEnable ? 1 : 0)
EndFunc   ;==>chkRankedBattleWaitForCastle

Func chkDBActivateSearches()
	If GUICtrlRead($g_hChkDBActivateSearches) = $GUI_CHECKED Then
		GUICtrlSetState($g_hTxtDBSearchesMin, $GUI_ENABLE)
		GUICtrlSetState($g_hLblDBSearches, $GUI_ENABLE)
		GUICtrlSetState($g_hTxtDBSearchesMax, $GUI_ENABLE)
	Else
		GUICtrlSetState($g_hTxtDBSearchesMin, $GUI_DISABLE)
		GUICtrlSetState($g_hLblDBSearches, $GUI_DISABLE)
		GUICtrlSetState($g_hTxtDBSearchesMax, $GUI_DISABLE)
	EndIf

	dbCheckall()
EndFunc   ;==>chkDBActivateSearches

Func chkDBActivateTropies()
	If GUICtrlRead($g_hChkDBActivateTrophies) = $GUI_CHECKED Then
		GUICtrlSetState($g_hTxtDBTrophiesMin, $GUI_ENABLE)
		GUICtrlSetState($g_hLblDBTrophies, $GUI_ENABLE)
		GUICtrlSetState($g_hTxtDBTrophiesMax, $GUI_ENABLE)
	Else
		GUICtrlSetState($g_hTxtDBTrophiesMin, $GUI_DISABLE)
		GUICtrlSetState($g_hLblDBTrophies, $GUI_DISABLE)
		GUICtrlSetState($g_hTxtDBTrophiesMax, $GUI_DISABLE)
	EndIf

	dbCheckall()
EndFunc   ;==>chkDBActivateTropies

Func chkDBActivateCamps()
	If GUICtrlRead($g_hChkDBActivateCamps) = $GUI_CHECKED Then
		GUICtrlSetState($g_hLblDBArmyCamps, $GUI_ENABLE)
		GUICtrlSetState($g_hTxtDBArmyCamps, $GUI_ENABLE)
	Else
		GUICtrlSetState($g_hLblDBArmyCamps, $GUI_DISABLE)
		GUICtrlSetState($g_hTxtDBArmyCamps, $GUI_DISABLE)
	EndIf

	dbCheckall()
EndFunc   ;==>chkDBActivateCamps

Func EnableSearchPanels($iMatchMode)
	Switch $iMatchMode
		Case $DB
			If GUICtrlRead($g_hChkDBActivateSearches) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBActivateTrophies) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBActivateCamps) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBKingWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBQueenWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBPrinceWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBWardenWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBChampionWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkDBNotWaitHeroes) = $GUI_CHECKED Then

				_GUI_Value_STATE("SHOW", $groupHerosDB)
				_GUI_Value_STATE("SHOW", $g_aGroupSearchDB)
				_GUI_Value_STATE("SHOW", $groupSpellsDB)

				cmbDBGoldElixir()
			Else
				_GUI_Value_STATE("HIDE", $groupHerosDB)
				_GUI_Value_STATE("HIDE", $g_aGroupSearchDB)
				_GUI_Value_STATE("HIDE", $groupSpellsDB)
			EndIf
		Case $LB
			If GUICtrlRead($g_hChkABActivateSearches) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABActivateTrophies) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABActivateCamps) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABKingWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABQueenWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABPrinceWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABWardenWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABChampionWait) = $GUI_CHECKED Or _
			   GUICtrlRead($g_hChkABNotWaitHeroes) = $GUI_CHECKED Then

				_GUI_Value_STATE("SHOW", $groupHerosAB)
				_GUI_Value_STATE("SHOW", $groupSearchAB)
				_GUI_Value_STATE("SHOW", $groupSpellsAB)

				cmbABGoldElixir()
			Else
				_GUI_Value_STATE("HIDE", $groupHerosAB)
				_GUI_Value_STATE("HIDE", $groupSearchAB)
				_GUI_Value_STATE("HIDE", $groupSpellsAB)
			EndIf
	EndSwitch

EndFunc   ;==>EnableSearchPanels




Func chkABActivateSearches()
	If GUICtrlRead($g_hChkABActivateSearches) = $GUI_CHECKED Then
		GUICtrlSetState($g_hTxtABSearchesMin, $GUI_ENABLE)
		GUICtrlSetState($g_hLblABSearches, $GUI_ENABLE)
		GUICtrlSetState($g_hTxtABSearchesMax, $GUI_ENABLE)
	Else
		GUICtrlSetState($g_hTxtABSearchesMin, $GUI_DISABLE)
		GUICtrlSetState($g_hLblABSearches, $GUI_DISABLE)
		GUICtrlSetState($g_hTxtABSearchesMax, $GUI_DISABLE)
	EndIf
	;EnableSearchPanels($LB)
	abCheckall()
EndFunc   ;==>chkABActivateSearches

Func chkABActivateTropies()
	If GUICtrlRead($g_hChkABActivateTrophies) = $GUI_CHECKED Then
		GUICtrlSetState($g_hTxtABTrophiesMin, $GUI_ENABLE)
		GUICtrlSetState($g_hLblABTrophies, $GUI_ENABLE)
		GUICtrlSetState($g_hTxtABTrophiesMax, $GUI_ENABLE)
	Else
		GUICtrlSetState($g_hTxtABTrophiesMin, $GUI_DISABLE)
		GUICtrlSetState($g_hLblABTrophies, $GUI_DISABLE)
		GUICtrlSetState($g_hTxtABTrophiesMax, $GUI_DISABLE)
	EndIf
	;EnableSearchPanels($LB)
	abCheckall()
EndFunc   ;==>chkABActivateTropies

Func chkABActivateCamps()
	If GUICtrlRead($g_hChkABActivateCamps) = $GUI_CHECKED Then
		GUICtrlSetState($g_hLblABArmyCamps, $GUI_ENABLE)
		GUICtrlSetState($g_hTxtABArmyCamps, $GUI_ENABLE)
		;_GUI_Value_STATE("SHOW", $groupSearchAB)
		;cmbABGoldElixir()
		;_GUI_Value_STATE("SHOW", $groupHerosAB)
	Else
		GUICtrlSetState($g_hLblABArmyCamps, $GUI_DISABLE)
		GUICtrlSetState($g_hTxtABArmyCamps, $GUI_DISABLE)
		;_GUI_Value_STATE("HIDE", $groupSearchAB)
		;_GUI_Value_STATE("HIDE", $groupHerosAB)
	EndIf
	;EnableSearchPanels($LB)
	abCheckall()
EndFunc   ;==>chkABActivateCamps

Func chkDBKingWait()
	If $g_iTownHallLevel > 6 Or $g_iTownHallLevel = 0 Then ; Must be TH7 or above to have King
		_GUI_Value_STATE("ENABLE", $g_hChkDBKingWait & "#" & $g_hChkDBKingAttack)
	Else
		GUICtrlSetState($g_hChkDBKingWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkDBKingAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkDBKingWait

Func chkDBQueenWait()
	If $g_iTownHallLevel > 7 Or $g_iTownHallLevel = 0 Then ; Must be TH8 or above to have Queen
		_GUI_Value_STATE("ENABLE", $g_hChkDBQueenWait & "#" & $g_hChkDBQueenAttack)
	Else
		GUICtrlSetState($g_hChkDBQueenWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkDBQueenAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkDBQueenWait

Func chkDBPrinceWait()
	If $g_iTownHallLevel > 8 Or $g_iTownHallLevel = 0 Then ; Must be TH9 or above to have Prince
		_GUI_Value_STATE("ENABLE", $g_hChkDBPrinceWait & "#" & $g_hChkDBPrinceAttack)
	Else
		GUICtrlSetState($g_hChkDBPrinceWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkDBPrinceAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkDBPrinceWait

Func chkDBWardenWait()
	If $g_iTownHallLevel > 10 Or $g_iTownHallLevel = 0 Then ; Must be TH11 to have warden
		_GUI_Value_STATE("ENABLE", $g_hChkDBWardenWait & "#" & $g_hChkDBWardenAttack)
	Else
		GUICtrlSetState($g_hChkDBWardenWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkDBWardenAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkDBWardenWait

Func chkDBChampionWait()
	If $g_iTownHallLevel > 12 Or $g_iTownHallLevel = 0 Then ; Must be TH13 to have Champion
		_GUI_Value_STATE("ENABLE", $g_hChkDBChampionWait & "#" & $g_hChkDBChampionAttack)
	Else
		GUICtrlSetState($g_hChkDBChampionWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkDBChampionAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkDBChampionWait

Func chkABKingWait()
	If $g_iTownHallLevel > 6 Or $g_iTownHallLevel = 0 Then ; Must be TH7 or above to have King
		_GUI_Value_STATE("ENABLE", $g_hChkABKingWait & "#" & $g_hChkABKingAttack)
	Else
		GUICtrlSetState($g_hChkABKingWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkABKingAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkABKingWait

Func chkABQueenWait()
	If $g_iTownHallLevel > 7 Or $g_iTownHallLevel = 0 Then ; Must be TH8 or above to have Queen
		_GUI_Value_STATE("ENABLE", $g_hChkABQueenWait & "#" & $g_hChkABQueenAttack)
	Else
		GUICtrlSetState($g_hChkABQueenWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkABQueenAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkABQueenWait

Func chkABPrinceWait()
	If $g_iTownHallLevel > 8 Or $g_iTownHallLevel = 0 Then ; Must be TH9 or above to have Prince
		_GUI_Value_STATE("ENABLE", $g_hChkABPrinceWait & "#" & $g_hChkABPrinceAttack)
	Else
		GUICtrlSetState($g_hChkABPrinceWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkABPrinceAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkABPrinceWait

Func chkABWardenWait()
	If $g_iTownHallLevel > 10 Or $g_iTownHallLevel = 0 Then ; Must be TH11 to have warden
		_GUI_Value_STATE("ENABLE", $g_hChkABWardenWait & "#" & $g_hChkABWardenAttack)
	Else
		GUICtrlSetState($g_hChkABWardenWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkABWardenAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkABWardenWait

Func chkABChampionWait()
	If $g_iTownHallLevel > 12 Or $g_iTownHallLevel = 0 Then ; Must be TH13 to have Champion
		_GUI_Value_STATE("ENABLE", $g_hChkABChampionWait & "#" & $g_hChkABChampionAttack)
	Else
		GUICtrlSetState($g_hChkABChampionWait, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
		GUICtrlSetState($g_hChkABChampionAttack, BitOR($GUI_DISABLE, $GUI_UNCHECKED))
	EndIf
EndFunc   ;==>chkABChampionWait






Func CmbDBTH()
	_GUI_Value_STATE("HIDE", $g_aGroupListPicDBMaxTH)
	Local $iCmbValue = _GUICtrlComboBox_GetCurSel($g_hCmbDBTH) + 6
	GUICtrlSetState($g_ahPicDBMaxTH[$iCmbValue], $GUI_SHOW)
EndFunc   ;==>CmbDBTH

Func CmbABTH()
	_GUI_Value_STATE("HIDE", $g_aGroupListPicABMaxTH)
	Local $iCmbValue = _GUICtrlComboBox_GetCurSel($g_hCmbABTH) + 6
	GUICtrlSetState($g_ahPicABMaxTH[$iCmbValue], $GUI_SHOW)
EndFunc   ;==>CmbABTH

Func CmbBullyMaxTH()
	_GUI_Value_STATE("HIDE", $g_aGroupListPicBullyMaxTH)
	Local $iCmbValue = _GUICtrlComboBox_GetCurSel($g_hCmbBullyMaxTH) + 6
	GUICtrlSetState($g_ahPicBullyMaxTH[$iCmbValue], $GUI_SHOW)
EndFunc   ;==>CmbBullyMaxTH

Func dbCheckAll()
	If BitAND(GUICtrlRead($g_hChkDBActivateSearches), GUICtrlRead($g_hChkDBActivateTrophies), GUICtrlRead($g_hChkDBActivateCamps)) = $GUI_UNCHECKED Then
		GUICtrlSetState($g_hChkDeadbase, $GUI_UNCHECKED)
	Else
		GUICtrlSetState($g_hChkDeadbase, $GUI_CHECKED)
	EndIf
	tabSEARCH()
EndFunc   ;==>dbCheckAll

Func abCheckAll()
	If BitAND(GUICtrlRead($g_hChkABActivateSearches), GUICtrlRead($g_hChkABActivateTrophies), GUICtrlRead($g_hChkABActivateCamps)) = $GUI_UNCHECKED Then
		GUICtrlSetState($g_hChkActivebase, $GUI_UNCHECKED)
	Else
		GUICtrlSetState($g_hChkActivebase, $GUI_CHECKED)
	EndIf
	tabSEARCH()
EndFunc   ;==>abCheckAll

Func chkNotWaitHeroes()
	If $g_abAttackTypeEnable[$DB] Then $g_iSearchNotWaitHeroesEnable = $g_aiSearchNotWaitHeroesEnable[$DB]
	If $g_abAttackTypeEnable[$LB] Then
		If $g_iSearchNotWaitHeroesEnable <> 0 Then $g_iSearchNotWaitHeroesEnable = $g_aiSearchNotWaitHeroesEnable[$LB]
	EndIf
EndFunc   ;==>ChkNotWaitHeroes

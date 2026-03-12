; #FUNCTION# ====================================================================================================================
; Name ..........: PrepareSearch
; Description ...: Goes into searching for a match, breaks shield if it has to
; Syntax ........: PrepareSearch()
; Parameters ....:
; Return values .: None
; Author ........: Code Monkey #4
; Modified ......: KnowJack (Aug 2015), MonkeyHunter(2015-12)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================
#include "..\MOD\RankedBattle.au3"
#include "..\MOD\RevengeBattle.au3"

Func PrepareSearch($Mode = $DB) ;Click attack button and find match button, will break shield

	SetLog("» GOING TO ATTACK «", $COLOR_INFO)

	; RestartSearchPickupHero - Check Remaining Heal Time
	If $g_bSearchRestartPickupHero And $Mode <> $DT Then
		Local $pTroopType[$eHeroCount] = [$eKing, $eQueen, $ePrince, $eWarden, $eChampion, $eDragonDuke]
		For $i = 0 To $eHeroSlots - 1 ; check slots
			For $pMatchMode = $DB To $g_iModeCount - 1 ; check all attack modes
				If IsUnitUsed($pMatchMode, $pTroopType[$g_aiCmbCustomHeroOrder[$i]]) Then
					If Not _DateIsValid($g_asHeroHealTime[$i]) Then
						getArmyHeroTime("All", True, True)
						ExitLoop 2
					EndIf
				EndIf
			Next
		Next
	EndIf

	ChkAttackCSVConfig()

	; === REVENGE BATTLE ===
	Local $bRevengeBattle = False
	If $g_bEnableRevengeBattle Then
		$bRevengeBattle = JoinRevengeBattle()
	EndIf

	If Not $bRevengeBattle And IsMainPage() Then
		; === NORMAL ATTACK FLOW ===
		If _Sleep($DELAYTREASURY4) Then Return
			If _CheckPixel($aAttackForTreasury, $g_bCapturePixel, Default, "Is attack for treasury:") Then
			SetLog("It isn't attack for Treasury:-(", $COLOR_SUCCESS)
			Return
		EndIf
		If _Sleep($DELAYTREASURY4) Then Return
		
		Local $aAttack = findButton("AttackButton", Default, 1, True)
		Local $AttackCoordsX[2] = [45, 85]
		Local $AttackCoordsY[2] = [590 + $g_iBottomOffsetY, 625 + $g_iBottomOffsetY]
		Local $AttackButtonClickXY[2] = [Random($AttackCoordsX[0], $AttackCoordsX[1], 1), Random($AttackCoordsY[0], $AttackCoordsY[1], 1)]
		
		If IsArray($aAttack) And UBound($aAttack, 1) = 2 Then
			ClickP($AttackButtonClickXY, 1, 130, "#0149")
		Else
			Local $aRescueAttack = findButton("RescueATKButton", Default, 1, True)
			If IsArray($aRescueAttack) And UBound($aRescueAttack, 1) = 2 Then
				ClickP($AttackButtonClickXY, 1, 130, "#0149")
			Else
				SetLog("Couldn't find the Attack Button!", $COLOR_ERROR)
				If $g_bDebugImageSave Then SaveDebugImage("AttackButtonNotFound")
				Return
			EndIf
		EndIf

		If _Sleep($DELAYPREPARESEARCH1) Then Return

		Local $bRankedBattle = False
		If $g_bEnableRankedBattle Then
			$bRankedBattle = JoinRankedBattle()
		EndIf

		$g_bCloudsActive = False ; early set of clouds to ensure no android suspend occurs that might cause infinite waits

		If Not $bRankedBattle Then
			; ========================================================================
		  ; 1 Yellow "Find a Match" Button
		  ; ========================================================================
			Local $iYelX = Random(140, 200, 1)
			Local $iYelY = Random(480, 500, 1)
			Click($iYelX, $iYelY)
		  ; ========================================================================
		  ; 2. Green "Attack!" Button
		  ; ========================================================================
			If _Sleep(1500) Then Return ; Wait for popup to appear
			; Range: X(655 to 800), Y(521 to 554)
			Local $iGrnX = Random(700, 770, 1)
			Local $iGrnY = Random(530, 540, 1)
			Click($iGrnX, $iGrnY)
			_Sleep(1000) ; Wait for clouds
			; ========================================================================
		EndIf
	EndIf

	;If $g_iTownHallLevel <> "" And $g_iTownHallLevel > 0 Then
	;	$g_iSearchCost += $g_aiSearchCost[$g_iTownHallLevel - 1]
	;	$g_iStatsTotalGain[$eLootGold] -= $g_aiSearchCost[$g_iTownHallLevel - 1]
	;EndIf

	;UpdateStats()
	;If _Sleep($DELAYPREPARESEARCH2) Then Return

	;If isGemOpen(True) Then ; Check for gem window open)
	;	SetLog(" Not enough gold to start searching!", $COLOR_ERROR)
	;	If _Sleep($DELAYPREPARESEARCH1) Then Return
	;	CloseWindow() ; Click close attack window "X"
	;	If _Sleep($DELAYPREPARESEARCH1) Then Return
	;	$g_bOutOfGold = True ; Set flag for out of gold to search for attack
	;EndIf

	SetDebugLog("PrepareSearch exit check $g_bRestart= " & $g_bRestart & ", $g_bOutOfGold= " & $g_bOutOfGold, $COLOR_DEBUG)

	If $g_bRestart Or $g_bOutOfGold Then ; If we have one or both errors, then return
		$g_bIsClientSyncError = False ; reset fast restart flag to stop OOS mode, collecting resources etc.
		Return
	EndIf

	;If IsAttackWhileShieldPage(False) Then ; check for shield window and then button to lose time due attack and click okay
	;	Local $aiOkayButton = findButton("Okay", Default, 1, True)
	;	If IsArray($aiOkayButton) And UBound($aiOkayButton, 1) = 2 Then ClickP($aiOkayButton, 1, 120, "#0153") ; Click Okay Button
	;	If _Sleep($DELAYPREPARESEARCH3) Then Return
	;EndIf

 Return True ; Continue with attack
EndFunc   ;==>PrepareSearch

Func OkayLegend()
	Local $aOkayAttackButton
	$aOkayAttackButton = findButton("Okay", Default, 1, True)
	
	If IsArray($aOkayAttackButton) And UBound($aOkayAttackButton, 1) = 2 Then
		ClickP($aOkayAttackButton, 1, 120)
		Return True
	EndIf

	Return False
EndFunc   ;==>OkayLegend

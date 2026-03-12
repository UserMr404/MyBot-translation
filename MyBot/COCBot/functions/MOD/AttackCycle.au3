; ===============================================================================================================================
; ===================================================== ATTACK CYCLE MODULE =====================================================
; ===============================================================================================================================
; This module handles the execution of attack cycles, including initial and routine attacks.
; It manages various bot activities during cycles for efficient operation.
; ===============================================================================================================================

; #FUNCTION# ====================================================================================================================
; Name ..........: AttackCycle
; Description ...: Executes the initial or routine attack cycle with resource and activity management
; Syntax ........: AttackCycle($bIsInitial = False)
; Parameters ....: $bIsInitial - True for initial cycle, False for routine
; Author ........: Phael
; Remarks .......: This function performs a series of attacks with troop requests, donations, upgrades, and attacks
; Related .......: AttackMain, CakeCC, RequestCC, DonateCC, UpgradeBuilding, AutoUpgrade, UpgradeWall
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: AttackCycle(True)
; ===============================================================================================================================
Func AttackCycle($bIsInitial = False)
	; === EARLY EXIT CHECK ===
	If Not $g_bRunState Then Return

	; === CYCLE INITIALIZATION ===
	Local $iPerformed = 0
	Local $iAttackCount = ProfileSwitchAccountEnabled() ? ($g_iCmbMaxInARow + 1) : $INITIAL_ATTACK_COUNT
	SetLog("» STARTING ATTACK CYCLE «", $COLOR_SUCCESS)

	; === MAIN ATTACK LOOP ===
	; Loop until the desired number of performed attacks is reached
	Local $iAttempt = 0
	While $iPerformed < $iAttackCount
		SetLog("Attack Sequence: " & ($iPerformed + 1) & "/" & $iAttackCount, $COLOR_ACTION)

		; === ZOOM OUT ===
		ClearScreen()
		ZoomOut()

		; === TROOP REQUEST HANDLING ===
		If $g_bRequestTroopsEnable Then
			RequestCC()
			If _Sleep(500) Then Return
		EndIf

		; === DONATION HANDLING ===
		If $g_bChkDonate Then
			DonateCC()
			If _Sleep(500) Then Return
		EndIf

		; === AUTO UPGRADE HANDLING ===
		If $g_bAutoUpgradeEnabled And $g_iFreeBuilderCount > 0 Then
			AutoUpgrade()
			If _Sleep(500) Then Return
		EndIf
		
		; === WALL UPGRADE HANDLING ===
		If $g_bAutoUpgradeWallsEnable And $g_iFreeBuilderCount > 0 Then
			UpgradeWall()
			If _Sleep(500) Then Return
		EndIf

		; === CLAN CASTLE WAIT CHECK ===
		If $g_bSearchCastleWaitEnable Then
			; Open Army overview to check CC status
			If Not OpenArmyOverview() Then
				SetLog("Failed to open army overview!", $COLOR_ERROR)
			Else
				If Not IsFullClanCastle() Then
					SetLog("Waiting for troops before attacking", $COLOR_ACTION)
					CloseWindow()
					If _Sleep(500) Then Return
					Local $iWaitCount = 0
					Local $iMaxWait = 60 ; Wait up to 15 minutes (60 * 15 seconds = 900 seconds)
					While Not IsFullClanCastle() And $iWaitCount < $iMaxWait
						If Not $g_bRunState Then Return
						
						; Donate troops while waiting
						If $g_bChkDonate Then
							DonateCC()
							If _Sleep(500) Then Return
						EndIf
						If _Sleep(15000) Then Return ; Wait 15 seconds
						$iWaitCount += 1
						If Mod($iWaitCount, 4) = 0 Then ; Update status every minute (4 * 15s = 60s)
							SetLog("Still waiting for troops (" & Floor($iWaitCount / 4) & " min elapsed)", $COLOR_ACTION)
						EndIf
						
						; Reopen army window to check CC status
						If Not OpenArmyOverview() Then
							SetLog("Failed to reopen army overview", $COLOR_ERROR)
							ExitLoop
						EndIf
						
						; Check if CC is now full
						If IsFullClanCastle() Then
							SetLog("Clan Castle is full, ready to attack!", $COLOR_SUCCESS)
							CloseWindow()
							If _Sleep(500) Then Return
							ExitLoop
						EndIf
						
						; Close window to continue donating
						CloseWindow()
						If _Sleep(500) Then Return
					WEnd
					If $iWaitCount >= $iMaxWait Then
						SetLog("Maximum wait time reached, attacking anyway", $COLOR_WARNING)
					EndIf
				Else
					CloseWindow()
					If _Sleep(500) Then Return
				EndIf
			EndIf
			If Not $g_bRunState Then Return
		EndIf
		
		; === ATTACK EXECUTION ===
		AttackMain()

		; Track performed attacks
		If $g_bAttackPerformed Then $iPerformed += 1
		$g_bAttackPerformed = False ; Reset for next attack

		; === SEQUENCE MANAGEMENT ===
		If $iPerformed < $iAttackCount Then
			If SmartPause() Then ExitLoop
			If $g_bRestart Then $g_bRestart = False
			Local $iWaitTime = Random($g_iAttackDelayMin, $g_iAttackDelayMax, 1)
			SetLog("Waiting " & Round($iWaitTime / 1000) & " seconds before next attack", $COLOR_INFO)
			If _Sleep($iWaitTime) Then Return
		Else
			SetLog("» ATTACK CYCLE COMPLETED (" & $iPerformed & "/" & $iAttackCount & ") «", $COLOR_SUCCESS)
			ExitLoop
		EndIf

		; === CRITICAL RESOURCE CHECK ===
		If $g_bOutOfGold Then
			SetLog("Switching To Halt Attack, Stay Online/Collect Mode", $COLOR_ERROR)
			$g_bFirstStart = True ; Reset First time flag to ensure army balancing when returns to training
			Return
		EndIf
		If _Sleep($DELAYRUNBOT1) Then Return
		$iAttempt += 1
	WEnd

	; === POST-ATTACK CYCLE CHECKS ===
	If ($g_aiAttackedCount - $g_aiAttackedCountSwitch[$g_iCurAccount] >= $g_iCmbMaxInARow) Or Not ProfileSwitchAccountEnabled() Then
		If ($g_bChkCollectBuilderBase Or $g_bChkStartClockTowerBoost Or $g_iChkBBSuggestedUpgrades Or $g_bChkEnableBBAttack) Then
			BuilderBase()
		EndIf
		If ProfileSwitchAccountEnabled() Then 
			checkSwitchAcc()
		EndIf
	EndIf
EndFunc   ;==>AttackCycle
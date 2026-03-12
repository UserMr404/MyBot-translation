; ===============================================================================================================================
; ======================================================== BB SPAM MODULE =======================================================
; ===============================================================================================================================
; This module handles Builder Base spam attacks, continuously executing attacks and monitoring resources.
; It includes safety checks to prevent infinite loops and resource management.
; ===============================================================================================================================

; #FUNCTION# ====================================================================================================================
; Name ..........: BBSpamCycle
; Description ...: Main loop function for BB Spam mode with resource monitoring
; Syntax ........: BBSpamCycle()
; Author ........: Phael
; Remarks .......: Executes BuilderBase() and checks for max resources after each cycle with safety limits
; Related .......: IsBBResourcesMaxed(), BuilderBase(), ToggleBBSpam()
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: BBSpamCycle()
; ===============================================================================================================================
Func BBSpamCycle()
	; === EARLY EXIT CHECK ===
	If Not $g_bBBSpamEnabled Then Return

	; === VALIDATION ===
	If Not $g_bRunState Then
		DisableBBSpam("Bot is not running")
		Return
	EndIf

	; === INITIALIZATION ===
	$g_bBBSpamRunning = True
	SetLog("» BB SPAM MODE ENABLED «", $COLOR_INFO)

	; === BASE SWITCHING ===
	; try switching a few times instead of giving up immediately
	Local $iSwitchAttempts = 0, $iMaxAttempts = 3
	While $iSwitchAttempts < $iMaxAttempts
		If SwitchBetweenBases(True, True) And isOnBuilderBase() Then
			ExitLoop
		EndIf
		$iSwitchAttempts += 1
		SetLog("Base switch attempt " & $iSwitchAttempts & " failed, retrying...", $COLOR_WARNING)
		Sleep(1000)
	WEnd
	
	If $iSwitchAttempts >= $iMaxAttempts Then
		DisableBBSpam("Failed to switch to Builder Base")
		Return
	EndIf
	

	; === BUILDER BASE CHECKS ===
	; BOB Control Upgrades
	If ($g_bDoubleCannonUpgrade Or $g_bArcherTowerUpgrade Or $g_bMultiMortarUpgrade Or $g_bAnyDefUpgrade Or $g_bBattleMachineUpgrade Or $g_bBattlecopterUpgrade) And $g_iFreeBuilderCountBB > 0 Then
		BOBBuildingUpgrades()
		If Not $g_bRunState Then Return
	EndIf
	
	; Suggested Upgrades
	If $g_iChkBBSuggestedUpgrades And $g_iFreeBuilderCountBB > 0 Then
		MainSuggestedUpgradeCode()
		If Not $g_bRunState Then Return
	EndIf
	
	; Star Laboratory Upgrade Check
	If $g_bAutoStarLabUpgradeEnable Then
		StarLaboratory()
		If Not $g_bRunState Then Return
	EndIf
	
	; Clock Tower Boost
	If $g_bChkStartClockTowerBoost Then
		StartClockTowerBoost()
		If Not $g_bRunState Then Return
	EndIf

	; Clear Yard Obstacles
	If $g_bChkCleanBBYard Then
		CleanBBYard()
		If Not $g_bRunState Then Return
	EndIf

	; === MAIN SPAM LOOP ===
	While $g_bBBSpamEnabled And $g_bRunState
		; Increment cycle counter
		$g_iBBSpamCycles += 1

		; === LOOT COLLECTION ===
		CollectBuilderBase(False, False, False)
		If _Sleep($DELAYRUNBOT3) Then ExitLoop

		; === RESOURCE MONITORING ===
		BuilderBaseReport(True, True)
		SetLog("BB Loot: Gold " & _NumberFormat($g_aiCurrentLootBB[$eLootGoldBB]) & ", Elixir " & _NumberFormat($g_aiCurrentLootBB[$eLootElixirBB]), $COLOR_INFO)
		If _Sleep($DELAYRUNBOT3) Then ExitLoop

		; Check if resources are full - STOP if both are full
		Local $bGoldFull = ($g_iBBSpamGoldThreshold > 0 ? ($g_aiCurrentLootBB[$eLootGoldBB] >= $g_iBBSpamGoldThreshold) : CheckBBGoldStorageFull())
		Local $bElixirFull = ($g_iBBSpamElixirThreshold > 0 ? ($g_aiCurrentLootBB[$eLootElixirBB] >= $g_iBBSpamElixirThreshold) : CheckBBElixirStorageFull())

		; === RESOURCE FULL CHECK ===
		If $bGoldFull And $bElixirFull Then
			Local $bIgnoreResources = $g_bChkBBIgnoreFullStorages
			If $g_bChkBBStarsAvailable Then
				$bIgnoreResources = $bIgnoreResources Or CheckLootAvail(False) ; Check stars without log
			EndIf
			If $bIgnoreResources Then
				SetLog("Resources maxed out, ignoring limit and continuing attacks")
			Else
				DisableBBSpam("Resources maxed out")
				ExitLoop
			EndIf
		EndIf

		; === ATTACK EXECUTION ===
		DoAttackBB()
		If Not $g_bRunState Then
			ExitLoop
		EndIf
		If checkObstacles() Then
			ExitLoop
		EndIf
		If $g_bRestart = True Then
			ExitLoop
		EndIf

		; === LOOT COLLECTION ===
		CollectBuilderBase(False, False, False)
		If _Sleep($DELAYRUNBOT3) Then ExitLoop

		; === POST-ATTACK RESOURCE UPDATE ===
		BuilderBaseReport(True, True)
		SetLog("BB Loot After Collect: Gold " & _NumberFormat($g_aiCurrentLootBB[$eLootGoldBB]) & ", Elixir " & _NumberFormat($g_aiCurrentLootBB[$eLootElixirBB]), $COLOR_INFO)
		If _Sleep($DELAYRUNBOT3) Then ExitLoop

		; === FINAL RESOURCE CHECK ===
		Local $bGoldFullAfter = ($g_iBBSpamGoldThreshold > 0 ? ($g_aiCurrentLootBB[$eLootGoldBB] >= $g_iBBSpamGoldThreshold) : CheckBBGoldStorageFull())
		Local $bElixirFullAfter = ($g_iBBSpamElixirThreshold > 0 ? ($g_aiCurrentLootBB[$eLootElixirBB] >= $g_iBBSpamElixirThreshold) : CheckBBElixirStorageFull())

		If $bGoldFullAfter And $bElixirFullAfter Then
			Local $bIgnoreResources = $g_bChkBBIgnoreFullStorages
			If $g_bChkBBStarsAvailable Then
				$bIgnoreResources = $bIgnoreResources Or CheckLootAvail(False) ; Check stars without log
			EndIf
			If $bIgnoreResources Then
				SetLog("Resources maxed out, ignoring limit and continuing attacks", $COLOR_INFO)
			Else
				DisableBBSpam("Resources maxed out")
				ExitLoop
			EndIf
		EndIf

		; === CYCLE LOGGING ===
		SetDebugLog("BBSpamCycle: Cycle #" & $g_iBBSpamCycles & " complete, starting next cycle", $COLOR_DEBUG)
	WEnd

	; === CLEANUP ===
	SwitchBetweenBases()
	checkMainScreen(False)
	$g_bBBSpamRunning = False
EndFunc   ;==>BBSpamCycle
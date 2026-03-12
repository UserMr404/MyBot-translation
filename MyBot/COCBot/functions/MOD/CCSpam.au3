; ===============================================================================================================================
; ======================================================== CC SPAM MODULE =======================================================
; ===============================================================================================================================
; This module handles Clan Castle donation spam, continuously calling DonateCC() every 30 seconds.
; It stops when donations are disabled/unconfigured, the toggle button is deactivated, or the bot stops.
; ===============================================================================================================================

; #FUNCTION# ====================================================================================================================
; Name ..........: CCSpamCycle
; Description ...: Main loop function for CC Spam mode - continuously donates troops every 30 seconds
; Syntax ........: CCSpamCycle()
; Author ........: Phael
; Remarks .......: Calls DonateCC() in a 30-second loop. Stops when donation is unconfigured or button is toggled off.
; Related .......: DonateCC(), ToggleCCSpam(), DisableCCSpam()
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: CCSpamCycle()
; ===============================================================================================================================
Func CCSpamCycle()
	; === EARLY EXIT CHECK ===
	If Not $g_bCCSpamEnabled Then Return

	; === VALIDATION ===
	If Not $g_bRunState Then
		DisableCCSpam("Bot is not running")
		Return
	EndIf

	; === DONATION CONFIGURED CHECK ===
	If Not $g_bChkDonate Then
		DisableCCSpam("Donation is disabled in settings")
		Return
	EndIf

	; === INITIALIZATION ===
	$g_bCCSpamRunning = True
	SetLog("» CC SPAM MODE ENABLED «", $COLOR_INFO)

	; === MAIN SPAM LOOP ===
	While $g_bCCSpamEnabled And $g_bRunState

		; === DONATION EXECUTION ===
		DonateCC()

		; === POST-DONATE STATE CHECKS ===
		If Not $g_bRunState Then ExitLoop
		If checkObstacles() Then ExitLoop
		If $g_bRestart = True Then ExitLoop

		; Return to main village screen between cycles
		checkMainScreen(False)
		If _Sleep($DELAYRUNBOT3) Then ExitLoop

		; === CHECK IF DONATIONS ARE STILL CONFIGURED ===
		If Not $g_bChkDonate Then
			DisableCCSpam("Donation disabled during cycle")
			ExitLoop
		EndIf

		If Not $g_bDonationEnabled Then
			DisableCCSpam("Donation system disabled during cycle")
			ExitLoop
		EndIf

		; === WAIT BEFORE NEXT DONATION CYCLE ===
		SetLog("Waiting " & $g_iCCSpamInterval & "s before next donation")
		Local $iWaitTimer = __TimerInit()
		While __TimerDiff($iWaitTimer) < ($g_iCCSpamInterval * 1000)
			If Not $g_bCCSpamEnabled Then ExitLoop
			If Not $g_bRunState Then ExitLoop
			If _Sleep(1000) Then ExitLoop
		WEnd

		; === POST-WAIT EXIT CHECKS ===
		If Not $g_bCCSpamEnabled Then ExitLoop
		If Not $g_bRunState Then ExitLoop

	WEnd

	; === CLEANUP ===
	checkMainScreen(False)
	$g_bCCSpamRunning = False
EndFunc   ;==>CCSpamCycle

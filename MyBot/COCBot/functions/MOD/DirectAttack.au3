; ===============================================================================================================================
; ==================================================== DIRECT ATTACK MODULE =====================================================
; ===============================================================================================================================
; This module provides an independent direct attack simulation for MyBot.
; ===============================================================================================================================

; #FUNCTION# ====================================================================================================================
; Name ..........: DirectAttack
; Description ...: Performs a direct attack simulation with full siege machine deployment
; Syntax ........: DirectAttack()
; Author ........: Phael
; Remarks .......: This function simulates a direct attack on Live Base with all siege machines enabled
; Related .......: Attack(), PrepareAttack()
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: DirectAttack()
; ===============================================================================================================================
Func DirectAttack()
	; === VARIABLE BACKUP ===
	; Save current state to restore later
	Local $tempbRunState = $g_bRunState
	Local $tempSieges = $g_aiCurrentSiegeMachines

	; === UI INTERACTION ===
	; Start running flag, double-click prevention is handled by disabling the GUI Button
	$g_bDirectAttackRunning = True
	
	; Disable the Direct Attack GUI Button to prevent clicks while running
	If $g_hBtnDirectAttack <> 0 Then GUICtrlSetState($g_hBtnDirectAttack, $GUI_DISABLE)
	If $g_hbtnAttNow <> 0 Then GUICtrlSetState($g_hbtnAttNow, $GUI_DISABLE)
	_GUICtrlTab_ClickTab($g_hTabMain, 0)
	
	; === ATTACK MODE SETUP ===
	; Active Base ($LB) or Dead Base ($DB) — Set via Direct Attack Control 
	$g_iMatchMode = $g_iDirectAttackMode
	$g_bRunState = True
	
	; === CONFIGURATION MANAGEMENT ===
	; Save current config before applying script-specific settings
	SaveConfig()
	ApplyConfig_600_52_2("Read")

	; === PRE-ATTACK MEASUREMENT ===
	; run measurement code here only when the dedicated PrepareAttack option is *disabled*
	If Not $g_bPrepareAttackMeasurement Then
		; Zoom out the screen to ensure proper view for troop detection and attack preparation
		ZoomOutSimple()
		_Sleep(500) ; Small delay to ensure changes are applied
		
		; Ensure red lines are detected for accurate attack planning
		If $g_sImglocRedline = "" Then
			Local $tempRedlineRoutine = (IsDeclared("g_iRedlineRoutine") ? Eval("g_iRedlineRoutine") : 0)
			Assign("g_iRedlineRoutine", 1) ; Use New ImgLoc based deployable red line routine for better accuracy
			SearchRedLinesMultipleTimes() ; Retry multiple times for reliable detection
			If $g_sImglocRedline = "" Then
				SetLog("Warning: Red lines not detected, attack may fail", $COLOR_WARNING)
			EndIf
			If IsDeclared("g_iRedlineRoutine") Then Assign("g_iRedlineRoutine", $tempRedlineRoutine)
		EndIf
	EndIf

	; === ATTACK PREPARATION ===
	; Prepare the attack simulation based on the selected match mode
	PrepareAttack($g_iMatchMode)

	; === ATTACK EXECUTION ===
	; Perform the attack simulation based on the selected match mode
	Attack()
	
	; === STATE RESTORATION ===
	; Restore original siege machines and run state
	$g_aiCurrentSiegeMachines = $tempSieges
	$g_bRunState = $tempbRunState

	; === COMPLETION LOG ===
	; Re-enable Direct Attack GUI Button and clear running flag
	If $g_hBtnDirectAttack <> 0 Then GUICtrlSetState($g_hBtnDirectAttack, $GUI_ENABLE)
	If $g_hbtnAttNow <> 0 Then GUICtrlSetState($g_hbtnAttNow, $GUI_ENABLE) ; legacy control (if present)
	
	; Clear running flag
	$g_bDirectAttackRunning = False
	SetLog("» DIRECT ATTACK COMPLETED «", $COLOR_SUCCESS)
EndFunc   ;==>DirectAttack


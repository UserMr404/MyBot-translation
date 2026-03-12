; ===============================================================================================================================
; ===================================================== REVENGE BATTLE MODULE ===================================================
; ===============================================================================================================================
; This module handles automated revenge attacks before the normal attack flow.
; When enabled, it opens the attack log panel and searches for available revenge buttons
; using pixel detection. If found, executes the revenge attack directly.
; ===============================================================================================================================

; #FUNCTION# ====================================================================================================================
; Name ..........: JoinRevengeBattle
; Description ...: Attempts to find and execute a revenge attack from the attack log panel
; Syntax ........: JoinRevengeBattle()
; Parameters ....: None
; Return values .: True if a revenge attack was initiated, False otherwise
; Author ........: Phael
; Remarks .......: Uses _MultiPixelSearch to detect the orange Revenge button at 3 fixed slot positions.
; Related .......: PrepareSearch
; Example .......: JoinRevengeBattle()
; ===============================================================================================================================
Func JoinRevengeBattle()
	If Not $g_bEnableRevengeBattle Then Return False
	If Not $g_bRunState Then Return False
	If Not IsMainPage() Then Return False

	; === CHECK REVENGE COOLDOWN ===
	If $g_sNextRevengeTime <> "" Then
		Local $iLeft = _DateDiff('s', _NowCalc(), $g_sNextRevengeTime)
		If $iLeft > 0 Then
			SetLog("Revenge Cooldown Active (" & $iLeft & "s remaining)", $COLOR_DEBUG)
			Return False
		Else
			$g_sNextRevengeTime = "" ; Expired, clear timer
		EndIf
	EndIf

	SetLog("Checking Revenge Attacks", $COLOR_INFO)

	; === OPEN REVENGE PANEL ===
	Click(Random(33, 37, 1), Random(148, 152, 1), 1, 0, "Click Revenge Panel")
	If _Sleep(1000) Then Return False

	; === OPEN LOG TAB ===
	Click(Random(230, 390, 1), Random(145, 155, 1), 1, 0, "Click Battle Log Tab")
	If _Sleep(500) Then Return False

	Click(Random(280, 400, 1), Random(190, 200, 1), 1, 0, "Click Defense Log Tab")
	If _Sleep(500) Then Return False

	; === REVENGE BUTTON DETECTION ===
	Local $aRevengeY[3] = [271, 381, 491]
	Local $aRevengeCheck[4] = [705, 0, 0xFFAA72, 20] ; X=705 fixed, Y assigned per slot

	For $iSlot = 0 To 2
		If Not $g_bRunState Then Return False
		$aRevengeCheck[1] = $aRevengeY[$iSlot]
		If _CheckPixel($aRevengeCheck, $g_bCapturePixel) Then
			SetLog("Revenge Available (Slot " & ($iSlot + 1) & ")", $COLOR_SUCCESS)
			Click(Random(745, 755, 1), Random($aRevengeY[$iSlot] + 12, $aRevengeY[$iSlot] + 24, 1), 1, 0)
			If _Sleep(1500) Then Return False
			
			$g_bIsRevengeBattleActive = True
			$g_sNextRevengeTime = "" ; Clear any previous cooldown
			SetLog("Revenge Initiated!", $COLOR_SUCCESS)
		Return True
		EndIf
	Next

	SetLog("Revenge Attacks Unavailable", $COLOR_DEBUG)
	
	; === SET COOLDOWN ===
	$g_sNextRevengeTime = _DateAdd('h', 1, _NowCalc())
	SetLog("Next Revenge Check @ " & $g_sNextRevengeTime, $COLOR_DEBUG)
	
	CloseWindow()
	Return False
EndFunc   ;==>JoinRevengeBattle

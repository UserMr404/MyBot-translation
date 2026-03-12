; ===============================================================================================================================
; ==================================================== RANKED BATTLE MODULE =====================================================
; ===============================================================================================================================
; This module handles automated joining of ranked battles (tournaments) in Clash of Clans for MyBot.
; ===============================================================================================================================

; #FUNCTION# ====================================================================================================================
; Name ..........: JoinRankedBattle
; Description ...: Joins available ranked battles by detecting UI buttons and performing the attack sequence
; Syntax ........: JoinRankedBattle()
; Parameters ....: None
; Return values .: True if joined a ranked battle, False otherwise
; Author ........: Based on xbebenkMod, Phael (2026)
; Modified ......: 2026 - Improved structure and documentation
; Remarks .......: Part of MyBot MOD system. Requires image assets for button detection.
; Related .......: PrepareSearch(), QuickMIS()
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================

Func JoinRankedBattle()
	; === VARIABLE INITIALIZATION ===
	Local $bRankedBattle = False, $aMatch, $aButton

	; === BUTTON SEARCH LOOP ===
	For $i = 1 To 20
		If Not $g_bRunState Then Return False
		If _Sleep(50) Then Return False
		SetDebugLog("Searching for Ranked Battle button #" & $i, $COLOR_DEBUG)
		$aButton = QuickMIS("CNX", $g_sImgRankedBattleSearch, 325, 435, 540, 500)
		If IsArray($aButton) And UBound($aButton) > 0 Then

			; === BUTTON PROCESSING ===
			For $z = 0 To UBound($aButton) - 1
				If $aButton[$z][0] = "SignUp" Then
					SetLog("Sign Up Button Detected", $COLOR_DEBUG)
					Click($aButton[$z][1], $aButton[$z][2], 1, 0, "SignUp Ranked Battle")
					If _Sleep(1500) Then Return False
					If QuickMIS("BC1", $g_sImgRankedBattleSearch, 500, 460, 710, 530) Then
						Click($g_iQuickMISX, $g_iQuickMISY, 1, 0, "SignUp Ranked Battle [2]")
						SetLog("Signing In For Ranked Battle", $COLOR_ACTION)
						ContinueLoop 2
					EndIf
				EndIf
				If $aButton[$z][0] = "SignedUp" Then
					SetLog("Signed Up Button Detected", $COLOR_DEBUG)
					SetLog("Signup Confirmed!", $COLOR_SUCCESS)
					If _Sleep(500) Then Return False
					ExitLoop 2
				EndIf
				If $aButton[$z][0] = "Completed" Then
					SetLog("Ranked Attacks Completed", $COLOR_SUCCESS)
					If _Sleep(500) Then Return False
					ExitLoop 2
				EndIf
				If $aButton[$z][0] = "Match" Then
					SetLog("Ranked Match Button Detected", $COLOR_INFO)
					$aMatch = getMatchRemain()
					If UBound($aMatch) > 0 Then
						SetLog("Ranked Matches: " & $aMatch[0] & "/" & $aMatch[1], $COLOR_INFO)
						SetLog("Remaining Matches: " & ($aMatch[1] - $aMatch[0]), $COLOR_INFO)
						If $aMatch[1] - $aMatch[0] = 0 Then
							SetLog("All Ranked Attacks Used", $COLOR_SUCCESS)
							ExitLoop 2
						EndIf
					EndIf
					
					Click($aButton[$z][1], $aButton[$z][2], 1, 0, "Find a Match Ranked Battle")
					If _Sleep(1000) Then Return False
					
					; === ATTACK BUTTON CLICK ===
					If _Sleep(1500) Then Return False ; Wait for popup to appear
					Local $iGrnX = Random(700, 770, 1)
					Local $iGrnY = Random(530, 540, 1)
					Click($iGrnX, $iGrnY)
					_Sleep(1000) ; Wait for clouds

					; === CONFIRMATION BUTTON CLICK ===
					If _Sleep(500) Then Return False
					Click(Random(520, 530, 1), Random(445, 455, 1), 1, 0, "Confirm Ranked Battle Attack")
					_Sleep(500) ; Wait for confirmation
					
					$bRankedBattle = True
					$g_bIsRankedBattleActive = True
					ExitLoop 2
				EndIf
			Next
		EndIf
	Next

	Return $bRankedBattle
EndFunc   ;==>JoinRankedBattle
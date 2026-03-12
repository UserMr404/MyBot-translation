; #FUNCTION# ====================================================================================================================
; Name ..........: StarBonus
; Description ...: Checks for Star bonus window, and clicks ok to close window.
; Syntax ........: StarBonus()
; Parameters ....:
; Return values .: MonkeyHunter(2016-1)
; Modified ......: MonkeyHunter (05-2017), Moebius14 (12-2023)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================
Func StarBonus()

	SetDebugLog("Begin Star Bonus window check", $COLOR_DEBUG1)

	Local $aWindowChk1[4] = [830, 130, 0x3E2EB7, 15]
	Local $aWindowChk2[4] = [830, 620, 0x524A45, 15]

	If _Sleep($DELAYSTARBONUS100) Then Return

	; Verify actual star bonus window open
	If _CheckPixel($aWindowChk1, $g_bCapturePixel, Default, "Starbonus1") And _CheckPixel($aWindowChk2, $g_bCapturePixel, Default, "Starbonus2") Then
		Click(435, 570) ; Click Okay Button
		SetDebugLog("Star Bonus Funcionou", $COLOR_DEBUG)
		If _Sleep($DELAYSTARBONUS500) Then Return
		$StarBonusReceived = 1
		Return True
	EndIf

	SetDebugLog("Star Bonus window not found?", $COLOR_DEBUG)
	Return False

EndFunc   ;==>StarBonus

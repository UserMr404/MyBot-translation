; #FUNCTION# ====================================================================================================================
; Name ..........: CheckBotRestartCondition
; Description ...: Function to check if Bot needs to restart after x hours
; Syntax ........: CheckBotRestartCondition()
; Parameters ....: $bRestartBot = True restarts Bot
; Return values .: True if Bot restart should be initiated, False otherwise
; Author ........: AI Assistant (2025)
; Modified ......:
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: If CheckBotRestartCondition() = True Then _RestartBot()
; ===============================================================================================================================
#include-once

Func InitBotRestartCondition($bLaunched = True)
	If $bLaunched = False Then
		$g_hBotLaunchTime = 0
		Return False
	EndIf
	$g_hBotLaunchTime = __TimerInit()
	Return True
EndFunc   ;==>InitBotRestartCondition

Func CheckBotRestartCondition($bRestartBot = True, $bLogOnly = False)

	; check if enabled
	If $g_bBotRestartEnabled = False Then Return False

	; check only for timeout restart condition
	If $g_iBotRestartHours <= 0 Then Return False

	Local $iLaunched = __TimerDiff($g_hBotLaunchTime)

	If $bLogOnly = True Then

		Local $day = 0, $hour = 0, $min = 0, $sec = 0, $sTime
		_TicksToDay($g_iBotRestartHours * 60 * 60 * 1000 - $iLaunched, $day, $hour, $min, $sec)
		$sTime = StringFormat("%id %ih %im", $day, $hour, $min)
		SetLog("Bot will be automatically restarted in " & $sTime)
		Return True

	EndIf

	If $g_bIdleState = False Then Return False

	Local $iRunTimeHrs = $iLaunched / (60 * 60 * 1000)

	If $iRunTimeHrs >= $g_iBotRestartHours Then
		SetLog("Restart Bot due to configured run-time of " & $g_iBotRestartHours & "h")
		Return True
	EndIf

	SetLog("Bot will restart in " & Round($g_iBotRestartHours - $iRunTimeHrs, 1) & " hours")
	Return False

EndFunc   ;==>CheckBotRestartCondition

Func CheckBotRestart($bRestartBot = True)
	Return CheckBotRestartCondition($bRestartBot)
EndFunc   ;==>CheckBotRestart
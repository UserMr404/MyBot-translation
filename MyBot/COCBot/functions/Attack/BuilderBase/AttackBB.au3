; #FUNCTION# ====================================================================================================================
; Name ..........: AttackBB
; Description ...: This file controls attacking preperation of the builders base
; Syntax ........:
; Parameters ....: None
; Return values .: None
; Author ........: Chilly-Chill (04-2019)
; Modified ......: Moebius14 (08-2023)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================
Local $IsChallengeCompleted = False
Local $bFirstAttackClick

Func CheckCGCompleted()
	Local $bRet = False
	Local $CompleteBar = 0
	For $x = 1 To 12
		If QuickMIS("BC1", $g_sImgBBAttackBonus, 360, 450 + $g_iMidOffsetY, 500, 510 + $g_iMidOffsetY) Then
			SetLog("Congratulations chief, stars bonus awarded!", $COLOR_SUCCESS)
			Click($g_iQuickMISX, $g_iQuickMISY)
			If _Sleep(250) Then Return
		EndIf
		If Not $g_bRunState Then Return
		SetDebugLog("Check challenges progress #" & $x, $COLOR_ACTION)
		If QuickMIS("BC1", $g_sImgGameComplete, 770, 474 + $g_iMidOffsetY, 830, 534 + $g_iMidOffsetY) Then
			SetLog("Challenge Completed", $COLOR_INFO)
			$g_bIsBBevent = 0
			$bRet = True
			ExitLoop
		EndIf
		If _ColorCheck(_GetPixelColor(830, 500 + $g_iMidOffsetY, True), Hex(0xFFD53D, 6), 10, Default) Then $CompleteBar += 1
		If $x = 12 And $CompleteBar = 0 Then
			SetDebugLog("No Complete Bar Detected, Stop Attack To Check", $COLOR_DEBUG)
			$g_bIsBBevent = 0
			$bRet = True
		EndIf
		If _Sleep(500) Then Return
	Next
	Return $bRet
EndFunc   ;==>CheckCGCompleted

Func DoAttackBB()

	If Not $g_bChkEnableBBAttack Then Return

	$IsChallengeCompleted = False
	$b_AbortedAttack = False
	Local $AttackCount = 0
	$iStartSlotMem = 0
	$iStartSlotMem2 = 0

	If $g_iBBAttackCount = 0 Then
		While PrepareAttackBB($AttackCount)
			If Not $g_bRunState Then Return
			SetDebugLog("PrepareAttackBB(): Success.", $COLOR_SUCCESS)
			SetLog("Attacking For Stars", $COLOR_OLIVE)
			SetLog("Attack #" & $AttackCount + 1 & "/~", $COLOR_INFO)
			_AttackBB()
			If Not $g_bRunState Then ExitLoop
			If $IsChallengeCompleted Then ExitLoop
			$AttackCount += 1
			If $AttackCount > 10 Then
				SetLog("Already Attack 10 times, continue next time", $COLOR_INFO)
				ExitLoop
			EndIf
			If _Sleep($DELAYATTACKMAIN2) Then ExitLoop
			checkObstacles()
		WEnd
		SetLog("Skip Attack This Time", $COLOR_DEBUG)
	Else
		Local $g_iBBAttackCountFinal = 0
		Local $AttackNbDisplay = 0
		If $g_iBBAttackCount = 1 Then
			$g_iBBAttackCountFinal = Random(2, 7, 1)
		ElseIf $g_iBBAttackCount > 1 Then
			$g_iBBAttackCountFinal = $g_iBBAttackCount - 1
		EndIf
		For $i = 1 To $g_iBBAttackCountFinal
			If Not $g_bRunState Then ExitLoop
			If PrepareAttackBB($AttackCount) Then
				If $AttackNbDisplay = 0 Then
					If $g_iBBAttackCount = 1 Then
						SetLog("Random Number Of Attacks: " & $g_iBBAttackCountFinal, $COLOR_OLIVE)
					ElseIf $g_iBBAttackCount > 1 Then
						SetLog("Number Of Attacks:" & $g_iBBAttackCountFinal, $COLOR_ACTION)
					EndIf
				EndIf
				$AttackNbDisplay += 1
				SetDebugLog("PrepareAttackBB(): Success.", $COLOR_SUCCESS)
				SetLog("Attack #" & $i & "/" & $g_iBBAttackCountFinal, $COLOR_INFO)
				If $b_AbortedAttack Then $b_AbortedAttack = False ; Reset Value
				_AttackBB()
				If Not $g_bRunState Then ExitLoop
				If Not $b_AbortedAttack Then
					$AttackCount += 1 ; Count if no Zoom Out fail
				Else
					SetLog("Add one more attack due to Zoom Out Fail", $COLOR_INFO)
					$g_iBBAttackCountFinal += 1
				EndIf
				If $IsChallengeCompleted Then
					SetLog("Skip Attack This Time", $COLOR_DEBUG)
					ExitLoop
				EndIf
				If $i = $g_iBBAttackCountFinal Then
					SetLog("Skip Attack This Time", $COLOR_DEBUG)
					ExitLoop
				EndIf
				If $AttackCount > 10 Then
					SetLog("Already Attack 10 times, continue next time", $COLOR_INFO)
					ExitLoop
				EndIf
				If _Sleep($DELAYATTACKMAIN2) Then ExitLoop
				checkObstacles()
			Else
				SetLog("Skip Attack This Time", $COLOR_DEBUG)
				ExitLoop
			EndIf
		Next
	EndIf
	If Not $g_bRunState Then Return
	If $AttackCount > 0 Then SetLog("BB Attack Cycle Done", $COLOR_SUCCESS1)
	ZoomOut()
	$iStartSlotMem = 0
	$iStartSlotMem2 = 0
EndFunc   ;==>DoAttackBB

Func ClickFindNowButton()
	Local $bRet = False
	For $i = 1 To 10
		If _ColorCheck(_GetPixelColor(655, 437 + $g_iMidOffsetY, True), Hex(0x89D239, 6), 20) Then
			Local $FindNowCoordsX[2] = [590, 715]
			Local $FindNowCoordsY[2] = [400 + $g_iMidOffsetY, 430 + $g_iMidOffsetY]
			Local $FindNowButtonClickX = Random($FindNowCoordsX[0], $FindNowCoordsX[1], 1)
			Local $FindNowButtonClickY = Random($FindNowCoordsY[0], $FindNowCoordsY[1], 1)
			Click($FindNowButtonClickX, $FindNowButtonClickY, 1, 120, "#0149") ; Click FindNow Button
			$bRet = True
			ExitLoop
		EndIf
		If _Sleep(500) Then Return
	Next

	If Obstructed() Then SetLog("Defensive Layout obstructed by obstacles, Attack Anyway !", $COLOR_WARNING)

	If _Sleep(8000) Then Return ; give time for find now button to go away
	If Not $bRet Then
		SetLog("Could not locate Find Now Button to go find an attack.", $COLOR_ERROR)
		CloseWindow2()
		Return False
	EndIf

	Return $bRet
EndFunc   ;==>ClickFindNowButton

Func Obstructed()

	If _Sleep(250) Then Return
	Local $sSearchDiamond = GetDiamondFromRect2(460, 380 + $g_iMidOffsetY, 600, 445 + $g_iMidOffsetY)

	For $i = 0 To 3
		Local $aCoords = decodeSingleCoord(findImage("ClickAttack", $g_sImgBBAttackButton, $sSearchDiamond, 1, True))
		If IsArray($aCoords) And UBound($aCoords) = 2 Then
			SetDebugLog("Attack Button found at " & String($aCoords[0]) & " " & String($aCoords[1]))
			ClickP($aCoords, 1, 120, "#0149") ; Click Attack Button
			If _Sleep(250) Then Return
			Return True
		EndIf
		If $i = 3 Then ExitLoop
		If _Sleep(250) Then Return
	Next

	Return False

EndFunc   ;==>Obstructed

Func WaitCloudsBB()
	Local $bRet = True

	Local $count = 1
	While Not QuickMIS("BC1", $g_sImgBBAttackStart, 370 + $g_iMidOffsetY, 25, 430 + $g_iMidOffsetY, 60)
		If Not $g_bRunState Then Return
		If $count = 19 Then
			SetLog("Too long waiting Clouds", $COLOR_ERROR)
		EndIf

		If $count = 21 Then
			SetLog("Try To Close and Search Again", $COLOR_ACTION)
			If $g_bDebugImageSave Then SaveDebugImage("WaitCloudsBB")
			Click(430, 535 + $g_iMidOffsetY)
			If _Sleep(3000) Then Return
			If Not ClickAttack() Then Return False
			If _Sleep(1500) Then Return
			SetLog("Trying again to attack", $COLOR_INFO)
			If Not ClickFindNowButton() Then
				ClearScreen("Defaut", False)
				Return False
			EndIf
		EndIf

		If $count > 30 Then
			CloseCoC(True)
			checkMainScreen(False, True)
			$bRet = False
			ExitLoop
		EndIf
		If isProblemAffect(True) Then Return
		$count += 1
		If _Sleep(2000) Then Return
	WEnd
	Return $bRet
EndFunc   ;==>WaitCloudsBB

Func _AttackBB()
	If Not $g_bRunState Then Return

	SetLog("Going To Attack", $COLOR_INFO)
	If Not ClickFindNowButton() Then
		ClearScreen("Defaut", False)
		Return False
	EndIf

	If Not $g_bRunState Then Return

	SetLog("Searching For Opponent", $COLOR_BLUE)
	If Not WaitCloudsBB() Then Return
	If Not $g_bRunState Then Return

	ZoomOut()
	If Not isOnBuilderBaseEnemyVillage(True) Then
		SetLog("Zoom Out has failed and Attack was aborted", $COLOR_DEBUG)
		$b_AbortedAttack = True
		Return
	EndIf

	; Get troops on attack bar and their quantities
	$g_aMachinePos = GetMachinePos()
	$g_DeployedMachine = False
	If _Sleep(150) Then Return
	Local $aBBAttackBar = GetAttackBarBB()

	If $g_bChkDropTrophyBB Then
		; Perform a normal attack but end battle immediately to drop trophies
		$bFirstAttackClick = True
		AttackBB($aBBAttackBar, True)
		Return
	EndIf

	$bFirstAttackClick = True
	AttackBB($aBBAttackBar)

	If Not $g_bRunState Then Return

	If EndBattleBB() Then SetLog("Battle Ended", $COLOR_INFO)
	If _Sleep($DELAYATTACKMAIN2) Then Return
	checkObstacles()

EndFunc   ;==>_AttackBB

Func EndBattleBB() ; Find if battle has ended and click okay
	Local $bRet = False, $bBattleMachine = True, $bBomber = True
	Local $sDamage = 0, $sTmpDamage = 0, $bCountSameDamage = 1

	For $i = 1 To 200

		If Not $g_bRunState Then ExitLoop
		If $bBattleMachine Then $bBattleMachine = CheckBMLoop()
		If $bBomber Then $bBomber = CheckBomberLoop()
		$sDamage = getOcrOverAllDamage(776, 558 + $g_iMidOffsetY)
		SetDebugLog("[" & $i & "] EndBattleBB LoopCheck, [" & $bCountSameDamage & "] Overall Damage : " & $sDamage & "%", $COLOR_DEBUG2)
		If Number($sDamage) = Number($sTmpDamage) Then
			$bCountSameDamage += 1
		Else
			$bCountSameDamage = 1
		EndIf
		$sTmpDamage = Number($sDamage)
		If $sTmpDamage = 100 Then
			Local $EndLoop = 0
			While 1
				If BBGoldEnd("EndBattleBB") Then
					$bRet = True
					If _Sleep(3000) Then Return
					ExitLoop 2
				EndIf
				$EndLoop += 1
				If $EndLoop = 20 Then ExitLoop
				If _Sleep(250) Then Return
			WEnd
			If _SleepStatus(7000) Then Return
			SetLog("Preparing For Second Round", $COLOR_INFO)
			If _Sleep(3000) Then Return
			;#cs
			ZoomOut()
			If Not isOnBuilderBaseEnemyVillage(True) Then
				SetLog("Zoom Out has failed and Attack was aborted", $COLOR_DEBUG)
				Return False
			EndIf
			;#ce
			; Get troops on attack bar and their quantities
			$g_aMachinePos = GetMachinePos()
			$g_DeployedMachine = False
			If _Sleep(150) Then Return
			Local $aBBAttackBar = GetAttackBarBB(False, True)
			AttackBB($aBBAttackBar)

			If _Sleep(5000) Then Return ; Add some delay for troops making some damage
			$sTmpDamage = 0
			$bBattleMachine = True
			$bBomber = True
		EndIf

		If $bCountSameDamage > 25 Then
			If ReturnHomeDropTrophyBB(True) Then $bRet = True
			ExitLoop
		EndIf

		If BBGoldEnd("EndBattleBB") Then
			$bRet = True
			If _Sleep(3000) Then Return
			ExitLoop
		EndIf

		If IsProblemAffect(True) Then Return
		If Not $g_bRunState Then ExitLoop
		If _Sleep(1000) Then Return
	Next

	If Not $g_bRunState Then Return

	For $i = 1 To 3
		Select
			Case QuickMIS("BC1", $g_sImgBBReturnHome, 380, 510 + $g_iMidOffsetY, 480, 570 + $g_iMidOffsetY) = True
				If _Sleep(2000) Then Return
				Click($g_iQuickMISX, $g_iQuickMISY)
				If $g_bIsBBevent Then
					If CheckCGCompleted() Then
						$IsChallengeCompleted = True
					Else
						SetLog("Challenge still in progress")
					EndIf
				EndIf
				If _Sleep(2000) Then Return
			Case QuickMIS("BC1", $g_sImgBBAttackBonus, 360, 450 + $g_iMidOffsetY, 500, 510 + $g_iMidOffsetY) = True
				SetLog("Congratulations chief, stars bonus awarded!", $COLOR_SUCCESS)
				If _Sleep(2000) Then Return
				Click($g_iQuickMISX, $g_iQuickMISY)
				If _Sleep(2000) Then Return
				$bRet = True
			Case isOnBuilderBase() = True
				$bRet = True
		EndSelect
		If _Sleep(1000) Then Return
	Next

	If Not $bRet Then SetLog("Could not find finish battle screen", $COLOR_ERROR)
	Return $bRet
EndFunc   ;==>EndBattleBB

Func AttackBB($aBBAttackBar = True, $bDropTrophy = False)

	Local $iSide
	Local $ai_DropPoints = []
	SetDebugLog("AttackBB: g_iBBPrioritizeDefenses = " & $g_iBBPrioritizeDefenses, $COLOR_DEBUG)
	If $g_iBBPrioritizeDefenses > 0 Then
		SetLog("Locating Priority Defenses", $COLOR_INFO)
		Local $aDefenseCounts[5] = [0,0,0,0,0]
		Local $aDefenseFuncs = ["FindLavaLauncher", "FindAirBombs", "FindMegaTesla", "FindGuardPost"]
		For $sFunc In $aDefenseFuncs
			SetDebugLog("About to call " & $sFunc, $COLOR_DEBUG)
			Local $aPositions = Call($sFunc)
			SetDebugLog("Called " & $sFunc & ", returned " & (IsArray($aPositions) ? UBound($aPositions, 1) & "x" & UBound($aPositions, 2) : "non-array") & " positions", $COLOR_DEBUG)
			If IsArray($aPositions) And UBound($aPositions, 1) > 0 Then
				SetDebugLog("Processing " & UBound($aPositions, 1) & " defense positions", $COLOR_DEBUG)
				For $i = 0 To UBound($aPositions, 1) - 1
					If UBound($aPositions, 2) >= 2 Then
						Local $aPos = [$aPositions[$i][0], $aPositions[$i][1]]
						Local $iSideTemp = GetSideFromPos($aPos[0], $aPos[1])
						If $iSideTemp > 0 Then $aDefenseCounts[$iSideTemp] += 1
					EndIf
				Next
			EndIf
		Next
		Local $sDefenseName = ""
		Switch $g_iBBPrioritizeDefenses
			Case 1
				$sDefenseName = "Lava Launcher"
			Case 2
				$sDefenseName = "Air Bomb"
			Case 3
				$sDefenseName = "Mega Tesla"
			Case 4
				$sDefenseName = "Guard Post"
		EndSwitch
		SetLog("Defense Detection (" & $sDefenseName & "): TL=" & $aDefenseCounts[1] & ", TR=" & $aDefenseCounts[2] & ", BR=" & $aDefenseCounts[3] & ", BL=" & $aDefenseCounts[4], $COLOR_INFO)
	EndIf
	Switch $g_iBBSideAttack
		Case 0 ; Random
			$iSide = Random(1, 4, 1)
		Case 1 ; 1 Side
			$iSide = ($g_iBBPrioritizeDefenses > 0) ? GetBestSide($aDefenseCounts, 1) : Random(1, 4, 1)
		Case 2 ; 2 Sides
			If $g_iBBPrioritizeDefenses > 0 Then
				$iSide = GetBestSide($aDefenseCounts, 2)
			Else
				; Random two different sides
				Local $iSide1 = Random(1, 4, 1)
				Local $iSide2 = Random(1, 4, 1)
				While $iSide2 = $iSide1
					$iSide2 = Random(1, 4, 1)
				WEnd
				$iSide = $iSide1 * 10 + $iSide2
			EndIf
		Case 3 ; All Sides
			$iSide = 0 ; Special case for all sides
	EndSwitch
	;generate attack drop points
	Switch $iSide
		Case 0 ; All Sides - combine all 4 sides
			Local $ai_DropPoints1 = _GetVectorOutZone($eVectorLeftTop)
			Local $ai_DropPoints2 = _GetVectorOutZone($eVectorRightTop)
			Local $ai_DropPoints3 = _GetVectorOutZone($eVectorRightBottom)
			Local $ai_DropPoints4 = _GetVectorOutZone($eVectorLeftBottom)
			; Combine all drop points into one array
			Local $iTotalPoints = UBound($ai_DropPoints1) + UBound($ai_DropPoints2) + UBound($ai_DropPoints3) + UBound($ai_DropPoints4)
			ReDim $ai_DropPoints[$iTotalPoints]
			Local $iIndex = 0
			For $i = 0 To UBound($ai_DropPoints1) - 1
				$ai_DropPoints[$iIndex] = $ai_DropPoints1[$i]
				$iIndex += 1
			Next
			For $i = 0 To UBound($ai_DropPoints2) - 1
				$ai_DropPoints[$iIndex] = $ai_DropPoints2[$i]
				$iIndex += 1
			Next
			For $i = 0 To UBound($ai_DropPoints3) - 1
				$ai_DropPoints[$iIndex] = $ai_DropPoints3[$i]
				$iIndex += 1
			Next
			For $i = 0 To UBound($ai_DropPoints4) - 1
				$ai_DropPoints[$iIndex] = $ai_DropPoints4[$i]
				$iIndex += 1
			Next
		Case 12, 13, 14, 21, 23, 24, 31, 32, 34, 41, 42, 43 ; Two sides combinations
			Local $iSide1 = Int($iSide / 10)
			Local $iSide2 = Mod($iSide, 10)
			Local $ai_DropPoints1, $ai_DropPoints2
			Switch $iSide1
				Case 1
					$ai_DropPoints1 = _GetVectorOutZone($eVectorLeftTop)
				Case 2
					$ai_DropPoints1 = _GetVectorOutZone($eVectorRightTop)
				Case 3
					$ai_DropPoints1 = _GetVectorOutZone($eVectorRightBottom)
				Case 4
					$ai_DropPoints1 = _GetVectorOutZone($eVectorLeftBottom)
			EndSwitch
			Switch $iSide2
				Case 1
					$ai_DropPoints2 = _GetVectorOutZone($eVectorLeftTop)
				Case 2
					$ai_DropPoints2 = _GetVectorOutZone($eVectorRightTop)
				Case 3
					$ai_DropPoints2 = _GetVectorOutZone($eVectorRightBottom)
				Case 4
					$ai_DropPoints2 = _GetVectorOutZone($eVectorLeftBottom)
			EndSwitch
			; Combine both sides
			Local $iTotalPoints = UBound($ai_DropPoints1) + UBound($ai_DropPoints2)
			ReDim $ai_DropPoints[$iTotalPoints]
			Local $iIndex = 0
			For $i = 0 To UBound($ai_DropPoints1) - 1
				$ai_DropPoints[$iIndex] = $ai_DropPoints1[$i]
				$iIndex += 1
			Next
			For $i = 0 To UBound($ai_DropPoints2) - 1
				$ai_DropPoints[$iIndex] = $ai_DropPoints2[$i]
				$iIndex += 1
			Next
		Case 1
			$ai_DropPoints = _GetVectorOutZone($eVectorLeftTop)
		Case 2
			$ai_DropPoints = _GetVectorOutZone($eVectorRightTop)
		Case 3
			$ai_DropPoints = _GetVectorOutZone($eVectorRightBottom)
		Case 4
			$ai_DropPoints = _GetVectorOutZone($eVectorLeftBottom)
	EndSwitch

	If IsProblemAffect(True) Then Return

	Local $bTroopsDropped = False
	If Not $g_bRunState Then Return

	; Deploy all troops
	SetLog($g_bBBDropOrderSet = True ? "Deploying Troops In Custom Order" : "Deploying Troops In Order Of Attack Bar", $COLOR_BLUE)
	Local $bLoop = 0 ; Break Loop If 4 Loops
	While Not $bTroopsDropped
		If Not $g_bRunState Then Return
		Local $iNumSlots = UBound($aBBAttackBar)
		If $g_bBBDropOrderSet = True Then
			Local $asBBDropOrder = StringSplit($g_sBBDropOrder, "|")
			Local $DeployedSlot = 0
			For $i = 0 To $g_iBBTroopCount - 1 ; loop through each name in the drop order
				For $j = 0 To $iNumSlots - 1
					If $aBBAttackBar[$j][0] = $asBBDropOrder[$i + 1] Then
						DeployBBTroop($aBBAttackBar[$j][0], $aBBAttackBar[$j][1] + 35, $aBBAttackBar[$j][2], $bDropTrophy ? 1 : $aBBAttackBar[$j][4], $ai_DropPoints)
						If $bDropTrophy Then
							$bTroopsDropped = True
							ExitLoop 3
						EndIf
						$DeployedSlot += 1
					EndIf
					If $DeployedSlot = $iNumSlots Then ExitLoop 2
				Next
				If _Sleep($g_iBBNextTroopDelay) Then Return ; wait before next troop
				If $i = $g_iBBTroopCount - 1 Then $bLoop += 1
				If $bLoop = 4 Then
					SaveDebugImage("AttackBar")
					SetLog("All Troops Can't Be Deployed", $COLOR_DEBUG)
					SetLog("Awaiting Battle Completion", $COLOR_INFO)
					ExitLoop 2
				EndIf
			Next
		Else
			Local $sTroopName = ""
			For $i = 0 To $iNumSlots - 1
				If $aBBAttackBar[$i][4] > 0 Then DeployBBTroop($aBBAttackBar[$i][0], $aBBAttackBar[$i][1] + 35, $aBBAttackBar[$i][2], $bDropTrophy ? 1 : $aBBAttackBar[$i][4], $ai_DropPoints)
				If $bDropTrophy Then
					$bTroopsDropped = True
					ExitLoop
				EndIf
				If $sTroopName <> $aBBAttackBar[$i][0] Then
					If _Sleep($g_iBBNextTroopDelay) Then Return ; wait before next troop
				Else
					_Sleep($DELAYRESPOND) ; we are still on same troop so lets drop them all down a bit faster
				EndIf
				$sTroopName = $aBBAttackBar[$i][0]
				If $i = $iNumSlots - 1 Then $bLoop += 1
				If $bLoop = 4 Then
					SaveDebugImage("AttackBar")
					SetLog("All Troops Can't Be Deployed", $COLOR_DEBUG)
					SetLog("Awaiting Battle Completion", $COLOR_INFO)
					ExitLoop 2
				EndIf
			Next
		EndIf
		$aBBAttackBar = GetAttackBarBB(True)
		If $aBBAttackBar = "" Then
			SetLog("All Troops Deployed", $COLOR_SUCCESS)
			SetLog("Awaiting Battle Completion", $COLOR_INFO)
			$bTroopsDropped = True
			;Use Troops Skills
			If $g_bChkBBUseTroopsSkills Then ActivateBBTroopsSkills()
		EndIf
	WEnd

	If Not $g_bRunState Then Return
	If IsProblemAffect(True) Then Return

	If $bDropTrophy Then
		If _Sleep(2000) Then Return ; wait for troops to deploy
		SetLog("Ending battle to drop trophies", $COLOR_INFO)
		ReturnHomeDropTrophyBB(False)
		; Update stats
		$g_iDroppedTrophyCount += 1
		UpdateStats()
		SetDebugLog("DropTrophyBB(): End", $COLOR_DEBUG)
		Return
	EndIf

	If Not $g_bRunState Then Return
	Return
EndFunc   ;==>AttackBB

Func DeployBBTroop($sName, $x, $y, $iAmount, $ai_AttackDropPoints)

	If $sName = "BattleMachine" Then
		Local $aBMPos = GetMachinePos()
		If IsArray($aBMPos) And $aBMPos <> 0 Then
			If StringInStr($aBMPos[2], "Copter") Then
				$sName = "Battle Copter"
			Else
				$sName = "Battle Machine"
			EndIf
		EndIf
		SetLog("Deploying " & $sName, $COLOR_ACTION)
	Else
		SetLog("Deploying " & $sName & " x" & String($iAmount), $COLOR_ACTION)
	EndIf

	PureClick($x, $y) ; select troop
	If _Sleep($g_iBBSameTroopDelay) Then Return ; slow down selecting then dropping troops

	For $j = 0 To $iAmount - 1
		If Not $g_bRunState Then Return
		; get random drop point
		Local $iPoint = Random(0, UBound($ai_AttackDropPoints) - 1, 1)
		Local $iPixel = $ai_AttackDropPoints[$iPoint]

		If $bFirstAttackClick Then
			IsClickOnPotions($iPixel[0], $iPixel[1])
			$bFirstAttackClick = False
		EndIf

		PureClickP($iPixel)
		Local $b_MachineTimeOffset = 0
		If $sName = "Battle Copter" Or $sName = "Battle Machine" Then
			Local $b_MachineTimeOffsetDiff = __TimerInit()
			Local $bRet = False
			For $i = 1 To 16 ; 4 seconds limit
				If Not $g_bRunState Then Return
				If _Sleep(250) Then Return
				Local $aBMPosCheck = GetMachinePos()
				If IsArray($aBMPosCheck) And $aBMPosCheck <> 0 And Number($aBMPos[1]) <> Number($aBMPosCheck[1]) Then
					If $g_bDebugSetLog Then
						Local $b_MachineTimeOffsetSec = Round(__TimerDiff($b_MachineTimeOffsetDiff) / 1000, 2)
						SetLog("$aBMPosCheck fixed in : " & $b_MachineTimeOffsetSec & " second", $COLOR_DEBUG)
					EndIf
					$bRet = True
				EndIf
				If $bRet Then ExitLoop
			Next
			Local $g_DeployColor[2] = [0xCD3AFF, 0xFF8BFF]
			For $z = 0 To 1
				If Not $g_bRunState Then Return
				If _ColorCheck(_GetPixelColor(71, 663 + $g_iBottomOffsetY, True), Hex(0x4E4E4E, 6), 20, Default) Then ;BM lvl<5
					$g_DeployedMachine = True
					$g_bMachineAliveOnAttackBar = False
					SetLog($sName & " Deployed", $COLOR_SUCCESS)
					ExitLoop
				EndIf
				If WaitforPixel(24, 552 + $g_iBottomOffsetY, 30, 554 + $g_iBottomOffsetY, Hex($g_DeployColor[$z], 6), 30, 5) Then ;BM with Capacity
					$g_DeployedMachine = True
					SetLog($sName & " Deployed", $COLOR_SUCCESS)
					PureClickP($aBMPos) ; Activate Ability
					SetLog("Activate " & $sName & " Ability", $COLOR_SUCCESS)
					ExitLoop
				EndIf
				If $z = 1 And $g_bDebugImageSave Then SaveDebugImage("AttackBar")
			Next
		EndIf
		If Number($g_iBBSameTroopDelay - $b_MachineTimeOffset) > 0 Then
			If _Sleep($g_iBBSameTroopDelay - $b_MachineTimeOffset) Then Return ; slow down dropping of troops
		EndIf
	Next
EndFunc   ;==>DeployBBTroop

Func GetMachinePos()
	Local $aBMPos = QuickMIS("CNX", $g_sImgBBBattleMachine, 18, 540 + $g_iBottomOffsetY, 85, 665 + $g_iBottomOffsetY)
	Local $aCoords[3]
	If $aBMPos = -1 Then Return 0

	If IsArray($aBMPos) Then
		$aCoords[0] = $aBMPos[0][1] ;x
		$aCoords[1] = $aBMPos[0][2] ;y
		$aCoords[2] = $aBMPos[0][0] ;Name
		Return $aCoords
	EndIf
	Return 0
EndFunc   ;==>GetMachinePos

Func CheckBMLoop($aBMPos = $g_aMachinePos)
	Local $BMDeadX = 71, $BMDeadColor
	Local $BMDeadY = 663 + $g_iBottomOffsetY
	Local $MachineName = ""

	If $aBMPos = 0 Or Not $g_bMachineAliveOnAttackBar Then Return False
	If Not IsArray($aBMPos) Then Return False

	If StringInStr($aBMPos[2], "Copter") Then
		$MachineName = "Battle Copter"
	Else
		$MachineName = "Battle Machine"
	EndIf

	If IsProblemAffect(True) Then Return
	If Not $g_bRunState Then Return False

	If QuickMIS("BC1", $g_sImgDirMachineAbility, $aBMPos[0] - 35, $aBMPos[1] - 40, $aBMPos[0] + 35, $aBMPos[1] + 40) Then
		If StringInStr($g_iQuickMISName, "Wait") Then
			; Wait for ability
		ElseIf StringInStr($g_iQuickMISName, "Ability") Then
			PureClickP($aBMPos)
			SetLog("Activate " & $MachineName & " Ability", $COLOR_SUCCESS)
		EndIf
	EndIf

	$BMDeadColor = _GetPixelColor($BMDeadX, $BMDeadY, True)
	If _ColorCheck($BMDeadColor, Hex(0x4E4E4E, 6), 20, Default) Then
		SetLog($MachineName & " Defeated", $COLOR_DEBUG)
		Return False
	EndIf

	Return True
EndFunc   ;==>CheckBMLoop

Func CheckBomberLoop()
	Local $bRet = True
	Local $nbrDeadBomber = 0
	If Not $g_bBomberOnAttackBar Or UBound($g_aBomberOnAttackBar) = 0 Then Return False
	Local $isGreyBanner = False, $ColorPickBannerX = 0, $iTroopBanners = 583 + $g_iBottomOffsetY

	For $i = 0 To UBound($g_aBomberOnAttackBar) - 1
		If Not $g_bRunState Then Return False
		$ColorPickBannerX = $g_aBomberOnAttackBar[$i][0] + 37
		$isGreyBanner = _ColorCheck(_GetPixelColor($ColorPickBannerX, $iTroopBanners, True), Hex(0x707070, 6), 10, Default) ;Grey Banner on TroopSlot = Troop Die
		If $isGreyBanner Then
			If UBound($g_aBomberOnAttackBar) = 1 Then
				SetLog("Bomber Defeated", $COLOR_DEBUG)
			Else
				If $BomberDead[$i] = 0 Then SetLog("Bomber " & $i + 1 & " Defeated", $COLOR_DEBUG)
				$BomberDead[$i] = 1
			EndIf
			$nbrDeadBomber += 1
			If $nbrDeadBomber = UBound($g_aBomberOnAttackBar) Then
				$bRet = False
				ExitLoop
			EndIf
		EndIf
		If QuickMIS("BC1", $g_sImgDirBomberAbility, $g_aBomberOnAttackBar[$i][0], $g_aBomberOnAttackBar[$i][1] - 30, $g_aBomberOnAttackBar[$i][0] + 70, $g_aBomberOnAttackBar[$i][1] + 30) Then
			If StringInStr($g_iQuickMISName, "Ability") Then
				Click($g_iQuickMISX, $g_iQuickMISY)
				If UBound($g_aBomberOnAttackBar) = 1 Then
					SetLog("Activate Bomber Ability", $COLOR_SUCCESS)
					ExitLoop
				Else
					SetLog("Activate Bomber " & $i + 1 & " Ability", $COLOR_SUCCESS)
					If _Sleep(Random(500, 1000, 1)) Then ExitLoop
				EndIf
			EndIf
		EndIf
	Next
	Return $bRet
EndFunc   ;==>CheckBomberLoop

Func IsBBAttackPage()
	Local $bRet = False
	If _ColorCheck(_GetPixelColor(30, 550 + $g_iMidOffsetY, True), Hex(0xCF0D0E, 6), 20) Then ;check red color on surrender button
		$bRet = True
	EndIf
	Return $bRet
EndFunc   ;==>IsBBAttackPage

Func BBGoldEnd($sLogText = "BBGoldEnd")
	If _CheckPixel($aBBGoldEnd, True, Default, $sLogText) Then
		SetDebugLog("Battle Ended", $COLOR_DEBUG2)
		Return True
	Else
		Return False
	EndIf
EndFunc   ;==>BBGoldEnd

Func IsClickOnPotions(ByRef $x, ByRef $y)
	Local $bResult = False
	SetDebugLog("IsClickOnPotions :" & $x & ", " & $y, $COLOR_INFO)
	If $y > 500 + $g_iBottomOffsetY Then
		$y = 500 + $g_iBottomOffsetY
		If $x < 460 Then
			$x = 460
		EndIf
		SetDebugLog("Adjusted Pixel :" & $x & ", " & $y, $COLOR_INFO)
		$bResult = True
	EndIf
	Return $bResult
EndFunc   ;==>IsClickOnPotions

Func ActivateBBTroopsSkills()
	If Not (GUICtrlRead($g_hChkBBUseTroopsSkills) = $GUI_CHECKED) Then Return ; Check real-time state
	If _Sleep(Random(2500, 4500, 100)) Then Return
	Local $locX[6] = [130, 200, 280, 350, 430, 510] ;slot x coordinates
	For $i = 0 To 5
		If Not $g_bRunState Then Return
		SetLog("Attempting to activate ability in slot: " & ($i + 1), $COLOR_DEBUG)
		PureClick($locX[$i] + Random(1, 5, 1), Random(660, 700, 1), 1, 10, "#0000")
		If _Sleep(Random(400, 800, 100)) Then Return
	Next
EndFunc  

Func GetBBDPPixelSection($XMiddle, $YMiddle, $x, $y)
Local $isLeft = ($x <= $XMiddle)
Local $isTop = ($y <= $YMiddle )
If $y > 565 Then Return 0 ;coord y overlap attackbar
If $isLeft Then
If $isTop Then Return 1 ; Top Left
Return 2 ; Bottom Left
EndIf
If $isTop Then Return 4 ; Top Right
Return 3 ; Bottom Right
EndFunc

Func GetSideFromPos($x, $y)
    If $x < 430 And $y < 250 Then Return 1
    If $x >= 430 And $y < 250 Then Return 2
    If $x >= 430 And $y >= 250 Then Return 3
    If $x < 430 And $y >= 250 Then Return 4
    Return 0
EndFunc

Func GetBestSide($aCounts, $iNumSides)
    Local $aSideCount[4][2]
    For $i = 1 To 4
        $aSideCount[$i-1][0] = $i
        $aSideCount[$i-1][1] = $aCounts[$i]
    Next
    _ArraySort($aSideCount, 1, 0, 0, 1) ; sort by count descending
    If $iNumSides = 1 Then
        Return $aSideCount[0][0]
    ElseIf $iNumSides = 2 Then
        ; Return the two best sides encoded as side1*10 + side2
        Local $iSide1 = $aSideCount[0][0]
        Local $iSide2 = $aSideCount[1][0]
        Return $iSide1 * 10 + $iSide2
    Else
        Return Random(1, 4, 1)
    EndIf
EndFunc

; Builder Base Defense detection functions
Func FindLavaLauncher()
    Local $aPositions[0][2] ; Initialize as empty 2D array
    Local $sImgPath = $g_sImgOpponentBuildingsBB & "LavaLauncher\"
    SetDebugLog("Searching for Lava Launcher in: " & $sImgPath, $COLOR_DEBUG)
    SetDebugLog("Search area: 50, 50, 800, 570", $COLOR_DEBUG)
    If QuickMIS("BC1", $sImgPath, 50, 50, 800, 570) Then
        SetDebugLog("QuickMIS found Lava Launcher at " & $g_iQuickMISX & "," & $g_iQuickMISY, $COLOR_DEBUG)
        ReDim $aPositions[1][2]
        $aPositions[0][0] = $g_iQuickMISX
        $aPositions[0][1] = $g_iQuickMISY
    Else
        SetDebugLog("QuickMIS did not find Lava Launcher", $COLOR_DEBUG)
        ; Keep as empty array [0][2]
    EndIf
    Return $aPositions
EndFunc

Func FindAirBombs()
    Local $aPositions[0][2]
    Local $sImgPath = $g_sImgOpponentBuildingsBB & "AirBomb\"
    SetDebugLog("Searching for Air Bomb in: " & $sImgPath, $COLOR_DEBUG)
    If QuickMIS("BC1", $sImgPath, 50, 50, 800, 570) Then
        SetDebugLog("QuickMIS found Air Bomb at " & $g_iQuickMISX & "," & $g_iQuickMISY, $COLOR_DEBUG)
        ReDim $aPositions[1][2]
        $aPositions[0][0] = $g_iQuickMISX
        $aPositions[0][1] = $g_iQuickMISY
    Else
        SetDebugLog("QuickMIS did not find Air Bomb", $COLOR_DEBUG)
    EndIf
    Return $aPositions
EndFunc

Func FindMegaTesla()
    Local $aPositions[0][2]
    Local $sImgPath = $g_sImgOpponentBuildingsBB & "MegaTesla\"
    SetDebugLog("Searching for Mega Tesla in: " & $sImgPath, $COLOR_DEBUG)
    If QuickMIS("BC1", $sImgPath, 50, 50, 800, 570) Then
        SetDebugLog("QuickMIS found Mega Tesla at " & $g_iQuickMISX & "," & $g_iQuickMISY, $COLOR_DEBUG)
        ReDim $aPositions[1][2]
        $aPositions[0][0] = $g_iQuickMISX
        $aPositions[0][1] = $g_iQuickMISY
    Else
        SetDebugLog("QuickMIS did not find Mega Tesla", $COLOR_DEBUG)
    EndIf
    Return $aPositions
EndFunc

Func FindGuardPost()
    Local $aPositions[0][2]
    Local $sImgPath = $g_sImgOpponentBuildingsBB & "GuardPost\"
    SetDebugLog("Searching for Guard Post in: " & $sImgPath, $COLOR_DEBUG)
    If QuickMIS("BC1", $sImgPath, 50, 50, 800, 570) Then
        SetDebugLog("QuickMIS found Guard Post at " & $g_iQuickMISX & "," & $g_iQuickMISY, $COLOR_DEBUG)
        ReDim $aPositions[1][2]
        $aPositions[0][0] = $g_iQuickMISX
        $aPositions[0][1] = $g_iQuickMISY
    Else
        SetDebugLog("QuickMIS did not find Guard Post", $COLOR_DEBUG)
    EndIf
    Return $aPositions
EndFunc

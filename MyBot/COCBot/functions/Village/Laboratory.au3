; #FUNCTION# ====================================================================================================================
; Name ..........: Laboratory
; Description ...:
; Syntax ........: Laboratory()
; Parameters ....:
; Return values .: None
; Author ........: summoner
; Modified ......: KnowJack (06/2015), Sardo (08/2015), Monkeyhunter(04/2016), MMHK(06/2018), Chilly-Chill (12/2019)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================
Local $iSlotWidth = 108, $iDistBetweenSlots = 14 ; use for logic to upgrade troops.. good for generic-ness
Local $iYMidPoint = Random(475, 485, 1) ;Space between rows in lab screen.  CHANGE ONLY WITH EXTREME CAUTION.
Local $iPicsPerPage = 12, $iPages = 6 ; used to know exactly which page the users choice is on
Local $sLabTroopsSection = "70,365,795,600"
Local $sLabTroopsSectionDiam = GetDiamondFromRect($sLabTroopsSection)

Func TestLaboratory()
	Local $bWasRunState = $g_bRunState
	Local $sWasLabUpgradeTime = $g_sLabUpgradeTime
	Local $sWasLabUpgradeEnable = $g_bAutoLabUpgradeEnable
	$g_bRunState = True
	$g_bAutoLabUpgradeEnable = True
	$g_sLabUpgradeTime = ""
	$g_bSilentSetDebugLog = False
	Local $Result = Laboratory(True)
	$g_bRunState = $bWasRunState
	$g_sLabUpgradeTime = $sWasLabUpgradeTime
	$g_bAutoLabUpgradeEnable = $sWasLabUpgradeEnable
	Return $Result
EndFunc   ;==>TestLaboratory

Func Laboratory($debug = False)

	If Not $g_bAutoLabUpgradeEnable Then Return ; Lab upgrade not enabled.

	If $g_iTownHallLevel < 3 Then
		SetLog("Townhall Lvl " & $g_iTownHallLevel & " has no Lab", $COLOR_ERROR)
		Return
	EndIf

	If Not $g_bRunState Then Return

	If $g_aiLaboratoryPos[0] = 0 Or $g_aiLaboratoryPos[1] = 0 Then
		SetLog("Laboratory Location unknown!", $COLOR_WARNING)
		LocateLab() ; Lab location unknown, so find it.
		If $g_aiLaboratoryPos[0] = 0 Or $g_aiLaboratoryPos[1] = 0 Then
			SetLog("Problem locating Laboratory, re-locate laboratory position before proceeding", $COLOR_ERROR)
			Return False
		EndIf
	EndIf

	If ChkUpgradeInProgress() Then Return False  ; see if we know about a upgrade in progress without checking the lab

	; Get updated village elixir and dark elixir values
	VillageReport()

	If UBound(decodeSingleCoord(FindImageInPlace2("GobBuilder", $g_sImgGobBuilder, 240, 0, 450, 60, True))) > 1 Then
		$GobBuilderPresent = True
		$GobBuilderOffsetRunning = 355
	Else
		$GobBuilderPresent = False
		$GobBuilderOffsetRunning = 0
	EndIf

	;Click Laboratory
	BuildingClickP($g_aiLaboratoryPos, "#0197")
	If _Sleep($DELAYLABORATORY5) Then Return ; Wait for window to open

	Local $sLabBuildingInfo = BuildingInfo(242, 475 + $g_iBottomOffsetY)
	If IsArray($sLabBuildingInfo) And UBound($sLabBuildingInfo) > 0 Then
		SetLog("Laboratory Level: " & $sLabBuildingInfo[2], $COLOR_INFO)
	EndIf

	If Not FindResearchButton() Then Return False ; cant start because we cannot find the research button

	If Not $GobBuilderPresent Then ; Just in case
		If UBound(decodeSingleCoord(FindImageInPlace2("GobBuilder", $g_sImgGobBuilderLab, 510, 140 + $g_iMidOffsetY, 575, 195 + $g_iMidOffsetY, True))) > 1 Or _
				UBound(decodeSingleCoord(FindImageInPlace2("GobBuilder", $g_sImgGobBuilder, 420, 115 + $g_iMidOffsetY, 490, 160 + $g_iMidOffsetY, True))) > 1 Then
			$GobBuilderPresent = True
			$GobBuilderOffsetRunning = 355
		EndIf
	EndIf

	If ChkLabUpgradeInProgress() Then
		CloseWindow()
		Return False ; cant start if something upgrading
	EndIf

	; Lab upgrade is not in progress and not upgreading, so we need to start a upgrade.
	Local $iCurPage = 1
	Local $sCostResult
	Global $bUserChoice = False

	; Single scan for all priorities
	Local $iBestPriority = -1
	Local $aBestCoords
	Local $sBestCost
	Local $iBestPage = -1
	Local $iCurrentPage = 1

	For $iPage = 1 To $iPages
		SetDebugLog("Scanning page " & $iPage & " for all priorities")
		Local $aPageUpgrades = findMultiple($g_sImgLabResearch, $sLabTroopsSectionDiam, $sLabTroopsSectionDiam, 0, 1000, 0, "objectname,objectpoints", True)

		If UBound($aPageUpgrades, 1) >= 1 Then
			For $iPriority = 0 To 2
				If $g_aiLabUpgradePriority[$iPriority] = 0 Then ContinueLoop
				If $iBestPriority <> -1 And $iPriority > $iBestPriority Then ContinueLoop ; already have a better (lower number) priority

				Local $sTargetShortName = $g_avLabTroops[$g_aiLabUpgradePriority[$iPriority]][2]
				For $i = 0 To UBound($aPageUpgrades, 1) - 1
					Local $aTempTroopArray = $aPageUpgrades[$i]
					If $aTempTroopArray[0] = $sTargetShortName Then
						Local $aCoords = decodeSingleCoord($aTempTroopArray[1])
						$sCostResult = GetLabCostResult($aCoords)
						If $sCostResult <> "" And StringSplit($sCostResult, "1")[0] <> StringLen($sCostResult) + 1 And StringSplit($sCostResult, "1")[1] <> "0" Then
							; can upgrade
							If $iBestPriority = -1 Or $iPriority < $iBestPriority Then
								$iBestPriority = $iPriority
								$aBestCoords = $aCoords
								$sBestCost = $sCostResult
								$iBestPage = $iPage
								SetLog("Found " & $g_avLabTroops[$g_aiLabUpgradePriority[$iPriority]][0] & " upgrade on page " & $iPage)
							EndIf
						EndIf
					EndIf
				Next
			Next
		EndIf

		; Navigate to next page if not last
		If $iPage < $iPages Then
			LabNextPage($iCurrentPage, $iPages, $iYMidPoint)
			$iCurrentPage += 1
			If _Sleep(1000) Then Return
		EndIf
	Next

	; If found a priority to upgrade
	If $iBestPriority <> -1 Then
		; Navigate to the page of the best upgrade by closing and reopening lab, then going forward
		LabGotoFirstPage()
		If _Sleep($DELAYLABORATORY5) Then Return
		BuildingClickP($g_aiLaboratoryPos, "#0197")
		If _Sleep($DELAYLABORATORY5) Then Return
		If Not FindResearchButton() Then Return False
		Local $iCurrentPage = 1
		For $i = 1 To $iBestPage - 1
			LabNextPage($iCurrentPage, $iPages, $iYMidPoint)
			$iCurrentPage += 1
			If _Sleep(1000) Then Return
		Next
		Return LaboratoryUpgrade($g_avLabTroops[$g_aiLabUpgradePriority[$iBestPriority]][0], $aBestCoords, $sBestCost, $debug)
	EndIf

	; No priorities upgraded, use any upgrade
	SetLog("No priority upgrades available, upgrading any available troop")
	
	; Any upgrade logic - backward search from last page to first
	Local $iFallbackCurPage = $iPages
	Local $iFallbackSearchPage = $iPages
	
	While ($iFallbackSearchPage >= 1)
		SetDebugLog("Searching any available upgrade on page " & $iFallbackSearchPage)
		Local $aPageUpgrades = findMultiple($g_sImgLabResearch, $sLabTroopsSectionDiam, $sLabTroopsSectionDiam, 0, 1000, 0, "objectname,objectpoints", True)
		If UBound($aPageUpgrades, 1) >= 1 Then ; if we found any troops
			SetDebugLog("Found upgrades on page #" & $iFallbackSearchPage & ", trying the first one")
			Local $aTempTroopArray = $aPageUpgrades[0] ; Take the first available upgrade

			Local $aCoords = decodeSingleCoord($aTempTroopArray[1])
			Local $sCostResult = GetLabCostResult($aCoords) ; get cost of the current upgrade option

			If $sCostResult = "" Then ; not enough resources
				SetLog("Not enough resources for upgrade", $COLOR_INFO)
				CloseWindow()
				Return False
			ElseIf StringSplit($sCostResult, "1")[0] = StringLen($sCostResult) + 1 Or StringSplit($sCostResult, "1")[1] = "0" Then ; max level if all ones returned from ocr or if the first letter is a 0.
				SetLog("All available troops are already at max level", $COLOR_INFO)
				CloseWindow()
				Return False
			Else
				Return LaboratoryUpgrade($aTempTroopArray[0], $aCoords, $sCostResult, $debug) ; return whether or not we successfully upgraded
			EndIf
		EndIf

		; Navigate to previous page for next search
		If $iFallbackSearchPage > 1 Then
			LabPreviousPage($iFallbackCurPage, $iPages, $iYMidPoint)
			$iFallbackCurPage -= 1
			If _Sleep(1000) Then Return
		EndIf
		
		$iFallbackSearchPage -= 1
	WEnd

	; If We got to here without returning, then nothing available for upgrade
	SetLog("Nothing available for upgrade at the moment, try again later")
	CloseWindow()

	Return False ; No upgrade started
EndFunc   ;==>Laboratory

; start a given upgrade
Func LaboratoryUpgrade($name, $aCoords, $sCostResult, $debug = False)
	SetLog($name & " upgrade cost: " & _NumberFormat($sCostResult, True), $COLOR_INFO)
	ClickP($aCoords) ; click troop
	If _Sleep(2000) Then Return

	If Not (SetLabUpgradeTime($name)) Then
		SetDebugLog("Couldn't read upgrade time, continue anyway", $COLOR_ERROR)
	EndIf
	If _Sleep($DELAYLABUPGRADE1) Then Return

	LabStatusGUIUpdate()
	If $debug = True Then ; if debugging, do not actually click it
		SetLog("[debug mode] - Start Upgrade, Click (" & 630 & "," & 565 + $g_iMidOffsetY & ")", $COLOR_ACTION)
		CloseWindow()
		Return True ; return true as if we really started a upgrade
	Else
		Click(630, 545 + $g_iMidOffsetY, 1, 120, "#0202") ; Everything is good - Click the upgrade button
		If _Sleep(500) Then Return
		If isGemOpen(True) = False Then ; check for gem window
			; success
			SetLog($name & " upgrade in your laboratory started with success!", $COLOR_SUCCESS)
			;If doing a user specific upgrade, set to "any" for next time.
			;Bad if user wanted to upgrade it multiple levels.
			If $bUserChoice Then
				SetLog("Clearing user's upgrade choice", $COLOR_INFO)
				;HArchH Set the global that gets saved to building.ini
				$g_iCmbLaboratory = 0 ;Set global
				_GUICtrlComboBox_SetCurSel($g_hCmbLaboratory, $g_iCmbLaboratory) ;Apply to the GUI in case it gets saved again.
				SaveBuildingConfig() ;Try to save for the future.
			EndIf
			If _Sleep(350) Then Return
			CloseWindow2()
			If _Sleep(1000) Then Return
			PushMsg("LabSuccess")
			ChkLabUpgradeInProgress($name)
			If _Sleep($DELAYLABUPGRADE2) Then Return
			CloseWindow()
			Return True ; upgrade started
		Else
			SetLog("Oops, Gems required for " & $name & " Upgrade, try again", $COLOR_ERROR)
			Return False
		EndIf
	EndIf
EndFunc   ;==>LaboratoryUpgrade

; get the time for the selected upgrade
Func SetLabUpgradeTime($sTrooopName)
	Local $Result = getLabUpgradeTime2(730, 544 + $g_iMidOffsetY) ; Try to read white text showing time for upgrade
	Local $iLabFinishTime = ConvertOCRTime("Lab Time", $Result, False)
	SetDebugLog($sTrooopName & " Upgrade OCR Time = " & $Result & ", $iLabFinishTime = " & $iLabFinishTime & " m", $COLOR_INFO)
	Local $StartTime = _NowCalc() ; what is date:time now
	SetDebugLog($sTrooopName & " Upgrade Started @ " & $StartTime, $COLOR_SUCCESS)
	If $iLabFinishTime > 0 Then
		$g_sLabUpgradeTime = _DateAdd('n', Ceiling($iLabFinishTime), $StartTime)
		; Log moved to ChkLabUpgradeInProgress to avoid duplicate
		$g_iLaboratoryElixirCost = 0
		$g_iLaboratoryDElixirCost = 0
	Else
		SetLog("Error processing upgrade time required, try again!", $COLOR_WARNING)
		Return False
	EndIf
	If ProfileSwitchAccountEnabled() Then SwitchAccountVariablesReload("Save") ; saving $asLabUpgradeTime[$g_iCurAccount] = $g_sLabUpgradeTime for instantly displaying in multi-stats
	Return True ; success
EndFunc   ;==>SetLabUpgradeTime

; get the cost of a upgrade based on its coords
; find image slot that we found so that we can read the cost to see if we can upgrade it... slots read 1-12 top to bottom so barb = 1, arch = 2, giant = 3, etc...
Func GetLabCostResult($aCoords)
	SetDebugLog("Getting lab cost")
	SetDebugLog("$iYMidPoint=" & $iYMidPoint)
	Local $iCurSlotOnPage, $iCurSlotsToTheRight, $sCostResult
	$iCurSlotsToTheRight = Ceiling((Int($aCoords[0]) - Int(StringSplit($sLabTroopsSection, ",")[1])) / ($iSlotWidth + $iDistBetweenSlots))
	If Int($aCoords[1]) < $iYMidPoint Then ; first row
		SetDebugLog("First row")
		$iCurSlotOnPage = 2 * $iCurSlotsToTheRight - 1
		SetDebugLog("$iCurSlotOnPage=" & $iCurSlotOnPage)
		$sCostResult = getLabUpgrdResourceWhtNew(Int(StringSplit($sLabTroopsSection, ",")[1]) + ($iCurSlotsToTheRight - 1) * ($iSlotWidth + $iDistBetweenSlots) + 4, 420 + $g_iMidOffsetY)
		If $sCostResult = "" Then
			Local $XCoord = Int(StringSplit($sLabTroopsSection, ",")[1]) + ($iCurSlotsToTheRight - 1) * ($iSlotWidth + $iDistBetweenSlots) + 4
			Local $YCoord = 420 + $g_iMidOffsetY
			If QuickMIS("BC1", $g_sImgElixirDrop, $XCoord + 77, $YCoord - 4, $XCoord + 110, $YCoord + 18) Then
				Local $g_iLaboratoryElixirCostOld = $g_iLaboratoryElixirCost
				Local $g_iLaboratoryElixirCostNew = getLabUpgrdResourceRed($XCoord, $YCoord)
				If $g_iLaboratoryElixirCostNew <= $g_iLaboratoryElixirCostOld Or $g_iLaboratoryElixirCostOld = 0 Then $g_iLaboratoryElixirCost = $g_iLaboratoryElixirCostNew
			Else
				Local $g_iLaboratoryDElixirCostOld = $g_iLaboratoryDElixirCost
				Local $g_iLaboratoryDElixirCostNew = getLabUpgrdResourceRed($XCoord, $YCoord)
				If $g_iLaboratoryDElixirCostNew <= $g_iLaboratoryDElixirCostOld Or $g_iLaboratoryDElixirCostOld = 0 Then $g_iLaboratoryDElixirCost = $g_iLaboratoryDElixirCostNew
			EndIf
		EndIf
	Else ; second row
		SetDebugLog("Second row")
		$iCurSlotOnPage = 2 * $iCurSlotsToTheRight
		SetDebugLog("$iCurSlotOnPage=" & $iCurSlotOnPage)
		$sCostResult = getLabUpgrdResourceWhtNew(Int(StringSplit($sLabTroopsSection, ",")[1]) + ($iCurSlotsToTheRight - 1) * ($iSlotWidth + $iDistBetweenSlots) + 4, 543 + $g_iMidOffsetY)
		If $sCostResult = "" Then
			Local $XCoord = Int(StringSplit($sLabTroopsSection, ",")[1]) + ($iCurSlotsToTheRight - 1) * ($iSlotWidth + $iDistBetweenSlots) + 4
			Local $YCoord = 543 + $g_iMidOffsetY
			If QuickMIS("BC1", $g_sImgElixirDrop, $XCoord + 77, $YCoord - 4, $XCoord + 110, $YCoord + 18) Then
				Local $g_iLaboratoryElixirCostOld = $g_iLaboratoryElixirCost
				Local $g_iLaboratoryElixirCostNew = getLabUpgrdResourceRed($XCoord, $YCoord)
				If $g_iLaboratoryElixirCostNew <= $g_iLaboratoryElixirCostOld Or $g_iLaboratoryElixirCostOld = 0 Then $g_iLaboratoryElixirCost = $g_iLaboratoryElixirCostNew
			Else
				Local $g_iLaboratoryDElixirCostOld = $g_iLaboratoryDElixirCost
				Local $g_iLaboratoryDElixirCostNew = getLabUpgrdResourceRed($XCoord, $YCoord)
				If $g_iLaboratoryDElixirCostNew <= $g_iLaboratoryDElixirCostOld Or $g_iLaboratoryDElixirCostOld = 0 Then $g_iLaboratoryDElixirCost = $g_iLaboratoryDElixirCostNew
			EndIf
		EndIf
	EndIf
	SetDebugLog("Cost found is " & $sCostResult)
	Return $sCostResult
EndFunc   ;==>GetLabCostResult

Func LabNextPage($iCurPage, $iPages, $iYMidPoint)
	If $iCurPage >= $iPages Then Return ; nothing left to scroll
	SetDebugLog("Drag to next full page")
	ClickDrag(720, 480, 100, 480, 10)
EndFunc   ;==>LabNextPage

Func LabPreviousPage($iCurPage, $iPages, $iYMidPoint)
	If $iCurPage <= 1 Then Return ; nothing left to scroll back
	SetDebugLog("Drag to previous full page from page " & $iCurPage)
	; Always drag from left to right to go back pages
	ClickDrag(100, 480, 720, 480, 10)
EndFunc   ;==>LabPreviousPage

Func LabGotoFirstPage()
	SetDebugLog("Going back to first page by closing lab window")
	CloseWindow()
	If _Sleep($DELAYLABORATORY3) Then Return
EndFunc   ;==>LabGotoFirstPage

; check the lab to see if something is upgrading in the lab already
Func ChkLabUpgradeInProgress($name = "")
	; check for upgrade in process - look for green in finish upgrade with gems button
	SetDebugLog("_GetPixelColor(X, Y): " & _GetPixelColor(775 - $GobBuilderOffsetRunning, 135 + $g_iMidOffsetY, True) & ":A1CA6B", $COLOR_DEBUG)
	If _ColorCheck(_GetPixelColor(775 - $GobBuilderOffsetRunning, 135 + $g_iMidOffsetY, True), Hex(0xA1CA6B, 6), 20) Then ; Look for light green in upper right corner of lab window.
		SetLog("Laboratory upgrade in progress, waiting for completion")
		If _Sleep($DELAYLABORATORY2) Then Return
		; upgrade in process and time not recorded so update completion time!
		If $GobBuilderPresent Then
			Local $sLabTimeOCR = getRemainTLaboratoryGob(210, 190 + $g_iMidOffsetY)
		Else
			Local $sLabTimeOCR = getRemainTLaboratory2(250, 210 + $g_iMidOffsetY)
		EndIf
		Local $iLabFinishTime = ConvertOCRTime("Lab Time", $sLabTimeOCR, False) + 1
		SetDebugLog("$sLabTimeOCR: " & $sLabTimeOCR & ", $iLabFinishTime = " & $iLabFinishTime & " m")
		If $iLabFinishTime > 0 Then
			$g_sLabUpgradeTime = _DateAdd('n', Ceiling($iLabFinishTime), _NowCalc())
			If @error Then _logErrorDateAdd(@error)
			SetLog("Research will finish in " & $sLabTimeOCR & " (" & $g_sLabUpgradeTime & ")")
			$g_iLaboratoryElixirCost = 0
			$g_iLaboratoryDElixirCost = 0
			LabStatusGUIUpdate() ; Update GUI flag
		ElseIf $g_bDebugSetLog Then
			SetLog("Invalid getRemainTLaboratory OCR", $COLOR_DEBUG)
		EndIf
		If ProfileSwitchAccountEnabled() Then SwitchAccountVariablesReload("Save") ; saving $asLabUpgradeTime[$g_iCurAccount] = $g_sLabUpgradeTime for instantly displaying in multi-stats
		Return True
	EndIf
	Return False ; returns False if no upgrade in progress
EndFunc   ;==>ChkLabUpgradeInProgress

; checks our global variable to see if we know of something already upgrading
Func ChkUpgradeInProgress()
	Local $TimeDiff ; time remaining on lab upgrade
	If $g_sLabUpgradeTime <> "" Then $TimeDiff = _DateDiff("n", _NowCalc(), $g_sLabUpgradeTime) ; what is difference between end time and now in minutes?
	If @error Then _logErrorDateDiff(@error)
	SetDebugLog($g_avLabTroops[$g_iCmbLaboratory][0] & " Lab end time: " & $g_sLabUpgradeTime & ", DIFF= " & $TimeDiff, $COLOR_DEBUG)

	If Not $g_bRunState Then Return
	If $TimeDiff <= 0 Then
		SetLog("Checking available troop upgrades")
	Else
		SetLog("Laboratory upgrade in progress, waiting for completion")
		$g_iLaboratoryElixirCost = 0
		$g_iLaboratoryDElixirCost = 0
		Return True
	EndIf
	Return False ; we currently do not know of any upgrades in progress
EndFunc   ;==>ChkUpgradeInProgress

; Find Research Button
Func FindResearchButton()
	Local $aResearchButton = findButton("Research", Default, 1, True)
	If IsArray($aResearchButton) And UBound($aResearchButton, 1) = 2 Then
		If $g_bDebugImageSave Then SaveDebugImage("LabUpgrade") ; Debug Only
		ClickP($aResearchButton)
		If _Sleep($DELAYLABORATORY1) Then Return ; Wait for window to open
		Return True
	Else
		SetLog("Laboratory research button not found!", $COLOR_ERROR)
		ClearScreen()
		Return False
	EndIf
EndFunc   ;==>FindResearchButton

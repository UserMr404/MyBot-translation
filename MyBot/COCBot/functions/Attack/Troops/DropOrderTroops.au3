; #FUNCTION# ====================================================================================================================
; Name ..........: Custom Drop Troops
; Description ...: This file contains the Sequence that runs all MBR Bot
; Author ........: Kychera (05-2017)
; Modified ......: NguyenAnhHD (12-2017)
; Remarks .......: This file is part of MyBot, previously known as ClashGameBot. Copyright 2015-2025
;                  MyBot is distributed under the terms of the GNU GPL
; Related .......:
; Link ..........: https://github.com/MyBotRun/MyBot/wiki
; Example .......: No
; ===============================================================================================================================

Func MatchTroopDropName($Num)
	Switch $g_aiCmbCustomDropOrder[$Num]
		Case 0 To 53
			Return $g_aiCmbCustomDropOrder[$Num]
		Case 54
			Return "CC"
		Case 55
			Return "HEROES"
	EndSwitch
EndFunc   ;==>MatchTroopDropName

Func MatchSlotsPerEdge($Num)
	; 0 = spread in all deploy points each side , 1 = one deploy point , 2 = 2 deploy points
	Switch $g_aiCmbCustomDropOrder[$Num]
		Case 0 ;$eBarb
			Return 0
		Case 1 ;$eSBarb
			Return 0
		Case 2 ;$eArch
			Return 0
		Case 3 ;$eSArch
			Return 0
		Case 4 ;$eGiant
			Return $g_iSlotsGiants
		Case 5 ;$eSGiant
			Return $g_iSlotsGiants
		Case 6 ;$eGobl
			Return 0
		Case 7 ;$eSGobl
			Return 0
		Case 8 ;$eWall
			Return 1
		Case 9 ;$eSWall
			Return 1
		Case 10 ;$eBall
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 11 ;$eRBall
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 12 ;$eWiza
			Return 0
		Case 13 ;$eSWiza
			Return 0
		Case 14 ;$eHeal
			Return 1
		Case 15 ;$eDrag
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 16 ;$eSDrag
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 17 ;$ePekk
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 1
			Else
				Return 2
			EndIf
		Case 18 ;$eBabyD
			Return 1
		Case 19 ;$eInfernoD
			Return 1
		Case 20 ;$eMine
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 1
			EndIf
		Case 21 ;$eSMine
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 1
			EndIf
		Case 22 ; $eEDrag
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 23 ; $eYeti
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 24 ; $eSYeti
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 25 ; $eRDrag
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 26 ; $eETitan
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 27 ; $eRootR
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf
		Case 28 ; $eThrower
			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
				Return 0
			Else
				Return 2
			EndIf	
 		Case 29 ;$eMini
 			Return 0
		Case 30 ;$eSMini
 			Return 0
		Case 31 ;$eHogs
 			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
 				Return 1
 			Else
 				Return 2
 			EndIf
		Case 32 ;$eSHogs
 			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
 				Return 1
 			Else
 				Return 2
 			EndIf
		Case 33 ;$eValk
 			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
 				Return 0
 			Else
 				Return 2
 			EndIf
		Case 34 ;$eSValk
 			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
 				Return 0
 			Else
 				Return 2
 			EndIf
		Case 35 ;$eGole
 			Return 2
		Case 36 ;$eWitc
 			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
 				Return 1
 			Else
 				Return 2
 			EndIf
		Case 37 ;$eSWitc
 			If $g_iMatchMode = $LB And $g_aiAttackStdDropSides[$LB] = 5 Then
 				Return 1
 			Else
 				Return 2
 			EndIf
		Case 38 ;$eLava
 			Return 2
		Case 39 ;$eIceH
 			Return 2
		Case 40 ;$eBowl
 			Return 0
		Case 41 ;$eSBowl
 			Return 0
		Case 42 ;$eIceG
 			Return 2
		Case 43 ;$eHunt
 			Return 0
		Case 44 ;$eAppWard
 			Return 0
		Case 45 ;$eDruid
 			Return 0
		Case 46 ;$eSYeti
 			Return 0
		Case 47 ;$eIceWiz
 			Return 0
		Case 48 ;$eGGiant
 			Return 0
		Case 49 ;$eAzureDragon
 			Return 0
		Case 50 ;$eFirecracker
 			Return 0
		Case 51 ;$eRamRider
 			Return 0
		Case 52 ;$eFurn
 			Return 0
		Case 53 ;$eFurn
 			Return 0
		Case 54 ;CC
 			Return 1
		Case 55 ;HEROES
 			Return 1
 	EndSwitch
 EndFunc   ;==>MatchSlotsPerEdge

Func MatchSidesDrop($Num)
	Switch $g_aiCmbCustomDropOrder[$Num]
		Case $eBarb To $eFurn
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 0 Then Return 1
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 1 Then Return 2
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 2 Then Return 3
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 3 Then Return 4
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 4 Then Return 4
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 5 Then Return 1
			If $g_aiAttackStdDropSides[$g_iMatchMode] = 6 Then Return 1
		Case 54
			Return 1 ;CC
		Case 55
			Return 1 ;HEROES
	EndSwitch
EndFunc   ;==>MatchSidesDrop

Func MatchTroopWaveNb($Num)
	Return 1
EndFunc   ;==>MatchTroopWaveNb

; ===============================================================================
;
; Program Name:     MsgBoxWizard()
; Description:      Generate the MessageBox function code according to the user
;                   choices
; Requirement(s):   None
; Return Value(s):  None
; Author(s):        Giuseppe Criaco <gcriaco@quipo.it>
;
; ===============================================================================
;
#include <EditConstants.au3>
#include <GUIConstantsEx.au3>
#include <WindowsStylesConstants.au3>

Global $g_idRdo_OptWarning, $g_idRdo_OptInfo, $g_idRdo_OptCritical, $g_idRdo_OptQuestion
Global $g_idRdo_OptSysModal, $g_idRdo_OptTaskModal
Global $g_idRdo_OptOkCancel, $g_idRdo_OptYesNo, $g_idRdo_OptYesNoCancel, $g_idRdo_OptAbortRetryIgnore
Global $g_idRdo_OptRetryCancel, $g_idRdo_OptCancelRetryContinue, $g_idRdo_OptTopMost
Global $g_idRdo_OptRightJust, $g_idRdo_OptSecond, $g_idRdo_OptThird

_Main()
Exit

Func _Main()
	Local $iFlag, $idButton, $sMsgBox, $asMsgText
	Local $idInp_TITLE, $idEdt_TEXT, $idInp_Timeout, $idRdo_OptOK
	Local $idBtn_COPY, $idBtn_EXIT, $idBtn_PREVIEW, $iMSG, $sText

	GUICreate("MsgBox Wizard v.1.0", 440, 540, 100, 100) ; will create a dialog box

	GUICtrlCreateLabel("Title", 10, 5, 30)
	$idInp_TITLE = GUICtrlCreateInput("", 10, 20, 420, 20)
	GUICtrlSetState(-1, $GUI_FOCUS)
	GUICtrlSetTip(-1, "The title of the message box.")
	GUICtrlCreateLabel("Text", 10, 50, 30)
	$idEdt_TEXT = GUICtrlCreateEdit("", 10, 65, 420, 100, $ES_AUTOVSCROLL + $WS_VSCROLL + $ES_MULTILINE + $ES_WANTRETURN)
	GUICtrlSetTip(-1, "The text of the message box.")

	GUICtrlCreateGroup("Icons", 10, 170, 200, 130)
	$g_idRdo_OptWarning = GUICtrlCreateRadio("Warning", 20, 190, 100, 20)
	GUICtrlSetState(-1, $GUI_CHECKED)
	$g_idRdo_OptInfo = GUICtrlCreateRadio("Informational", 20, 210, 100, 20)
	$g_idRdo_OptCritical = GUICtrlCreateRadio("Critical", 20, 230, 100, 20)
	$g_idRdo_OptQuestion = GUICtrlCreateRadio("Question", 20, 250, 100, 20)
	GUICtrlCreateRadio("None", 20, 270, 100, 20)
	GUICtrlCreateGroup("", -99, -99, 1, 1) ;close group

	GUICtrlCreateGroup("Modality", 10, 310, 200, 90)
	GUICtrlCreateRadio("Application", 20, 330, 100, 20)
	GUICtrlSetState(-1, $GUI_CHECKED)
	$g_idRdo_OptSysModal = GUICtrlCreateRadio("System Modal", 20, 350, 100, 20)
	$g_idRdo_OptTaskModal = GUICtrlCreateRadio("Task Modal", 20, 370, 100, 20)
	GUICtrlCreateGroup("", -99, -99, 1, 1) ;close group

	GUICtrlCreateGroup("Buttons", 230, 170, 200, 170)
	$idRdo_OptOK = GUICtrlCreateRadio("OK", 240, 190, 100, 20)
	GUICtrlSetState(-1, $GUI_CHECKED)
	$g_idRdo_OptOkCancel = GUICtrlCreateRadio("OK, Cancel", 240, 210, 100, 20)
	$g_idRdo_OptYesNo = GUICtrlCreateRadio("Yes, No", 240, 230, 100, 20)
	$g_idRdo_OptYesNoCancel = GUICtrlCreateRadio("Yes, No, Cancel", 240, 250, 100, 20)
	$g_idRdo_OptAbortRetryIgnore = GUICtrlCreateRadio("Abort, Retry, Ignore", 240, 270, 120, 20)
	$g_idRdo_OptRetryCancel = GUICtrlCreateRadio("Retry, Cancel", 240, 290, 100, 20)
	$g_idRdo_OptCancelRetryContinue = GUICtrlCreateRadio("Cancel, Retry, Continue", 240, 310, 130, 20)
	GUICtrlCreateGroup("", -99, -99, 1, 1) ;close group

	GUICtrlCreateGroup("Miscellaneous", 10, 410, 200, 90)
	GUICtrlCreateRadio("Nothing", 20, 430, 100, 20)
	GUICtrlSetState(-1, $GUI_CHECKED)
	$g_idRdo_OptTopMost = GUICtrlCreateRadio("Top-most attribute set", 20, 450, 130, 20)
	$g_idRdo_OptRightJust = GUICtrlCreateRadio("Right-justified title/text", 20, 470, 150, 20)
	GUICtrlCreateGroup("", -99, -99, 1, 1) ;close group

	GUICtrlCreateGroup("Default Buttons", 230, 350, 200, 90)
	Local $idRdo_OptFirst = GUICtrlCreateRadio("First Button", 240, 370, 130, 20)
	GUICtrlSetState(-1, $GUI_CHECKED)
	$g_idRdo_OptSecond = GUICtrlCreateRadio("Second Button", 240, 390, 130, 20)
	GUICtrlSetState(-1, $GUI_DISABLE)
	$g_idRdo_OptThird = GUICtrlCreateRadio("Third Button", 240, 410, 130, 20)
	GUICtrlSetState(-1, $GUI_DISABLE)
	GUICtrlCreateGroup("", -99, -99, 1, 1) ;close group

	GUICtrlCreateGroup("Timeout", 230, 450, 200, 50)
	$idInp_Timeout = GUICtrlCreateInput("", 240, 470, 100, 20, $ES_NUMBER)
	GUICtrlSetTip(-1, "Optional Timeout in seconds. After the timeout has elapsed the message box will be automatically closed.")
	GUICtrlCreateGroup("", -99, -99, 1, 1) ;close group

	$idBtn_PREVIEW = GUICtrlCreateButton("&Preview", 10, 510, 100)
	GUICtrlSetTip(-1, "Show the MessageBox")
	$idBtn_COPY = GUICtrlCreateButton("&Copy", 120, 510, 100)
	GUICtrlSetTip(-1, "Copy the generated AutoIt code to the Clipboard")
	$idBtn_EXIT = GUICtrlCreateButton("&Exit", 230, 510, 100)
	GUICtrlSetTip(-1, "Quit the program")

	$idButton = $idRdo_OptOK

	GUISetState() ; will display an empty dialog box

	; Run the GUI until the dialog is closed
	While 1
		$iMSG = GUIGetMsg()
		Select
			Case $iMSG = $GUI_EVENT_CLOSE Or $iMSG = $idBtn_EXIT
				Exit

			Case $iMSG = $idRdo_OptOK
				$idButton = $idRdo_OptOK
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_DISABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_DISABLE)

			Case $iMSG = $g_idRdo_OptOkCancel
				$idButton = $g_idRdo_OptOkCancel
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_DISABLE)

			Case $iMSG = $g_idRdo_OptYesNo
				$idButton = $g_idRdo_OptYesNo
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_DISABLE)

			Case $iMSG = $g_idRdo_OptYesNoCancel
				$idButton = $g_idRdo_OptYesNoCancel
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_ENABLE)

			Case $iMSG = $g_idRdo_OptAbortRetryIgnore
				$idButton = $g_idRdo_OptAbortRetryIgnore
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_ENABLE)

			Case $iMSG = $g_idRdo_OptRetryCancel
				$idButton = $g_idRdo_OptRetryCancel
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_DISABLE)

			Case $iMSG = $g_idRdo_OptCancelRetryContinue
				$idButton = $g_idRdo_OptCancelRetryContinue
				GUICtrlSetState($idRdo_OptFirst, $GUI_CHECKED)
				GUICtrlSetState($idRdo_OptFirst, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptSecond, $GUI_ENABLE)
				GUICtrlSetState($g_idRdo_OptThird, $GUI_ENABLE)

			Case $iMSG = $idBtn_PREVIEW
				MsgBox(_SetFlag($iFlag), GUICtrlRead($idInp_TITLE), GUICtrlRead($idEdt_TEXT), GUICtrlRead($idInp_Timeout))

			Case $iMSG = $idBtn_COPY
				$asMsgText = StringSplit(GUICtrlRead($idEdt_TEXT), @CRLF, 1)
				If $asMsgText[0] = 1 Then
					$sText = GUICtrlRead($idEdt_TEXT)
				Else
					$sText = $asMsgText[1]

					For $iCtr = 2 To $asMsgText[0]
						$sText = $sText & Chr(34) & " & @CRLF & " & Chr(34) & $asMsgText[$iCtr]
					Next

				EndIf

				Select
					Case $idButton = $idRdo_OptOK
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"   Case Else                ;OK" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf

					Case $idButton = $g_idRdo_OptOkCancel
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 1 ;OK" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 2 ;Cancel" & @CRLF & @CRLF & _
									"EndSelect"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 1  ;OK" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 2  ;Cancel" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf

					Case $idButton = $g_idRdo_OptYesNo
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 6 ;Yes" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 7 ;No" & @CRLF & @CRLF & _
									"EndSelect"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 6  ;Yes" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 7  ;No" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf

					Case $idButton = $g_idRdo_OptYesNoCancel
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 6 ;Yes" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 7 ;No" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 2 ;Cancel" & @CRLF & @CRLF & _
									"EndSelect"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 6  ;Yes" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 7  ;No" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 2  ;Cancel" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf

					Case $idButton = $g_idRdo_OptAbortRetryIgnore
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 3 ;Abort" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 4 ;Retry" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 5 ;Ignore" & @CRLF & @CRLF & _
									"EndSelect"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 3  ;Abort" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 4  ;Retry" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 5  ;Ignore" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf

					Case $idButton = $g_idRdo_OptRetryCancel
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 4 ;Retry" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 2 ;Cancel" & @CRLF & @CRLF & _
									"EndSelect"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 4  ;Retry" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 2  ;Cancel" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf

					Case $idButton = $g_idRdo_OptCancelRetryContinue
						If GUICtrlRead($idInp_Timeout) = "" Then
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 2 ;Cancel" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 10 ;Try Again" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 11 ;Continue" & @CRLF & @CRLF & _
									"EndSelect"
						Else
							$sMsgBox = "Dim $iMsgBoxAnswer" & @CRLF & _
									"$iMsgBoxAnswer = MsgBox(" & _SetFlag($iFlag) & "," & Chr(34) & GUICtrlRead($idInp_TITLE) & Chr(34) & "," _
									 & Chr(34) & $sText & Chr(34) & "," & GUICtrlRead($idInp_Timeout) & ")" & @CRLF & _
									"Select" & @CRLF & _
									"   Case $iMsgBoxAnswer = 2  ;Cancel" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 10 ;Try Again" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = 11 ;Continue" & @CRLF & @CRLF & _
									"   Case $iMsgBoxAnswer = -1 ;Timeout" & @CRLF & @CRLF & _
									"EndSelect"
						EndIf
				EndSelect

				ClipPut($sMsgBox)
		EndSelect

	WEnd
EndFunc   ;==>_Main

; ===============================================================================
;
; Function Name:    _SetFlag()
; Description:      Set the flag that indicates the type of message box and the
;                   possible button combinations.
; Parameter(s):     $iFlag        - Flag
; Requirement(s):   None
; Return Value(s):  On Success - Returns the message box flag
;                   None
; Author(s):        Giuseppe Criaco <gcriaco@quipo.it>
;
; ===============================================================================
;

Func _SetFlag($iFlag)
	$iFlag = 0

	;Icons
	Select
		Case GUICtrlRead($g_idRdo_OptWarning) = $GUI_CHECKED
			$iFlag = $iFlag + 48
		Case GUICtrlRead($g_idRdo_OptInfo) = $GUI_CHECKED
			$iFlag = $iFlag + 64
		Case GUICtrlRead($g_idRdo_OptCritical) = $GUI_CHECKED
			$iFlag = $iFlag + 16
		Case GUICtrlRead($g_idRdo_OptQuestion) = $GUI_CHECKED
			$iFlag = $iFlag + 32
	EndSelect

	;Modality
	Select
		Case GUICtrlRead($g_idRdo_OptSysModal) = $GUI_CHECKED
			$iFlag = $iFlag + 4096
		Case GUICtrlRead($g_idRdo_OptTaskModal) = $GUI_CHECKED
			$iFlag = $iFlag + 8192
	EndSelect

	;Buttons
	Select
		Case GUICtrlRead($g_idRdo_OptOkCancel) = $GUI_CHECKED
			$iFlag = $iFlag + 1
		Case GUICtrlRead($g_idRdo_OptYesNo) = $GUI_CHECKED
			$iFlag = $iFlag + 4
		Case GUICtrlRead($g_idRdo_OptYesNoCancel) = $GUI_CHECKED
			$iFlag = $iFlag + 3
		Case GUICtrlRead($g_idRdo_OptAbortRetryIgnore) = $GUI_CHECKED
			$iFlag = $iFlag + 2
		Case GUICtrlRead($g_idRdo_OptRetryCancel) = $GUI_CHECKED
			$iFlag = $iFlag + 5
		Case GUICtrlRead($g_idRdo_OptCancelRetryContinue) = $GUI_CHECKED
			$iFlag = $iFlag + 6
	EndSelect

	;Miscellaneous
	Select
		Case GUICtrlRead($g_idRdo_OptTopMost) = $GUI_CHECKED
			$iFlag = $iFlag + 262144
		Case GUICtrlRead($g_idRdo_OptRightJust) = $GUI_CHECKED
			$iFlag = $iFlag + 5244288
	EndSelect

	;Default Buttons
	Select
		Case GUICtrlRead($g_idRdo_OptSecond) = $GUI_CHECKED
			$iFlag = $iFlag + 256
		Case GUICtrlRead($g_idRdo_OptThird) = $GUI_CHECKED
			$iFlag = $iFlag + 512
	EndSelect

	Return $iFlag
EndFunc   ;==>_SetFlag

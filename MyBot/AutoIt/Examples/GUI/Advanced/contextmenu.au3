#include <GUIConstantsEx.au3>
#include <MsgBoxConstants.au3>

_Example()
Exit

Func _Example()
	GUICreate("GUI with simple context menu", 300, 200)

	Local $idCtx_Track = GUICtrlCreateContextMenu()
	Local $idMni_About = GUICtrlCreateMenuItem("About", $idCtx_Track)
	; next one creates a menu separator (line)
	GUICtrlCreateMenuItem("", $idCtx_Track)
	Local $idMni_Exit = GUICtrlCreateMenuItem("Exit", $idCtx_Track)

	GUISetState()

	While 1
		Local $iMsg = GUIGetMsg()
		If $iMsg = $idMni_Exit Or $iMsg = $GUI_EVENT_CLOSE Or $iMsg = -1 Then ExitLoop
		If $iMsg = $idMni_About Then MsgBox($MB_SYSTEMMODAL, "About", "A simple example with a context menu!")
	WEnd
EndFunc   ;==>_Example

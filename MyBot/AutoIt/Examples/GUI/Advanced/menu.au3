#include <Constants.au3>
#include <GUIConstantsEx.au3>

_Main()
Exit

Func _Main()
	Local $idMnu_File, $idMni_File, $idMnu_RecentFiles, $idMni_Separator1
	Local $idMni_Exit, $idMnu_Help, $idMni_About, $idBtn_Ok, $idBtn_Cancel
	Local $iMsg, $sFile
	#forceref $idMni_Separator1

	GUICreate("GUI menu", 300, 200)

	$idMnu_File = GUICtrlCreateMenu("File")
	$idMni_File = GUICtrlCreateMenuItem("Open...", $idMnu_File)
	$idMnu_RecentFiles = GUICtrlCreateMenu("Recent Files", $idMnu_File)
	$idMni_Separator1 = GUICtrlCreateMenuItem("", $idMnu_File)
	$idMni_Exit = GUICtrlCreateMenuItem("Exit", $idMnu_File)
	$idMnu_Help = GUICtrlCreateMenu("?")
	$idMni_About = GUICtrlCreateMenuItem("About", $idMnu_Help)

	$idBtn_Ok = GUICtrlCreateButton("OK", 50, 130, 70, 20)

	$idBtn_Cancel = GUICtrlCreateButton("Cancel", 180, 130, 70, 20)

	GUISetState()

	While 1
		$iMsg = GUIGetMsg()

		Select
			Case $iMsg = $GUI_EVENT_CLOSE Or $iMsg = $idBtn_Cancel
				ExitLoop

			Case $iMsg = $idMni_File
				$sFile = FileOpenDialog("Choose file...", @TempDir, "All (*.*)")
				If @error <> 1 Then GUICtrlCreateMenuItem($sFile, $idMnu_RecentFiles)

			Case $iMsg = $idMni_Exit
				ExitLoop

			Case $iMsg = $idBtn_Ok
				MsgBox($MB_SYSTEMMODAL, "Click", "You clicked OK!")

			Case $iMsg = $idMni_About
				MsgBox($MB_SYSTEMMODAL, "About", "GUI Menu Test")
		EndSelect
	WEnd

	GUIDelete()
EndFunc   ;==>_Main

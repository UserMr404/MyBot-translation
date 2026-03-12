#include <GUIConstantsEx.au3>
#include <TreeViewConstants.au3>
#include <WindowsStylesConstants.au3>

Example()
Exit

Func Example()
	Local $hGUI = GUICreate("GUI with more treeviews", 340, 200, -1, -1, BitOR($WS_MINIMIZEBOX, $WS_MAXIMIZEBOX, $WS_GROUP, $WS_CAPTION, $WS_POPUP, $WS_SYSMENU))

	Local $idTreeView = GUICtrlCreateTreeView(10, 10, 120, 150)
	Local $idTVi_About = GUICtrlCreateTreeViewItem("About", $idTreeView)
	Local $idTVi_General = GUICtrlCreateTreeViewItem("General", $idTreeView)
	Local $idTVi_Tools = GUICtrlCreateTreeViewItem("Tools", $idTreeView)
	Local $idTVi_Effect = GUICtrlCreateTreeViewItem("Effects", $idTVi_General)
	Local $idTVi_Style = GUICtrlCreateTreeViewItem("Styles", $idTVi_General)
	GUICtrlCreateTreeViewItem("Commandline", $idTVi_Tools)
	GUICtrlCreateTreeViewItem("Misc", $idTVi_Tools)

	Local $idGrp_DescriptionGroup = GUICtrlCreateGroup("Description", 140, 105, 180, 55)
	GUICtrlSetState(-1, $GUI_HIDE)

	Local $idGrp_EffectsGroup = GUICtrlCreateGroup("Effects", 140, 5, 180, 95)
	GUICtrlSetState(-1, $GUI_HIDE)
	Local $idTV_EffectsTreeView = GUICtrlCreateTreeView(150, 20, 160, 70, BitOR($TVS_CHECKBOXES, $TVS_DISABLEDRAGDROP), $WS_EX_CLIENTEDGE)
	GUICtrlSetState(-1, $GUI_HIDE)
	Local $idTVi_Effect1 = GUICtrlCreateTreeViewItem("Effect 1", $idTV_EffectsTreeView)
	GUICtrlCreateTreeViewItem("Effect 2", $idTV_EffectsTreeView)
	Local $idTVi_Effect3 = GUICtrlCreateTreeViewItem("Effect 3", $idTV_EffectsTreeView)
	GUICtrlCreateTreeViewItem("Effect 4", $idTV_EffectsTreeView)
	GUICtrlCreateTreeViewItem("Effect 5", $idTV_EffectsTreeView)

	Local $idGrp_StylesGroup = GUICtrlCreateGroup("Styles", 140, 5, 180, 95)
	GUICtrlSetState(-1, $GUI_HIDE)
	Local $idTV_StylesTreeView = GUICtrlCreateTreeView(150, 20, 160, 70, BitOR($TVS_CHECKBOXES, $TVS_DISABLEDRAGDROP), $WS_EX_CLIENTEDGE)
	GUICtrlSetState(-1, $GUI_HIDE)
	GUICtrlCreateTreeViewItem("Style 1", $idTV_StylesTreeView)
	GUICtrlCreateTreeViewItem("Style 2", $idTV_StylesTreeView)
	GUICtrlCreateTreeViewItem("Style 3", $idTV_StylesTreeView)
	Local $idTVi_Style4 = GUICtrlCreateTreeViewItem("Style 4", $idTV_StylesTreeView)
	Local $idTVi_Style5 = GUICtrlCreateTreeViewItem("Style 5", $idTV_StylesTreeView)

	Local $idLbl_About = GUICtrlCreateLabel("This is only a treeview demo.", 160, 80, 160, 20)

	Local $idBtn_Cancel = GUICtrlCreateButton("Cancel", 130, 170, 85, 25)
	GUISetState(@SW_SHOW, $hGUI)

	GUICtrlSetState($idTVi_Effect1, $GUI_CHECKED)
	GUICtrlSetState($idTVi_Effect3, $GUI_CHECKED)
	GUICtrlSetState($idTVi_Style4, $GUI_CHECKED)
	GUICtrlSetState($idTVi_Style5, $GUI_CHECKED)

	While 1
		Switch GUIGetMsg()
			Case $GUI_EVENT_CLOSE, $idBtn_Cancel
				ExitLoop

			Case $idTVi_About
				GUICtrlSetState($idGrp_DescriptionGroup, $GUI_HIDE)
				GUICtrlSetState($idTV_EffectsTreeView, $GUI_HIDE)
				GUICtrlSetState($idGrp_EffectsGroup, $GUI_HIDE)
				GUICtrlSetState($idTV_StylesTreeView, $GUI_HIDE)
				GUICtrlSetState($idGrp_StylesGroup, $GUI_HIDE)
				GUICtrlSetState($idLbl_About, $GUI_SHOW)

			Case $idTVi_Effect
				GUICtrlSetState($idTV_StylesTreeView, $GUI_HIDE)
				GUICtrlSetState($idGrp_StylesGroup, $GUI_HIDE)
				GUICtrlSetState($idLbl_About, $GUI_HIDE)
				GUICtrlSetState($idGrp_EffectsGroup, $GUI_SHOW)
				GUICtrlSetState($idGrp_DescriptionGroup, $GUI_SHOW)
				GUICtrlSetState($idTV_EffectsTreeView, $GUI_SHOW)
				GUICtrlSetBkColor($idTV_EffectsTreeView, 0xD0F0F0)

			Case $idTVi_Style
				GUICtrlSetState($idTV_EffectsTreeView, $GUI_HIDE)
				GUICtrlSetState($idGrp_EffectsGroup, $GUI_HIDE)
				GUICtrlSetState($idLbl_About, $GUI_HIDE)
				GUICtrlSetState($idGrp_StylesGroup, $GUI_SHOW)
				GUICtrlSetState($idGrp_DescriptionGroup, $GUI_SHOW)
				GUICtrlSetState($idTV_StylesTreeView, $GUI_SHOW)
				GUICtrlSetColor($idTV_StylesTreeView, 0xD00000)
				GUICtrlSetBkColor($idTV_StylesTreeView, 0xD0FFD0)

		EndSwitch
	WEnd
	GUIDelete($hGUI)
EndFunc   ;==>Example

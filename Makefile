all: edledit_ui.py edledit_about_ui.py edledit_license_ui.py edledit_rc.py

clean:
	rm -f edledit_ui.py edledit_rc.py

edledit_ui.py: edledit.ui
	pyuic4 -x -o edledit_ui.py edledit.ui

edledit_about_ui.py: edledit_about.ui
	pyuic4 -x -o edledit_about_ui.py edledit_about.ui

edledit_license_ui.py: edledit_license.ui
	pyuic4 -x -o edledit_license_ui.py edledit_license.ui

edledit_rc.py: edledit.qrc
	pyrcc4 -o edledit_rc.py edledit.qrc

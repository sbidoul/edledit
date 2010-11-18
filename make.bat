set QTBIN=c:\Soft\Python27\Lib\site-packages\PyQt4\bin
call %QTBIN%\pyuic4 -x -o edledit\edledit_ui.py edledit\edledit.ui
call %QTBIN%\pyuic4 -x -o edledit\edledit_about_ui.py edledit\edledit_about.ui
call %QTBIN%\pyuic4 -x -o edledit\edledit_license_ui.py edledit\edledit_license.ui
call %QTBIN%\pyrcc4 -o edledit\edledit_rc.py edledit\edledit.qrc

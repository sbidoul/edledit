set QTBIN=c:\Soft\Python27\Lib\site-packages\PyQt4\bin
set SRCDIR=edledit
set SOURCES=%SRCDIR%\edledit.py %SRCDIR%\edledit_about_ui.py %SRCDIR%\edledit_license_ui.py %SRCDIR%\edledit_ui.py %SRCDIR%\pyedl.py %SRCDIR%\edlwidget.py

rem UI
call %QTBIN%\pyuic4 -x -o %SRCDIR%\edledit_ui.py %SRCDIR%\edledit.ui
call %QTBIN%\pyuic4 -x -o %SRCDIR%\edledit_about_ui.py %SRCDIR%\edledit_about.ui
call %QTBIN%\pyuic4 -x -o %SRCDIR%\edledit_license_ui.py %SRCDIR%\edledit_license.ui

rem translation
call %QTBIN%\pylupdate4 -verbose %SOURCES% -ts %SRCDIR%\translations\edledit_fr.ts 
call %QTBIN%\lrelease %SRCDIR%\translations\edledit_fr.ts

rem res
call %QTBIN%\pyrcc4 -o %SRCDIR%\edledit_rc.py %SRCDIR%\edledit.qrc


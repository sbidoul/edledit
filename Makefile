all:: edleditui.py edleditres_rc.py

clean:
	rm -f edleditui.py edleditres_rc.py

edleditui.py: edleditui.ui
	pyuic4 -x -o edleditui.py edleditui.ui

edleditres_rc.py: edleditres.qrc
	pyrcc4 -o edleditres_rc.py edleditres.qrc

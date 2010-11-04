all:: edleditui.py edleditres.py

clean:
	rm -f edleditui.py edleditres.py

edleditui.py: edleditui.ui
	pyuic4 -x -o edleditui.py edleditui.ui

edleditres.py: edleditres.qrc
	pyrcc4 -o edleditres.py edleditres.qrc

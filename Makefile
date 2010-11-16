all: edledit/edledit_ui.py edledit/edledit_about_ui.py edledit/edledit_license_ui.py edledit/edledit_rc.py

clean:
	rm -f edledit/edledit_ui.py edledit/edledit_about_ui.py edledit/edledit_license_ui.py edledit/edledit_rc.py

edledit/edledit_ui.py: edledit/edledit.ui
	pyuic4 -x -o $@ $<

edledit/edledit_about_ui.py: edledit/edledit_about.ui
	pyuic4 -x -o $@ $<

edledit/edledit_license_ui.py: edledit/edledit_license.ui
	pyuic4 -x -o $@ $<

edledit/edledit_rc.py: edledit/edledit.qrc
	pyrcc4 -o $@ $<

sdist:
	rm -f MANIFEST
	python setup.py sdist

bdist_deb:
	rm -f MANIFEST
	python setup.py --command-packages=stdeb.command bdist_deb

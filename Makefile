all: resources

clean:
	rm -f edledit/edledit_ui.py edledit/edledit_about_ui.py edledit/edledit_license_ui.py edledit/edledit_rc.py
	rm -f MANIFEST
	rm -fr dist
	rm -fr deb_dist
	rm -fr build
	rm -f edledit/*.pyc

resources: edledit/edledit_ui.py edledit/edledit_about_ui.py edledit/edledit_license_ui.py edledit/edledit_rc.py

edledit/edledit_ui.py: edledit/edledit.ui
	pyuic4 -x -o $@ $<

edledit/edledit_about_ui.py: edledit/edledit_about.ui
	pyuic4 -x -o $@ $<

edledit/edledit_license_ui.py: edledit/edledit_license.ui
	pyuic4 -x -o $@ $<

edledit/edledit_rc.py: edledit/edledit.qrc
	pyrcc4 -o $@ $<

sdist: resources
	rm -f MANIFEST
	python setup.py sdist

bdist_deb: resources
	rm -f MANIFEST
	python setup.py --command-packages=stdeb.command bdist_deb

all: tr res

SRCDIR = edledit

UI_SOURCES = \
		$(SRCDIR)/edledit_about_ui.py \
		$(SRCDIR)/edledit_license_ui.py \
		$(SRCDIR)/edledit_ui.py \

RC_SOURCES = \
		$(SRCDIR)/edledit_rc.py

SOURCES = $(UI_SOURCES) \
		$(SRCDIR)/edledit.py \
		$(SRCDIR)/pyedl.py \
		$(SRCDIR)/edlwidget.py

clean:
	rm -f $(UI_SOURCES)
	rm -f $(RC_SOURCES)
	rm -f $(SRCDIR)/translations/*.qm
	rm -f MANIFEST
	rm -fr dist
	rm -fr deb_dist
	rm -fr build
	rm -f $(SRCDIR)/*.pyc

ui: $(UI_SOURCES)

$(SRCDIR)/edledit_ui.py: $(SRCDIR)/edledit.ui
	pyuic4 -x -o $@ $<

$(SRCDIR)/edledit_about_ui.py: $(SRCDIR)/edledit_about.ui
	pyuic4 -x -o $@ $<

$(SRCDIR)/edledit_license_ui.py: $(SRCDIR)/edledit_license.ui
	pyuic4 -x -o $@ $<

tr: $(SRCDIR)/translations/edledit_fr.qm

$(SRCDIR)/translations/edledit_fr.ts: $(SOURCES)
	pylupdate4 -verbose $(SOURCES) -ts $@

$(SRCDIR)/translations/edledit_fr.qm: $(SRCDIR)/translations/edledit_fr.ts
	lrelease $<

res: $(RC_SOURCES)

$(SRCDIR)/edledit_rc.py: $(SRCDIR)/edledit.qrc
	pyrcc4 -o $@ $<

sdist: all
	rm -f MANIFEST
	python setup.py sdist

bdist_deb: all
	rm -f MANIFEST
	python setup.py --command-packages=stdeb.command bdist_deb


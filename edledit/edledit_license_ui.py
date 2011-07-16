# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edledit/edledit_license.ui'
#
# Created: Sat Jul 16 10:56:40 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LicenseDialog(object):
    def setupUi(self, LicenseDialog):
        LicenseDialog.setObjectName(_fromUtf8("LicenseDialog"))
        LicenseDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        LicenseDialog.resize(526, 299)
        LicenseDialog.setSizeGripEnabled(True)
        LicenseDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(LicenseDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.plainTextEdit = QtGui.QPlainTextEdit(LicenseDialog)
        self.plainTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout.addWidget(self.plainTextEdit, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(LicenseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(LicenseDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LicenseDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LicenseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LicenseDialog)

    def retranslateUi(self, LicenseDialog):
        LicenseDialog.setWindowTitle(QtGui.QApplication.translate("LicenseDialog", "License for edledit", None, QtGui.QApplication.UnicodeUTF8))
        self.plainTextEdit.setPlainText(QtGui.QApplication.translate("LicenseDialog", "edledit is free software: you can redistribute it and/or modify\n"
"it under the terms of the GNU General Public License as published by\n"
"the Free Software Foundation, either version 3 of the License, or\n"
"(at your option) any later version.\n"
"\n"
"edledit is distributed in the hope that it will be useful,\n"
"but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
"GNU General Public License for more details.\n"
"\n"
"You should have received a copy of the GNU General Public License\n"
"along with edledit.  If not, see <http://www.gnu.org/licenses/>.\n"
"", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LicenseDialog = QtGui.QDialog()
    ui = Ui_LicenseDialog()
    ui.setupUi(LicenseDialog)
    LicenseDialog.show()
    sys.exit(app.exec_())


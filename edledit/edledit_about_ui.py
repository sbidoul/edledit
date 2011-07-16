# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edledit/edledit_about.ui'
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

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName(_fromUtf8("AboutDialog"))
        AboutDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        AboutDialog.resize(385, 309)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(AboutDialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.labelIcon = QtGui.QLabel(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelIcon.sizePolicy().hasHeightForWidth())
        self.labelIcon.setSizePolicy(sizePolicy)
        self.labelIcon.setText(_fromUtf8(""))
        self.labelIcon.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/edledit.png")))
        self.labelIcon.setScaledContents(True)
        self.labelIcon.setObjectName(_fromUtf8("labelIcon"))
        self.horizontalLayout_2.addWidget(self.labelIcon)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.labelNameVersion = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.labelNameVersion.setFont(font)
        self.labelNameVersion.setAlignment(QtCore.Qt.AlignCenter)
        self.labelNameVersion.setObjectName(_fromUtf8("labelNameVersion"))
        self.verticalLayout.addWidget(self.labelNameVersion)
        self.labelDescription = QtGui.QLabel(AboutDialog)
        self.labelDescription.setMinimumSize(QtCore.QSize(0, 19))
        self.labelDescription.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDescription.setOpenExternalLinks(True)
        self.labelDescription.setObjectName(_fromUtf8("labelDescription"))
        self.verticalLayout.addWidget(self.labelDescription)
        self.labelCopyright = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelCopyright.setFont(font)
        self.labelCopyright.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCopyright.setOpenExternalLinks(True)
        self.labelCopyright.setObjectName(_fromUtf8("labelCopyright"))
        self.verticalLayout.addWidget(self.labelCopyright)
        self.labelIconsCredits = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelIconsCredits.setFont(font)
        self.labelIconsCredits.setAlignment(QtCore.Qt.AlignCenter)
        self.labelIconsCredits.setOpenExternalLinks(True)
        self.labelIconsCredits.setObjectName(_fromUtf8("labelIconsCredits"))
        self.verticalLayout.addWidget(self.labelIconsCredits)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButtonLicense = QtGui.QPushButton(AboutDialog)
        self.pushButtonLicense.setAutoDefault(False)
        self.pushButtonLicense.setObjectName(_fromUtf8("pushButtonLicense"))
        self.horizontalLayout.addWidget(self.pushButtonLicense)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.pushButtonOK = QtGui.QPushButton(AboutDialog)
        self.pushButtonOK.setDefault(True)
        self.pushButtonOK.setObjectName(_fromUtf8("pushButtonOK"))
        self.horizontalLayout.addWidget(self.pushButtonOK)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(AboutDialog)
        QtCore.QObject.connect(self.pushButtonOK, QtCore.SIGNAL(_fromUtf8("clicked()")), AboutDialog.accept)
        QtCore.QObject.connect(self.pushButtonLicense, QtCore.SIGNAL(_fromUtf8("clicked()")), AboutDialog.license)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)
        AboutDialog.setTabOrder(self.pushButtonOK, self.pushButtonLicense)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QtGui.QApplication.translate("AboutDialog", "About edledit", None, QtGui.QApplication.UnicodeUTF8))
        self.labelNameVersion.setText(QtGui.QApplication.translate("AboutDialog", "edledit {__version__}", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription.setText(QtGui.QApplication.translate("AboutDialog", "An editor for <a href=\"http://www.mplayerhq.hu/DOCS/HTML/en/edl.html\">MPlayer Edit Decision Lists</a>", None, QtGui.QApplication.UnicodeUTF8))
        self.labelCopyright.setText(QtGui.QApplication.translate("AboutDialog", "Copyright (c) 2010 Stéphane Bidoul &lt;<a href=\"mailto:sbi@skynet.be?subject=[edledit] ...\">sbi@skynet.be</a>&gt;", None, QtGui.QApplication.UnicodeUTF8))
        self.labelIconsCredits.setText(QtGui.QApplication.translate("AboutDialog", "Icons by <a href=\"http://www.famfamfam.com/lab/icons/silk/\">FamFamFam</a>, <a href=\"http://www.customicondesign.com/\">Custom Icon Design</a> and <a href=\"http://dlanham.com/\">David Lanham</a>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLicense.setText(QtGui.QApplication.translate("AboutDialog", "&License", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOK.setText(QtGui.QApplication.translate("AboutDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))

import edledit_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    AboutDialog = QtGui.QDialog()
    ui = Ui_AboutDialog()
    ui.setupUi(AboutDialog)
    AboutDialog.show()
    sys.exit(app.exec_())


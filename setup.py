#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

from edledit.edledit import __version__

setup(
    name='edledit',
    version=__version__,
    description='An editor for MPlayer Edit Decision Lists',
    author=u'Stéphane Bidoul',
    author_email='sbi@skynet.be',
    url='http://users.skynet.be/sbi/edledit/',
    packages=['edledit'],
    package_data={'edledit': ['translations/*.qm']},
    data_files=[('share/icons', ['edledit/images/edledit.png'])],
    #install_requires=['PyQt4'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Video',
    ],
    entry_points={
        'console_scripts': 'edledit=edledit.edledit:run',
    },
)

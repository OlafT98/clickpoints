#!/usr/bin/env python
# -*- coding: utf-8 -*-
# launch.py

# Copyright (c) 2015-2022, Richard Gerum, Sebastian Richter, Alexander Winterl
#
# This file is part of ClickPoints.
#
# ClickPoints is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ClickPoints is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClickPoints. If not, see <http://www.gnu.org/licenses/>
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# launch.py

import asyncio


def main(*args):
    import sys
    if len(args) == 0:
        args = sys.argv
    else:
        args = [sys.executable] + list(args)
    print("args", args)

    if len(args) > 1:
        if args[1] in ("register", "install"):
            from .includes.RegisterRegistry import install
            return install()
        elif args[1] in ("unregister", "uninstall"):
            from .includes.RegisterRegistry import install
            return install("uninstall")
        elif args[1] in ("-v", "--version"):
            import clickpoints
            print(clickpoints.__version__)
            return
        elif args[1] == "ffmpeg":
            import imageio, glob, os
            try:
                imageio.plugins.ffmpeg.get_exe()
                print("ffmpeg found from imageio")
            except imageio.core.fetching.NeedDownloadError:
                files = glob.glob(os.path.join(os.path.dirname(__file__), "..", "ffmpeg*.exe"))
                files.extend(glob.glob(os.path.join(os.path.dirname(__file__), "..", "external", "ffmpeg*.exe")))
                if files:
                    print("ffmpeg found", files[0])
                    os.environ["IMAGEIO_FFMPEG_EXE"] = files[0]
                else:
                    print("try to download ffmpeg")
                    imageio.plugins.ffmpeg.download()
            return

    from clickpoints import print_status
    print_status()

    # keep PyQt5 exceptions visible
    sys._excepthook = sys.excepthook
    sys.excepthook = lambda *a: sys._excepthook(*a)

    from qtpy import QtCore, QtWidgets, QtGui
    import ctypes
    from clickpoints.Core import ClickPointsWindow
    from clickpoints.includes import LoadConfig
    import qasync
    from clickpoints import define_paths

    define_paths()

    app = QtWidgets.QApplication(args)

    # Create and install the qasync event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    app.loop = loop

    # Windows taskbar grouping
    if sys.platform.startswith("win"):
        myappid = "fabrybiophysics.clickpoints"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # load config and init window
    config = LoadConfig(*args)
    window = ClickPointsWindow(config, app)
    try:
        import pyi_splash  # pyinstaller only
        pyi_splash.close()
    except ImportError:
        pass
    window.show()

    # >>> This is the crucial change <<<
    # Run BOTH Qt and asyncio by running the qasync loop, not app.exec_()
    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()


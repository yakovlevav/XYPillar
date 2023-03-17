nuitka --follow-imports ^
        --enable-plugin=tk-inter ^
        --standalone ^
        --include-data-file=XYpillar.png=XYpillar.png ^
        --include-data-file=XYpillar.ico=XYpillar.ico ^
        --windows-icon-from-ico=XYpillar.ico ^
        --onefile-windows-splash-screen-image=XYpillar.png ^
        xypillar.py  
pyinstaller --noconfirm ^
    --onedir --windowed ^
    --add-data .conda\lib\site-packages\customtkinter;customtkinter ^
    --add-data XYpillar.png;. ^
    --add-data XYpillar.ico;. ^
    --splash="XYpillar.ico" ^
    --icon="XYpillar.ico" ^
    xypillar.py
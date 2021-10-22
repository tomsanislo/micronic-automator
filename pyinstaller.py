import PyInstaller.__main__
import os, sys
    
PyInstaller.__main__.run([  
     '--onefile',
     '--windowed',
     "--icon=icon.ico"
     ,os.path.join(os.path.dirname(sys.executable), 'client.py'),                                        
])
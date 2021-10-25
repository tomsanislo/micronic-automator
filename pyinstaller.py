import PyInstaller.__main__
import os, sys
    
PyInstaller.__main__.run([  
     '--onefile',
     '--windowed'
     ,os.path.join(os.getcwd(), 'client.py'),                                        
])
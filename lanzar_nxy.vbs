' lanzar_nxy.vbs
' Ejecuta hora_de_trabajo_NXY.py sin mostrar ninguna ventana CMD
' Coloca este archivo en la misma carpeta que el .py

Dim ruta
ruta = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

CreateObject("WScript.Shell").Run _
    "pythonw """ & ruta & "\hora_de_trabajo_NXY.py""", _
    0, False

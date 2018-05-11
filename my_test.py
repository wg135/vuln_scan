#my_test.py
import my_debugger

path_to_exe = "C:\\Program Files\\Foxit Software\\Foxit Reader\\FoxitReader.exe"
debugger = my_debugger.debugger()
# debugger.load(path_to_exe)
pid = raw_input("pid")
debugger.attach(int(pid))
debugger.detach()
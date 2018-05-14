from ctypes import *
from my_debugger_defines import *

import sys
import time

kernel32 = windll.kernel32


class debugger():

	def init(self):
		self.h_process = None
		self.pid = None
		self.debugger_active = False
		self.h_thread = None
		self.context = None


	def load(self, path_to_exe):

		# dwCreation flas determines how to create the process
		# set creation_flags = CREATE_NEW_CONSOLE if you want
		# to see the calculator GUI
		creation_flags = CREATE_NEW_CONSOLE

		# instantiate the structs
		startupinfo = STARTUPINFO()
		process_information = PROCESS_INFORMATION()

		# The following two opinions allow the started process
		# to be shown as a separate window. This also illustrates
		# how different settings in the STARTUPINFO struct can affect
		# the debuggee

		startupinfo.dwFlags = 0x1
		startupinfo.wShowWindow = 0x0
		# we then initialize the cb variable in the STARTUPINFO struct
		# which is just the size of the struct itself
		startupinfo.cb = sizeof(startupinfo)
		if kernel32.CreateProcessA(path_to_exe,
								   None,
								   None,
								   None,
								   None,
								   creation_flags,
								   None,
								   None,
								   byref(startupinfo),
								   byref(process_information)):
			print "[+] process us launched successfully"
			print "[+] PID: %d"	%	process_information.dwProcessId
			self.pid = process_information.dwProcessId
			self.h_process = self.open_process(process_information.dwProcessId)
			self.debugger_active = True
		else:
			print "[!] Error: 0x%08x." % kernel32.GetLastError()

	def open_process(self, pid):
		h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
		return h_process

	def attach(self, pid):

		self.h_process = self.open_process(pid)
		if kernel32.DebugActiveProcess(pid):
			self.debugger_active = True
			self.pid = int(pid)
			# self.run()
		else:
			print "[-] unable to attach to the process"

	def run(self):
		while self.debugger_active == True:
			self.get_debug_event()		

	def get_debug_event(self):
		debug_event = DEBUG_EVENT()
		continue_status = DBG_CONTINUE
		if kernel32.WaitForDebugEvent(byref(debug_event),100):
			kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)
			# self.h_thread = self.open_thread(debug_event.dwThreadId)
			# self.context = self.get_thread_context(h_thread=self.h_thread)

	def detach(self):
		if kernel32.DebugActiveProcessStop(self.pid):
			print "[+] Finished debugging. Exiting..."
			return True
		else:
			print "[!] detach process error"		

	## thread part

	def open_thread(self, thread_id):
		h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)
		if h_thread is not None:
			return h_thread
		else:
			print "[!] could not obtain a valid thread handle"
			return False

	def enumerate_threads(self):
		thread_entry = THREADENTRY32()
		thread_list = []
		snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)
		if snapshot is not None:
			thread_entry.dwSize = sizeof(thread_entry)
			success = kernel32.Thread32First(snapshot, byref(thread_entry))

			while success:
				if thread_entry.th32OwnerProcessID == self.pid:
					thread_list.append(thread_entry.th32ThreadID)
				success = kernel32.Thread32Next(snapshot, byref(thread_entry))	
			kernel32.CloseHandle(snapshot)
			return thread_list
		else:
			return False

	def get_thread_context(self, thread_id = None, h_thread = None):

		context = CONTEXT()
		context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS

		# obtain a handle to the thread

		if h_thread is None:
			self.h_thread = self.open_thread(thread_id)

		if kernel32.GetThreadContext(self.h_thread, byref(context)):
			return context
		else:						
			return False
		





		

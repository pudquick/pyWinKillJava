# Depends on the following:
# WMI: http://timgolden.me.uk/python/wmi/index.html
# pywin32: http://sourceforge.net/projects/pywin32/
# python.org python for Windows (32-bit): http://python.org/download/
# Install python, pywin32, and the WMI module before attempting to compile
# pyInstaller to build into an .exe: http://www.pyinstaller.org/
# pyInstaller suggested command: python pyinstaller.py -F -n KillJava pyWinKillJava.py

import os, os.path, wmi, shutil, stat, win32api, win32con, winerror, re, win32service
from win32com.shell import shell

def is_admin():
    try:
        return shell.IsUserAnAdmin()
    except:
        return False

def ignore_exception(IgnoreException=Exception,DefaultVal=None):
    def dec(fname):
        def _dec(*args, **kwargs):
            try:
                return fname(*args, **kwargs)
            except IgnoreException:
                return DefaultVal
        return _dec
    return dec

def kill_process_name(n):
    wmi_interface = wmi.WMI()
    try:
        processes = wmi_interface.Win32_Process(name=n)
    except:
        processes = []
    for process in processes:
        ignore_exception()(process.Terminate)()
    try:
        processes = wmi_interface.Win32_Process(name=n)
    except:
        processes = []
    for process in processes:
        fin,fout = ignore_exception(DefaultVal=(None,None))(os.popen4)("taskkill /F /PID %s" % process.ProcessId)
        if fout:
            _ = fout.read()

def remove_readonly(fn, path, excinfo):
    if (fn is os.rmdir) or (fn is os.remove):
        ignore_exception()(win32api.SetFileAttributes)(path, win32con.FILE_ATTRIBUTE_NORMAL)
        ignore_exception()(os.chmod)(path, stat.S_IWRITE)
        ignore_exception()(fn)(path)

def kill_program_folder(n):
    p_paths = []
    p_paths.append(os.environ.get("ProgramFiles", ""))
    p_paths.append(os.environ.get("ProgramW6432", ""))
    for p_path in set(p_paths):
        if p_path:
            n_path = p_path.rstrip('\\') + '\\' + n
            shutil.rmtree(n_path, onerror=remove_readonly)

def kill_system32_file(n):
    sys_path  = win32api.GetSystemDirectory()
    sys_drive = sys_path.lower().split('\\windows\\')[0]
    for sys32_path in ["\\windows\\sysnative\\", "\\windows\\system32\\"]:
        n_path = sys_drive + sys32_path + n
        if os.path.exists(n_path):
            ignore_exception()(win32api.SetFileAttributes)(n_path, win32con.FILE_ATTRIBUTE_NORMAL)
            ignore_exception()(os.chmod)(n_path, stat.S_IWRITE)
            ignore_exception()(os.remove)(n_path)
        if os.path.exists(n_path):
            fin,fout = ignore_exception(DefaultVal=(None,None))(os.popen4)("del /F %s" % n_path)
            if fout:
                _ = fout.read()

def _remove_registry_key(path, base, mode=32):
    try:
        if mode == 64:
            win32api.RegDeleteKeyEx(base, path, win32con.KEY_WOW64_64KEY)
        else:
            win32api.RegDeleteKey(base, path)
    except win32api.error, (code, fn, msg):
        if code != winerror.ERROR_FILE_NOT_FOUND:
            raise win32api.error, (code, fn, msg)

def recurse_delete_registry_key(path, base=win32con.HKEY_LOCAL_MACHINE, mode=32):
    base_key = None
    registry_flags = win32con.KEY_READ
    if mode == 64:
        registry_flags = win32con.KEY_READ | win32con.KEY_WOW64_64KEY
    try:
        base_key = win32api.RegOpenKeyEx(base, path, 0, registry_flags)
    except win32api.error, (code, fn, msg):
        raise win32api.error, (code, fn, msg)
    else:
        # Found and opened the key
        loop_counter = 5000
        # Don't try forever
        while (loop_counter > 0):
            loop_counter -= 1
            try:
                subkeyname = win32api.RegEnumKey(base_key, 0)
            except win32api.error, (code, fn, msg):
                if code != winerror.ERROR_NO_MORE_ITEMS:
                    raise win32api.error, (code, fn, msg)
                break
            recurse_delete_registry_key(path + '\\' + subkeyname, base, mode)
        _remove_registry_key(path, base, mode)
    finally:
        if base_key:
            win32api.RegCloseKey(base_key)

def registry_subkey_value(path, subname, base=win32con.HKEY_LOCAL_MACHINE, mode=32):
    registry_flags = win32con.KEY_READ
    if mode == 64:
        registry_flags = win32con.KEY_READ | win32con.KEY_WOW64_64KEY
    try:
        base_key = win32api.RegOpenKeyEx(base, path, 0, registry_flags)
    except:
        base_key = None
    if base_key:
        try:
            sub_value,_ = win32api.RegQueryValueEx(base_key, subname)
            return sub_value
        except:
            return ''
    return ''

def regexp_find_registry_keys(patterns, path, base=win32con.HKEY_LOCAL_MACHINE, mode=32):
    registry_flags = win32con.KEY_READ
    if mode == 64:
        registry_flags = win32con.KEY_READ | win32con.KEY_WOW64_64KEY
    try:
        base_key = win32api.RegOpenKeyEx(base, path, 0, registry_flags)
    except:
        base_key = None
    if base_key:
        found_keys = set()
        compiled_patterns = [re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns]
        for subkey in win32api.RegEnumKeyEx(base_key):
            key_name, reserved, key_class, key_last_write = subkey
            for pattern in compiled_patterns:
                if pattern.match(key_name):
                    found_keys.add(path + '\\' + key_name)
        win32api.RegCloseKey(base_key)
        return sorted(found_keys)
    return []


def kill_java_service():
    for bit_mode in [32,64]:
        for cset in ["CurrentControlSet", "ControlSet001", "ControlSet002", "ControlSet003"]:
            ignore_exception()(recurse_delete_registry_key)("SYSTEM\\%s\\Services\\JavaQuickStarterService" % cset, mode=bit_mode)
            ignore_exception()(recurse_delete_registry_key)("SYSTEM\\%s\\Services\\Eventlog\\Application\\JavaQuickStarterService" % cset, mode=bit_mode)
    try:
        svc_mgr = win32service.OpenSCManager('.',None,win32service.SC_MANAGER_ALL_ACCESS)
        svc_handle = win32service.OpenService(svc_mgr,'JavaQuickStarterService',win32service.SERVICE_ALL_ACCESS)
        _ = win32service.DeleteService(svc_handle)
    except:
        _ = None
    for bit_mode in [32,64]:
        for cset in ["CurrentControlSet", "ControlSet001", "ControlSet002", "ControlSet003"]:
            ignore_exception()(recurse_delete_registry_key)("SYSTEM\\%s\\Services\\JavaQuickStarterService" % cset, mode=bit_mode)
            ignore_exception()(recurse_delete_registry_key)("SYSTEM\\%s\\Services\\Eventlog\\Application\\JavaQuickStarterService" % cset, mode=bit_mode)

def kill_java_install_base():
    processes = ['jqs.exe',    'jusched.exe', 'jucheck.exe',  'jp2launcher.exe', 'java.exe',
                 'javaws.exe', 'javaw.exe',   'jaucheck.exe', 'jaureg.exe',      'iexplore.exe']
    for process in processes:
        kill_process_name(process)
    kill_java_service()
    kill_program_folder("Java")
    sys_files = ['javacpl.cpl','java.exe','javaw.exe','javaws.exe']
    for filename in sys_files:
        kill_system32_file(filename)

def kill_java_keys():
    total_kill = set()
    for bit_mode in [32,64]:
        prod_names = [r'java 7 update [0-9]+', r'java\(tm\) 6 update [0-9]+', r'java auto updater']
        prod_names = [re.compile(prod_name, re.IGNORECASE) for prod_name in prod_names]
        for product in regexp_find_registry_keys([r'.*'], "SOFTWARE\\Classes\\Installer\\Products", mode=bit_mode):
            p_name = registry_subkey_value(product, 'ProductName', mode=bit_mode)
            for prod_name in prod_names:
                if prod_name.match(p_name):
                    ignore_exception()(recurse_delete_registry_key)(product, mode=bit_mode)
        the_paths = [("CLSID", win32con.HKEY_CLASSES_ROOT),
                     (".DEFAULT\\Software\\Classes\\CLSID", win32con.HKEY_USERS),
                     ("Software\\Classes", win32con.HKEY_LOCAL_MACHINE),
                     ("Software\\Classes\\CLSID", win32con.HKEY_LOCAL_MACHINE),
                     ("Software\\Classes\\MIME\\Database\\Content Type", win32con.HKEY_LOCAL_MACHINE),
                     ("Software\\Classes\\Interface", win32con.HKEY_LOCAL_MACHINE),
                     ("SOFTWARE\\Microsoft\\Internet Explorer\\Low Rights\\ElevationPolicy", win32con.HKEY_LOCAL_MACHINE),
                     ("SOFTWARE\\MozillaPlugins", win32con.HKEY_LOCAL_MACHINE),
                     ("Software\\Classes\\TypeLib", win32con.HKEY_LOCAL_MACHINE)]
        the_names = [r'{CAFEEFAC-[0F][0F][1F].+-ABCDEFFEDCB.}',
                     r'{08B0E5C0-4FCB-11CF-AAA5-00401C60850.}',
                     r'{4299124F-F2C3-41B4-9C73-9236B2AD0E8F}',
                     r'{5852F5E.-8BF4-11D4-A245-0080C6F74284}',
                     r'{761497BB-D6F0-462C-B6EB-D4DAF1D92D43}',
                     r'{8AD9C840-044E-11D1-B3E9-00805F499D93}',
                     r'{C8FE2181-CAE7-49EE-9B04-DB7EB4DA544A}',
                     r'{DBC80044-A445-435B-BC74-9C25C1C588A9}',
                     r'{E19F9331-3110-11D4-991C-005004D3B3DB}',
                     r'{E7E6F031-17CE-4C07-BC86-EABFE594F69C}',
                     r'@java\.com/.*',
                     r'javaplugin.*',
                     r'javawebstart.*',
                     r'jnlpfile.*',
                     r'jarfile.*',
                     r'ieplugin\.jqsiestartdetectorimpl.*',
                     r'application/x-java-applet.*',
                     r'application/x-java-jnlp-file.*']
        for target_path, target_base in the_paths:
            for java_key in regexp_find_registry_keys(the_names, target_path, base=target_base, mode=bit_mode):
                ignore_exception()(recurse_delete_registry_key)(java_key, base=target_base, mode=bit_mode)
        misc_key_paths = ["SOFTWARE\\Microsoft\\Internet Explorer\\AdvancedOptions\\JAVA_SUN",
                          "SOFTWARE\\Microsoft\\Internet Explorer\\AdvancedOptions\\JAVA_VM",
                          "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Accessibility\\ATs\\Oracle_JavaAccessBridge",
                          "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\javaws.exe",
                          "SOFTWARE\\JavaSoft",
                          "SOFTWARE\\JreMetrics"]
        for misc_path in misc_key_paths:
            ignore_exception()(recurse_delete_registry_key)(misc_path, mode=bit_mode)

def kill_java():
    print "RUNNING (please wait)"
    if is_admin():
        for x in range(2):
            kill_java_install_base()
            kill_java_keys()
        print "COMPLETE"
    else:
        print "NOT ADMIN - RUN AS ADMIN!"

kill_java()

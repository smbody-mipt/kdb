import sublime, sublime_plugin
from . import Settings as S
import time

class q_creds_provider():
    settings = S.Settings()
    username = ""
    password = ""
    last_upd = None
    @classmethod
    def updateCreds(cls, force=False):
        # if(cls.last_upd):
        #     print("diff="+str(time.time()-cls.last_upd))
        if (not force and cls.last_upd and time.time() - cls.last_upd < cls.settings.get_creds_valid_time()):
            return
        cls.last_upd = time.time()
        creds_cmd = cls.settings.get_creds_command()
        if (not creds_cmd):
            cls.username = ''
            cls.password = ''
            return
        s = sublime.load_settings('q_creds_temp.sublime-settings')
        s.set('username', None)
        s.set('password', None)
        sublime.active_window().active_view().set_status("q_creds","kdb is resolving credentials")
        sublime.active_window().run_command(
            creds_cmd,
            {'settings': 'q_creds_temp.sublime-settings'}
        )
        sublime.active_window().active_view().erase_status("q_creds")
        cls.username = s.get('username')
        cls.password = s.get('password')

    @classmethod
    def getUser(cls):
        cls.updateCreds()
        # print("getuser")
        return cls.username

    @classmethod
    def getPassword(cls):
        cls.updateCreds()
        # print("getpass")
        return cls.password

class QUpdateCredsCommand(sublime_plugin.TextCommand):
    def run(self, edit, input=None, chain=None):
        q_creds_provider.updateCreds(True)
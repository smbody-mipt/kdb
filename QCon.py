import sublime, sublime_plugin
from .qpython import qconnection
from . import q_creds_provider as qcp
from socket import error as socket_error
from . import Settings as S

class QCon():

    settings = S.Settings()

    def __init__(self, host, port, username, password, name=None):
        # self.init = False
        self.mem = 0
        
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # print("user="+str(username))
        # print("pass="+str(password))
        if (not username and not password): #sso
            username = qcp.q_creds_provider.getUser();
            password = qcp.q_creds_provider.getPassword();
        self.q = qconnection.QConnection(host = self.host, port = self.port, username = username, password = password)

    @classmethod
    def fromH(cls, h):
        if h is None: return None
        p = h.split(':')
        for i in range(len(p), 4):
            p.append(None)
        if not p[1].isdigit(): 
            sublime.error_message('port must be digit: ' + p[1])
            raise Exception('port must be digit: ' + p[1])

        return cls(p[0], int(p[1]), p[2], p[3])

    @classmethod
    def new(cls, name, h):
        con = QCon.fromH(h)
        con.name = name
        return con

    @classmethod
    def fromDict(cls, d):
        if d is None: return None
        return cls(d["host"], d["port"], d["username"], d["password"], d["name"])

    def clone(self):
        return QCon.fromDict(self.toDict())

    def toDict(self):
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }

    def equals(self, other):
        if type(other) is not QCon:
            other = QCon.fromDict(other)

        return self.name == other.name  \
            and self.host == other.host \
            and self.port == other.port \
            and self.username == other.username \
            and self.password == other.password

    def h(self, h=None):
        if h:
            p = h.split(':')
            for i in range(len(p), 4):
                p.append(None)
            if not p[1].isdigit(): 
                sublime.error_message('port must be digit: ' + p[1])
                raise Exception('port must be digit: ' + p[1])
            self.host = p[0]
            self.port = int(p[1])
            self.username = p[2]
            self.password = p[3]
        else:
            s = self.host + ':' + str(self.port)
            if self.username: s+= ':' + self.username
            if self.password: s+= ':' + self.password
            return s

    def hstatus(self):
        s = self.host + ':' + str(self.port)
        if self.username: s+= ':' + self.username
        return s

    def status(self):
        status = 'OK' if self.ok() else 'FAIL'
        name = (self.name) if self.name else ''
        if self.mem:
            mem = ' [' + self.mem_str(self.mem) + ']'
        else:
            mem = ''

        return status + ': ' + name + '> ' + self.hstatus() + mem

    def mem_str(self, mem):
        mem = int(mem)
        if mem > 1000000000:
            return '{0:.2f}'.format(mem/1000000000) + 'GB'
        elif mem > 1000000:
            return '{0:.0f}'.format(mem/1000000) + 'MB'
        elif mem > 1000:
            return '{0:.0f}'.format(mem/1000) + 'KB'
        else:
            return '{0:.0f}'.format(mem) + 'B'

    def ok(self):
        try:
            self.q.open()
            if S.Settings.get_reduce_rtt() < 2:
                self.mem = self.q('@[{.Q.w[][`used]}; (); 0]')
            else:
                self.mem = None
        except socket_error as serr:
            return False
        finally:
            if S.Settings.get_reduce_rtt() < 3:
                self.q.close()
        return True

    def close(self):
        self.q.close()
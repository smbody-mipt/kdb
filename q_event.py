import sublime, sublime_plugin
from . import QCon as Q
from . import q_send as QS
from . import Settings as S

class QEvent(sublime_plugin.EventListener):
	#update connection status when view is activated
	def on_activated_async(self, view):
		if (view.score_selector(0, 'source.q') != 0):				#only activated for q
			qcon = S.Settings.get_view_conn(view)
			if qcon:
				view.set_status('q', qcon.status())

	def on_query_completions(self, view, prefix, locations):
		if not view.match_selector(locations[0], "source.q") or not S.Settings.get('use_completion'):
			return []
		compl = view.settings().get('q_compl')
		#print(compl)
		return compl or []

class QUpdateCompletionsCommand(QS.QSendRawCommand):
	def query(self):
		t = '(tables `.)!cols each tables `.'
		v = '(system "v") except system"a"'
		f = 'system "f"'
		q = '1 _ key `.q'
		ns = "raze {(enlist x)!enlist 1 _ key x} each `$\".\",' string except[;`q] key `"
		return '`t`v`f`q`ns!({0}; {1}; {2}; {3}; {4})'.format(t, v, f, q, ns)

	def send(self, con, s):
		if not S.Settings.get('use_completion'):
			return
		try:
			q = con.q
			q.open()
			res = q(self.query())
			#print(res)
			compl = []

			tb = res[b't']
			for x in tb.iteritems():
				t = x[0].decode('utf-8')
				compl.append((t + '\tTable', t))
				for c in x[1]:
					c = c.decode('utf-8')
					#print(c)
					compl.append((t + '\t' + c, c))
					compl.append((c + '\t' + t, c))

			compl.extend(self.makeCompletions(res[b'v'], 'Variable'))
			compl.extend(self.makeCompletions(res[b'f'], 'Function'))          
			compl.extend(self.makeCompletions(res[b'q'], 'q'))       
			compl.extend(self.makeCompletions(['select', 'from', 'update', 'delete'], 'q'))       

			ns = res[b'ns']
			for x in ns.iteritems():
				n = x[0].decode('utf-8')
				compl.append((n + '\tNamespace', n[1:]))
				for c in x[1]:
					c = c.decode('utf-8')
					#print(c)
					f = n + '.' + c
					compl.append((f + '\t' + n, f[1:]))

			self.view.settings().set('q_compl', compl)
		finally:
			if S.Settings.get_reduce_rtt() < 3:
				q.close()

	def makeCompletions(self, l, t):
		out = []
		for x in l:
			#v = x.decode('utf-8')
			v = self.decode(x)
			out.append((v + '\t' + t, v))
		return out


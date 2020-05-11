import sublime, sublime_plugin

class Settings():
	s = {}

	@staticmethod
	def save():
		sublime.save_settings('kdb.sublime-settings')

	@staticmethod
	def add_connection():
		con_dicts = Settings.get('connections')
		if not Settings.has_connection(qcon):
			con_dicts.insert(0, qcon.toDict())	#then add to top
			Settings.set('connections', con_dicts)
			Settings.save()

	@staticmethod
	def delete_connection(qcon):
		con_dicts = Settings.get('connections')
		con_dicts = list(filter(lambda x: not qcon.equals(x), con_dicts))
		Settings.set('connections', con_dicts)
		Settings.save()

	@staticmethod
	def move_to_top(qcon):
		Settings.delete_connection(qcon)
		Settings.add_connection(qcon)

	@staticmethod
	def update_connection(qcon, new_qcon):
		con_dicts = Settings.get('connections')
		for i, c in enumerate(con_dicts):	#modify existing qcon
			if qcon.equals(c):
				con_dicts[i] = new_qcon.toDict()

		Settings.s.set('connections', con_dicts)
		Settings.save()

	@staticmethod
	def has_connection(qcon):
		con_dicts = Settings.get('connections')
		for c in con_dicts:	#modify existing qcon
			if qcon.equals(c):
				return True
		return False

	@staticmethod
	def get(key):
		if not Settings.s:
			Settings.s = sublime.load_settings('kdb.sublime-settings')

		return Settings.s.get(key)

	def set(key, value):
		Settings.s.set(key, value)

	#actual use
	@staticmethod
	def default_new_connection():
		return Settings.get('default_new_connection')

	@staticmethod
	def get_connections():
		return Settings.get('connections') or []

	@staticmethod
	def get_creds_command():
		return Settings.get('creds_command')

	@staticmethod
	def get_creds_valid_time():
		return Settings.get('creds_valid_time')

	@staticmethod
	def get_reduce_rtt():
		return Settings.get('reduce_rtt')
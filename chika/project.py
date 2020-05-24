class Project:
	def __init__(self, path: str, name: str, folder_name: str = ''):
		if not folder_name or len(folder_name) == 0:
			folder_name = name
		self.path: str = path
		self.name: str = name
		self.folder_name: str = folder_name

from typing import List


class ProjectConf:
	def __init__(self, json: dict, *, name: str = 'Unknown'):
		self.name = json.get('name', name)
		self.build_path = json.get('build_path', '')
		self.github = json.get('github', '')
		self.open_folder = json.get('open_folder', '')
		self.open_text = json.get('open_text', '')
		self.open_web = json.get('open_web', '')

	def save(self) -> dict:
		return {
			'name': self.name,
			'build_path': self.build_path,
			'github': self.github,
			'open_folder': self.open_folder,
			'open_text': self.open_text,
			'open_web': self.open_web
		}


class GlobalConf:
	def __init__(self, json: dict):
		self.build_path = json.get('build_path', '')
		self.github = json.get('github', '')
		self.open_folder = json.get('open_folder', 'explorer')
		self.open_text = json.get('open_text', 'explorer')
		self.open_web = json.get('open_web', 'explorer')
		self.projects: List = json.get('projects', [])

	def save(self) -> dict:
		return {
			'build_path': self.build_path,
			'github': self.github,
			'open_folder': self.open_folder,
			'open_text': self.open_text,
			'open_web': self.open_web,
			'projects': self.projects
		}

	def gen_project(self, name) -> ProjectConf:
		return ProjectConf(self.save(), name=name)

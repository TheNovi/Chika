from os.path import basename
from typing import List


class ProjectConf:
	def __init__(self, json: dict):
		self.build_path = json.get('build_path', '')
		self.github = json.get('github', '')

	def save(self) -> dict:
		return {
			'build_path': self.build_path,
			'github': self.github
		}

	@staticmethod
	def parse_name(path):
		return basename(path)


class GlobalConf:
	def __init__(self, json: dict):
		self.build_path = json.get('build_path', '')
		self.github = json.get('github', '')
		self.open_folder = json.get('open_folder', 'explorer')
		self.open_text = json.get('open_text', 'explorer')
		self.open_web = json.get('open_web', 'explorer')
		self.projects: List[str] = json.get('projects', [])

	def save(self) -> dict:
		return {
			'build_path': self.build_path,
			'github': self.github,
			'open_folder': self.open_folder,
			'open_text': self.open_text,
			'open_web': self.open_web,
			'projects': self.projects
		}

	def gen_project(self) -> ProjectConf:
		return ProjectConf(self.save())

	def get_project(self, name):
		for p in self.projects:
			if ProjectConf.parse_name(p) == name:
				return p
		return None

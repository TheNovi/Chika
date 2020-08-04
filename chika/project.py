import json
import subprocess
from os import path as os_path
from shutil import rmtree

from PyInstaller.__main__ import run as pyi_run

from chika.conf import GlobalConf, ProjectConf


class Project:
	def __init__(self, gc: GlobalConf, path: str):
		self.path: str = os_path.realpath(path)
		self.conf: ProjectConf = self.load(gc)

	@property
	def name(self):
		return ProjectConf.parse_name(self.path)

	def run_cscript(self, cs: str, conf_path: str):
		parse = []
		for t in cs.split('\n'):
			t = t.strip()
			if len(t) > 0 and t[0] != '#':
				parse.append(t.replace('{:name', self.name).replace('{:lname', self.name.lower()))
		# print(parse) # NOSONAR
		with open(os_path.join(conf_path, 'gen_cs.bat'), 'w') as f:
			f.write('\n'.join(parse))
		# print(os_path.realpath(os_path.join(self.path, os_path.pardir)))
		o = subprocess.run(os_path.join(conf_path, 'gen_cs.bat'), cwd=os_path.join(self.path, os_path.pardir), shell=True)
		return o.returncode == 0

	def save(self):
		if os_path.exists(self.path):
			with open(os_path.join(self.path, '.chika'), 'w') as f:
				json.dump(self.conf.save(), f)
		else:
			print("Cant save project: " + self.name)

	def load(self, gc: GlobalConf) -> ProjectConf:
		if os_path.exists(os_path.join(self.path, '.chika')):
			with open(os_path.join(self.path, '.chika')) as f:
				return ProjectConf(json.load(f))
		else:
			return gc.gen_project()

	def open_folder(self, open_folder):
		subprocess.run(f'{open_folder} {self.path}')

	def open_github(self, open_web):
		subprocess.run(f'{open_web} https://github.com/{self.conf.github}/{self.name}')

	def create_spec(self):
		subprocess.run(f"pyi-makespec {os_path.join(self.path, self.name.lower(), '__main__.py')} -n={self.name}", cwd=self.path)

	def build(self):
		build_path = self.conf.build_path if self.conf.build_path else self.path
		pyi_run(f"{os_path.join(self.path, f'{self.name.lower()}.spec')} --clean -y --workpath={os_path.join(build_path, 'build')} --distpath={os_path.join(build_path)}".split())
		rmtree(os_path.join(self.conf.build_path, 'build'))

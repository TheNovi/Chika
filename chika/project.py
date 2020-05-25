import json
import subprocess
from os import path as os_path

from chika.conf import GlobalConf, ProjectConf


class Project:
	def __init__(self, gc: GlobalConf, path: str):
		self.path: str = os_path.realpath(path)
		self.conf: ProjectConf = gc.gen_project()

	@property
	def name(self):
		return os_path.basename(self.path)

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

import subprocess
from os import path as os_path

from chika.conf import GlobalConf, ProjectConf


class Project:
	def __init__(self, gc: GlobalConf, path: str, name: str):
		self.path: str = path
		self.name: str = name
		self.conf: ProjectConf = gc.gen_project(self.name)

	def run_cscript(self, cs: str, conf_path: str):
		parse = []
		for t in cs.split('\n'):
			t = t.strip()
			if len(t) > 0 and t[0] != '#':
				parse.append(t.replace('{:name', self.name).replace('{:lname', self.name.lower()))
		# print(parse) # NOSONAR
		# print(realpath(self.path))
		with open(os_path.join(conf_path, 'gen_cs.bat'), 'w') as f:
			f.write('\n'.join(parse))
		o = subprocess.run(os_path.join(conf_path, 'gen_cs.bat'), cwd=os_path.realpath(self.path), shell=True)
		return o.returncode == 0

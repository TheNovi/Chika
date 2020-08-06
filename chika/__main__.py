import json
import subprocess
from os import path as os_path
from sys import argv
from typing import Optional

import pkg_resources

from chika.conf import GlobalConf, ProjectConf
from chika.ncui3.api import Api
from chika.ncui3.com import Com
from chika.ncui3.consts import RetCode
from chika.project import Project


class Ncui(Api):
	def __init__(self):
		super().__init__()
		self.conf_path = os_path.dirname(__file__)
		self.global_conf = self.load()
		self.project: Optional[Project] = self.in_project_dir()

	def load(self) -> GlobalConf:
		p = os_path.join(self.conf_path, 'conf.json')
		if os_path.exists(p):
			with open(p) as f:
				return GlobalConf(json.load(f))
		else:
			return GlobalConf({})

	def save(self):
		with open(os_path.join(self.conf_path, 'conf.json'), 'w') as f:
			json.dump(self.global_conf.save(), f, indent=True)

	def in_project_dir(self) -> Optional[Project]:  # TODO (Zero priority) Fix for linux (\\ -> /)
		for p in self.global_conf.projects:
			if f"{os_path.realpath('.')}\\".startswith(os_path.realpath(p) + '\\'):
				o = Project(self.global_conf, p)
				o.save()
				return o
		return None

	def path(self):
		return self.project.name if self.project else ''

	def set_commands(self):
		self.com(Com('e q exit quit', self.rc.quick, None, {'code': RetCode.EXIT}, man="""exit\nExit from chika shell"""))

		@self.com(Com('version v', man="""version\nPrints Chika version"""))
		def version():
			return self.rc.quick(f'Chika v{pkg_resources.require("chika")[0].version}')

		@self.com(Com('debug', man="""debug\nOpens chika in pip"""))
		def debug():
			subprocess.run(f'{self.global_conf.open_folder} .', cwd=self.conf_path, shell=True)
			return self.rc.quick(f'{self.conf_path}')

		@self.com(Com('ls lp', man="""ls\nPrints all saved projects"""))
		def list_projects():
			o = []
			for i, p in enumerate(self.global_conf.projects):
				n = ProjectConf.parse_name(p)
				if os_path.exists(p):
					if os_path.exists(os_path.join(p, '.chika')):
						o.append(n)
					else:
						o.append(n + ' - (missing .chika file)')
				else:
					o.append(n + '- (invalid path)')
			return self.rc.quick('\n'.join(o))

		@self.com(Com('pwd', man="""pwd <path='.'>\nPrints real path (Same path will be parsed as project path)"""))
		def pwd():
			return self.rc.quick(os_path.realpath(self.rc.get_arg(1, '.')))

		@self.com(Com('printg pg', man="""printg\nPrints global config"""))
		def printg():
			o = []
			for k in self.global_conf.save():
				if k != 'projects':
					o.append(f'{k}: {self.global_conf.save()[k]}')
			return self.rc.quick('\n'.join(o))

		@self.com(Com('setg sg', man="""setg <key> <value>\nSets project config value by key"""))
		def setg():
			if len(self.rc.args) != 3:
				return self.rc.quick(f'2 args are required, found {len(self.rc.args) - 1}', RetCode.ARGS_ERROR)
			k = self.rc.get_arg(1)
			if k == 'build_path':
				self.global_conf.build_path = self.rc.get_arg(2)
			elif k == 'github':
				self.global_conf.github = self.rc.get_arg(2)
			elif k == 'open_folder':
				self.global_conf.open_folder = self.rc.get_arg(2)
			elif k == 'open_text':
				self.global_conf.open_text = self.rc.get_arg(2)
			elif k == 'open_web':
				self.global_conf.open_web = self.rc.get_arg(2)
			else:
				return self.rc.quick(f'Key: \'{k}\' not found', RetCode.ARGS_ERROR)
			self.save()
			return self.rc.quick()

		@self.com(Com('cscript cs', man="""cscript\nOpen cscript"""))
		def cscript():
			p = os_path.join(self.conf_path, 'cscript.txt')
			if not os_path.exists(p):
				with open(p, 'w') as f:
					f.write(default_cscript)
			subprocess.run(f'{self.global_conf.open_text} cscript.txt', cwd=self.conf_path, shell=True)

		@self.com(Com('initp ip', man="""initp <path> <name>\nAdds new project and run cscript"""))  # TODO option with default path=. (only 1 arg: name)
		def initp():
			if len(self.rc.args) != 3:
				return self.rc.quick(f'2 args are required, found {len(self.rc.args) - 1}', RetCode.ARGS_ERROR)
			if os_path.exists(os_path.join(self.rc.get_arg(1), self.rc.get_arg(2))):
				return self.rc.error('Project folder already exists (either use \'add\' commad or delete project folder)')
			self.project = Project(self.global_conf, os_path.join(self.rc.get_arg(1), self.rc.get_arg(2)))
			p = os_path.join(self.conf_path, 'cscript.txt')
			if os_path.exists(p):
				with open(p) as f:
					cs = f.read()
			else:
				cs = default_cscript
				with open(p, 'w') as f:
					f.write(cs)
			self.project.run_cscript(cs, self.conf_path)
			self.project.save()
			if self.project.path not in self.global_conf.projects:
				self.global_conf.projects.append(self.project.path)
			self.save()

		@self.com(Com('add', man="""add <path='.'>\nAdds new project"""))
		def add():
			p = Project(self.global_conf, self.rc.get_arg(1, '.'))
			if p.path in self.global_conf.projects:
				return self.rc.error('Project already added')
			if not os_path.exists(p.path):
				return self.rc.error('Specified project path does not exists: ' + p.path)
			self.project = p
			self.project.save()
			self.global_conf.projects.append(self.project.path)
			self.save()

		@self.com(Com('rm del', man="""rm <name: str>\nRemoves project from ls list\nProject folder stays intact"""))
		def add():
			if len(self.rc.args) != 2:
				return self.rc.quick(f'1 args are required, found {len(self.rc.args) - 1}', RetCode.ARGS_ERROR)
			name = self.rc.get_arg(1)
			if p := self.global_conf.get_project(name):
				if self.project.path == p:
					self.project.save()
					self.project = None
				self.global_conf.projects.remove(p)
			else:
				return self.rc.error(f'No project found: \'{name}\'')
			self.save()

		@self.com(Com('cd cp o open select', man="""cd <name: str>\nOpen project"""))
		def open_():
			if len(self.rc.args) != 2:
				return self.rc.quick(f'1 args are required, found {len(self.rc.args) - 1}', RetCode.ARGS_ERROR)
			name = self.rc.get_arg(1)
			if p := self.global_conf.get_project(name):
				self.project = Project(self.global_conf, p)
				self.project.save()
				self.save()
			else:
				return self.rc.error(f'No project found: \'{name}\'')

		# In project
		def sel_project():
			return self.rc.quick('No project opened', RetCode.DENIED)

		@self.com(Com('printp pp', man="""printp\nPrints project config"""))
		def printp():
			if not self.project:
				return sel_project()
			o = []
			for k in self.project.conf.save():
				o.append(f'{k}: {self.project.conf.save()[k]}')
			return self.rc.quick('\n'.join(o))

		@self.com(Com('setp sp', man="""setp <key> <value>\nSets project config value by key"""))
		def setp():
			if not self.project:
				return sel_project()
			if len(self.rc.args) != 3:
				return self.rc.quick(f'2 args are required, found {len(self.rc.args) - 1}', RetCode.ARGS_ERROR)
			k = self.rc.get_arg(1)
			if k == 'build_path':
				self.project.conf.build_path = self.rc.get_arg(2)
			elif k == 'github':
				self.project.conf.github = self.rc.get_arg(2)
			else:
				return self.rc.quick(f'Key: \'{k}\' not found', RetCode.ARGS_ERROR)
			self.project.save()
			return self.rc.quick()

		@self.com(Com('folder f', man="""folder\nOpen project folder"""))
		def folder():
			if not self.project:
				return sel_project()
			if not os_path.exists(self.project.path):
				return self.rc.error('Project folder does not exist')
			self.project.open_folder(self.global_conf.open_folder)

		@self.com(Com('github gh', man="""github\nOpen github page"""))
		def github():
			if not self.project:
				return sel_project()
			self.project.open_github(self.global_conf.open_web)

		@self.com(Com('spec', man="""spec\nCreates spec file"""))  # TODO Overwrite main file path
		def spec():
			if not self.project:
				return sel_project()
			if os_path.exists(os_path.join(self.project.path, f'{self.project.name}.spec')):
				return self.rc.error('Spec file already exists')
			self.project.create_spec()

		@self.com(Com('build', man="""build\nBuilds project on build_path"""))
		def spec():
			if not self.project:
				return sel_project()
			if not os_path.exists(os_path.join(self.project.path, f'{self.project.name}.spec')):
				return self.rc.error('No spec file found (run `spec` command first)')
			self.project.build()


def main():
	n = Ncui()
	if len(argv) == 1:  # No arg
		n.quick_run('version')
		n.quick_run_loop()
	elif len(argv) == 2:  # One arg (build, github, version)
		n.quick_run(argv[1])
	elif len(argv) > 2:  # More args (project build) or (add .)
		if n.global_conf.get_project(argv[1]):  # If first arg is project name
			n.quick_run(f"cd {argv[1]} | {' '.join(argv[2:])}")
		else:
			n.quick_run(' '.join(argv[1:]))
	n.save()


default_cscript = """# Type # to comment line (works only at the start of the line)
# Your pwd/cwd is set project path
# All commads are going to be executed as batch script
# Dont forget: window uses \\ as path separator
# Here are some useful commands:
# cd/chdir - change current pwd/cwd
# md/mkdir - makes new directory
# rd/rmdir /Q /S - removes none empty directory
# ren/rename - rename directory

@echo off
md {:name
cd {:name
	md {:lname
	cd {:lname
		echo def main():>> __main__.py
		echo 	print("Hello world!")>> __main__.py
		echo.>> __main__.py
		echo.>> __main__.py
		echo if __name__ == '__main__':>> __main__.py
		echo 	main()>> __main__.py
	cd ..
	md doc
		cd doc
		md dev
		md usr
	cd ..
	echo [[source]] >> Pipfile
	echo name = "pypi">> Pipfile
	echo url = "https://pypi.org/simple">> Pipfile
	echo verify_ssl = true>> Pipfile
	echo.>> Pipfile 
	echo [dev-packages]>> Pipfile
	echo.>> Pipfile 
	echo [packages]>> Pipfile
	echo.>> Pipfile 
	echo [requires]>> Pipfile
	echo python_version = "3.8">> Pipfile

	echo # {:name>> README.md
	# TODO Licence
echo cscript done
"""

if __name__ == '__main__':
	main()

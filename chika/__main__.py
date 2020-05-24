import json
from os import path as os_path
from sys import path as sys_path
from typing import Union

import pkg_resources

from chika.conf import GlobalConf
from chika.ncui3.api import Api
from chika.ncui3.com import Com
from chika.ncui3.consts import RetCode
from chika.project import Project


class Ncui(Api):
	def __init__(self):
		super().__init__()
		self.conf_path = os_path.join(sys_path[-1], 'chika')
		self.global_conf = self.load()
		self.project: Union[Project, None] = None

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

	def set_commands(self):
		self.com(Com('e q exit quit', self.rc.quick, None, {'code': RetCode.EXIT}, man="""exit\nExit from chika shell"""))

		@self.com(Com('version v', man="""version\nPrints Chika version."""))
		def version():
			return self.rc.quick(f'Chika v{pkg_resources.require("chika")[0].version}')

		@self.com(Com('printg pg', man="""printg\nPrints global config."""))
		def printg():
			o = []
			for k in self.global_conf.save():
				if k != 'projects':
					o.append(f'{k}: {self.global_conf.save()[k]}')
			return self.rc.quick('\n'.join(o))

		@self.com(Com('setg sg', man="""setg <key> <value>\nPrints global config."""))
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
			return self.rc.quick()

		@self.com(Com('initp ip', man="""initp <path> <name>\nAdds new project and run cscript"""))  # TODO option with default path=. (only 1 arg: name)
		def initp():
			if len(self.rc.args) != 3:
				return self.rc.quick(f'2 args are required, found {len(self.rc.args) - 1}', RetCode.ARGS_ERROR)
			self.project = Project(self.global_conf, self.rc.get_arg(1), self.rc.get_arg(2))
			p = os_path.join(self.conf_path, 'cscript.txt')
			if os_path.exists(p):
				with open(p) as f:
					cs = f.read()
			else:
				cs = default_cscript
				with open(p, 'w') as f:
					f.write(cs)
			self.project.run_cscript(cs, self.conf_path)


def main():
	n = Ncui()
	# n.quick_run('ip . Qwer')
	n.quick_run_loop()
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
	echo pyinstaller = "*">> Pipfile
	echo.>> Pipfile 
	echo [requires]>> Pipfile
	echo python_version = "3.8">> Pipfile

	echo # {:name>> README.md
	# TODO Licence
echo cscript done
"""

if __name__ == '__main__':
	main()

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
		self.conf_path = os_path.join(sys_path[-1], 'chika', 'conf.json')
		self.global_conf = self.load()
		self.project: Union[Project, None] = None

	def load(self) -> GlobalConf:
		if os_path.exists(self.conf_path):
			with open(self.conf_path) as f:
				return GlobalConf(json.load(f))
		else:
			return GlobalConf({})

	def save(self):
		with open(self.conf_path, 'w') as f:
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


def main():
	n = Ncui()
	n.quick_run_loop()
	n.save()


if __name__ == '__main__':
	main()

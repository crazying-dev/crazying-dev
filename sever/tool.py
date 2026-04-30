import os
import random


def get_random_file(dir_path):
	# 收集所有文件
	files = []
	for name in os.listdir(dir_path):
		fp = os.path.join(dir_path, name)
		if os.path.isfile(fp):
			files.append(fp)
	if not files:
		return None
	return os.path.abspath(os.path.normpath(random.choice(files)))

import json

# returns a list of all files in a directory
def walk(dir):
	assert dir['type'] == 'dir'
	files, folders = [], []
	for name, obj in dir['contents'].items():
		if obj['type'] == 'file':
			files.append(obj['path'])
		else:
			folders.append(obj['path'])
			subfiles, subfolders = walk(obj)
			files += subfiles
			folders += subfolders
	return files, folders

# gets all files unique to dir 1 (not in dir 2)
def diff_helper(dir1, dir2):
	if dir1['hash'] == dir2['hash']:
		return []

	files = []
	for name, obj in dir1['contents'].items():
		assert obj['type'] == 'file' or obj['type'] == 'dir'
		if obj['type'] == 'file':
			if not (
				name in dir2['contents']
				and dir2['contents'][name]['hash'] == obj['hash']
				and dir2['contents'][name]['type'] == 'file'
			):
				files.append(obj['path'])
		
		if obj['type'] == 'dir':
			if name not in dir2['contents']:
				files += walk(obj)[0]
				continue
			if dir2['contents'][name]['hash'] == obj['hash']:
				continue
			if dir2['contents'][name]['type'] == 'file':
				files += walk(obj)[0]
			else:
				r = diff_helper(obj, dir2['contents'][name])
				files += diff_helper(obj, dir2['contents'][name])
	return files

# acc: (PATHs of unique files/dirs in dir1, PATHs of unique files/dirs in dir2)
def diff(dir1, dir2):
	assert dir1['type'] == 'dir' and dir2['type'] == 'dir'
	dir1_unique = diff_helper(dir1, dir2)
	dir2_unique = diff_helper(dir2, dir1)
	return (dir1_unique, dir2_unique)
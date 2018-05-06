import json
import pprint
with open('tree1.json') as f:
	tree1 = json.load(f)

with open('tree2.json') as f:
	tree2 = json.load(f)

# acc: (PATHs of unique files/dirs in dir1, PATHs of unique files/dirs in dir2)
def walk(dir1, dir2, acc):

	dir1_unique, dir2_unique = [], []

	for name, obj in dir1['contents'].items():
		if obj['type'] == 'file':
			if name in dir2['contents']:
				if not obj['hash'] == dir2['contents'][name]['hash'] and dir2['contents'][name]['type'] == 'file':
					dir1_unique.append(obj['path'])
					# dir2_unique.append(dir2['contents'][name]['path'])
			else:
				dir1_unique.append(obj['path'])
		if obj['type'] == 'dir':
			if name in dir2['contents']:
				if not obj['hash'] == dir2['contents'][name]['hash'] and dir2['contents'][name]['type'] == 'dir':
					walk(obj, dir2['contents'][name], acc)
			else:
				dir1_unique.append(obj['path'])

	for name, obj in dir2['contents'].items():
		if obj['type'] == 'file':
			if name in dir1['contents']:
				if not obj['hash'] == dir1['contents'][name]['hash'] and dir2['contents'][name]['type'] == 'file':
					dir2_unique.append(obj['path'])
					# dir2_unique.append(dir2['contents'][name]['path'])
			else:
				dir2_unique.append(obj['path'])
		if obj['type'] == 'dir':
			if name in dir1['contents']:
				if not obj['hash'] == dir1['contents'][name]['hash'] and dir2['contents'][name]['type'] == 'dir':
					walk(dir1['contents'][name], obj, acc)
			else:
				dir2_unique.append(obj['path'])

	return acc[0] + dir1_unique, acc[1] + dir2_unique

pprint.pprint(walk(tree1, tree2, ([], [])))

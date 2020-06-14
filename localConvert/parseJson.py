import json

def HLSHandlingProcess(kwargs):
	# kwargs['ContainerSettings']
	for items in kwargs:
		print(items)

def DASHHandlingProcess(kwargs):
	pass

with open('outputFormatSetting.json') as setting:
	kwargs = json.load(setting)
	# print(kwargs)
	for outputGrp in kwargs['OutputGroups']:
		name = outputGrp['CustomName']
		settingsGeneral = outputGrp['Outputs']
		print(settingsGeneral)

		if name == 'HLS':
			HLSHandlingProcess(settingsGeneral)

		elif name == 'DASH':
			DASHHandlingProcess(settingsGeneral)
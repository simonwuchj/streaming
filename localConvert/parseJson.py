import json
from job import Job

#  Fragment length must be a whole number and must be a multiple of this value: 
#  GOP size x Closed GOP cadence ÷ Framerate
def HlsHandlingProcess(settings):
	streamName = 'hls'
	jobs = list()
	try:
		for setting in settings:
			job = Job()
			job.nameModifier = setting['NameModifier'] # _360, _720
			job.resolution = job.nameModifier[1:]

			job.streamFormat = 'hls'
			job.outputFormat = setting['ContainerSettings']['Container'].lower() # M3U8
			job.width, job.height = setting['VideoDescription']['Width'], setting['VideoDescription']['Width']

			vidCodecSetting = setting['VideoDescription']['CodecSettings']
			if vidCodecSetting['Codec'] == 'H_264': # temporarily support h264
				job.vidsSettings['numOfRefFrame'] = vidCodecSetting['H264Settings']['NumberReferenceFrames']
				# GOP - key frame interval
				job.vidsSettings['GOPClosedCadence'] = vidCodecSetting['H264Settings']['GopClosedCadence']
				job.vidsSettings['GOPSize'] = vidCodecSetting['H264Settings']['GopSize']
				job.vidsSettings['bitrate'] = vidCodecSetting['H264Settings']['Bitrate']
				job.vidsSettings['codec'] = 'H_264'


			audioCodecSetting = setting['AudioDescriptions'][0]['CodecSettings']
			if audioCodecSetting['Codec'] == 'AAC':
				job.audioSettings['bitrate'] = audioCodecSetting['AacSettings']['Bitrate']
				job.audioSettings['sampleRate'] = audioCodecSetting['AacSettings']['SampleRate']
				job.audioSettings['spec'] = audioCodecSetting['AacSettings']['Specification']
				job.audioSettings['codec'] = 'AAC'

			jobs += [job]

	except Exception as e:
		print(e)
		jobs = list() # clear out this section if exceptions occur

	return jobs

def DashHandlingProcess(settings):
	pass

def parseAWSJsonSetting(filePath):
	jobs = list()
	with open(filePath) as setting:
		kwargs = json.load(setting)
		for outputGrp in kwargs['OutputGroups']:
			name = outputGrp['CustomName']
			settingsGeneral = outputGrp['Outputs']

			if name == 'HLS':
				hlsjobs = HlsHandlingProcess(settingsGeneral)
				jobs += hlsjobs

			elif name == 'DASH':
				dashjobs = DashHandlingProcess(settingsGeneral)
				jobs += dashjobs

	return jobs


if __name__ == '__main__':
	jobs = parseAWSJsonSetting('outputFormatSetting.json')
	print(jobs)

class Job(object):
	def __init__(self):
		self.nameModifier = None # aws usually use it to refer resolution
		self.resolution = None

		self.streamFormat = None # hls, dash ...
		self.outputFormat = None # m3u8, mp4 ...

		self.width = None
		self.height = None

		self.hlsInitTime = 0
		self.hlsTime = 10
		self.hlsListSize = 0

		self.vidsSettings = dict()
		self.audioSettings = dict()

	def get_hls_init_time(self):
		return self.hlsInitTime 

	def get_hls_time(self):
		return self.hlsTime

	def get_hls_list_size(self):
		return self.hlsListSize

	def get_bitrate(self):
		return self.vidsSettings['bitrate'], self.audioSettings['bitrate']

	def get_job_name(self):
		return self.streamFormat + '-' + self.resolution + '-' + \
					self.vidsSettings['codec'] + '-' + \
					self.audioSettings['codec']

	def get_output_file_name(self):
		return self.streamFormat + '_' + self.resolution + '_' + \
					self.vidsSettings['codec'] + '_' + \
					self.audioSettings['codec']+ '.' + self.outputFormat
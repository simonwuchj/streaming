import ffmpeg
import os
from parseJson import parseAWSJsonSetting

def emptyFolder(path):
	files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	dirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
	
	for f in files:
		os.remove(f)

	for d in dirs:
		emptyFolder(d)
		os.rmdir(d)

def makeNameDst(srcPath, job):
	baseDir, videoName = os.path.split(srcPath)
	vNameNoSuffix, _ = videoName.split('.')
	outputDir = os.path.join(baseDir, vNameNoSuffix + '-Output-' + job.get_job_name())

	if os.path.isdir(outputDir):
		emptyFolder(outputDir)
		os.rmdir(outputDir)

	os.mkdir(outputDir)
	return os.path.join(outputDir, vNameNoSuffix + '_' + job.get_output_file_name())

def generateShellCMD(inputFileAbsPath, outputFileAbsPath, job):
	cmd = 'echo' # by default nothing

	if job.streamFormat == 'hls':
		start = job.get_hls_init_time()
		hlstime = job.get_hls_time()
		hlslistsize = job.get_hls_list_size()
		vbitrate, abitrate = job.get_bitrate()

		width, height = job.width, job.height

		cmd = f'ffmpeg -i {inputFileAbsPath} -vf scale={width}:{height} \
			-start_number {start} -hls_time {hlstime} -hls_list_size {hlslistsize} -f hls {outputFileAbsPath}'

	elif job.streamFormat == 'dash':
		# TODO
		pass

	return cmd


def convert(videoSrcPath, configPath):
	jobs = parseAWSJsonSetting(configPath)
	for job in jobs[:1]:
		outputFile = makeNameDst(videoSrcPath, job)
		cmd = generateShellCMD(videoSrcPath, outputFile, job)
		os.system(cmd)

if __name__ == '__main__':
	cwd = os.getcwd()
	convert(os.path.join(cwd, 'JFla.mp4'), 
			os.path.join(cwd, 'outputFormatSetting.json'))


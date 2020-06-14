import ffmpeg
import os

def emptyFolder(path):
	files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	dirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
	
	for f in files:
		os.remove(f)

	for d in dirs:
		emptyFolder(d)
		os.rmdir(d)

def makeNameDst(srcPath, args):
	baseDir = os.path.dirname(srcPath)
	outputDir = os.path.join(baseDir, 'Result')

	if os.path.isdir(outputDir):
		emptyFolder(outputDir)
		os.rmdir(outputDir)

	os.mkdir(outputDir)
	containerSetting = args['ContainerSettings']

	resolution = args['NameModifier'] # in form of _720


def convert(srcPath):
	ffmpeg.input(inptFile).output(outputFile, format='hls', 
			start_number=0,
			hls_time=10,
			hls_list_size=0
		)


if __name__ == '__main__':
	convert()

import ffmpeg
import os

ffmpeg.input('JFla.mp4').output('JFla_transcode.m3u8', format='hls', 
			start_number=0,
			hls_time=10,
			hls_list_size=0
		).run()
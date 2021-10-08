# Purges tracks based on user input
from pathlib import Path
import pymkv

current_directory = (Path.cwd()).resolve()
output_directory = (current_directory / 'output').resolve()

def create_folder():
	'''Creates the output folder if it doesn't already exist'''

	if not output_directory.exists():
		output_directory.mkdir()
	

def demux(mkv, mkvfile, count):

	if count:
		for _ in range(count):
			mkv.remove_track(0)
		mkv.mux(output_directory / mkvfile, silent=True)
	else:
		print('No Tracks To Remove')


def display_track(track, i):
	'''Displays the tracks for a given mkvfile'''

	print('{0:02d}: TRACK NAME: {1}, TRACK TYPE: {2}, TRACK LANGUAGE: {3}'.format(i, track.track_name, track.track_type, track.language))


def remove(mkv, tracks, choice):
	'''Chooses the tracks to remove from the mkvfile'''

	print('\nTracks Present:')

	for i, track in enumerate(tracks, 1):
		display_track(track, i)

	count = 0
	TID = 0

	print('\nRemoving Tracks:')
	for track in tracks:
		try:
			if (choice == 1) and ((track.track_type == 'audio' and track.language not in ['jpn', 'und']) or \
				(track.track_type == 'subtitles' and track.language not in ['eng', 'und']) or \
				('sign' in track.track_name.lower()) or ('eng' in track.track_name.lower() and track.track_type != 'subtitles')):

				TID = track.track_id
				

			elif (choice == 2) and ('commentary' in track.track_name):
				TID = track.track_id

			else:
				continue

		except Exception as e:
			print('{0:02d}: ERROR:'.format(TID + 1), e, ', SKIPPING TRACK')
			continue

		mkv.move_track_front(TID)
		count += 1
		display_track(track, TID + 1)

	return count		


def main():
	create_folder()
	mkvfiles = sorted([item for item in current_directory.iterdir() if item.suffix == '.mkv' and not item.is_dir()])

	choice = int(input('1) Remove Only Dub\n2) Remove Only Commentary\nChoice: '))

	if choice not in  [1, 2]:
		exit(0)

	for mkvfile in mkvfiles:
		print('-----------------------------------------')
		print('\nWorking File: ', mkvfile.name, end='\n\n')

		try:
			mkv = pymkv.MKVFile(mkvfile)
		except KeyError as e:
			print('ERROR:', e, 'NOT RECOGNIZED, SKIPPING CURRENT FILE')
			continue

		mkv.no_global_tags()
		tracks = mkv.get_track()

		count = remove(mkv, tracks, choice)
		demux(mkv, mkvfile.name, count)

	print('\nDone')


if __name__ == '__main__':
	main()
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



def display_track(track, i, err=''):
	'''Displays the tracks for a given mkvfile'''

	if err != '':
		print('{:<3} {:<10} {:<10} {:<25} {:<25}'.format(i, track.track_type, track.language, str(track.track_name), err))
	else:

		print('{:<3} {:<10} {:<10} {:<25}'.format(i, track.track_type, track.language, str(track.track_name)))


def remove(mkv, tracks, choice):
	'''Chooses the tracks to remove from the mkvfile'''

	print('\nTracks Present:')
	print('\n{:<3} {:<10} {:<10} {}\n----------------------------------------------'.format('ID', 'Type', 'Language', 'Name'))

	for i, track in enumerate(tracks, 1):
		display_track(track, i)

	count = 0
	TID = 0
	errors = []

	print('\nRemoving Tracks:')
	print('\n{:<3} {:<10} {:<10} {}\n----------------------------------------------'.format('ID', 'Type', 'Language', 'Name'))
	for track in tracks:
		try:
			if ('1' in choice) and ((track.track_type == 'audio' and track.language not in ['jpn', 'und']) or \
				(track.track_type == 'subtitles' and track.language not in ['eng', 'und']) or \
				('sign' in track.track_name.lower()) or ('eng' in track.track_name.lower() and track.track_type != 'subtitles')):

				TID = track.track_id
				mkv.move_track_front(TID)
				count += 1
				display_track(track, TID + 1)


			if ('2' in choice) and ('commentary' in track.track_name):
				TID = track.track_id
				mkv.move_track_front(TID)
				count += 1
				display_track(track, TID + 1)

		except Exception as e:
			errors.append((track, e))
			continue

	if errors:
		print('\nErrors while parsing, these tracks were skipped from being purged')
		print('\n{:<3} {:<10} {:<10} {:<25} {}\n----------------------------------------------'.format('ID', 'Type', 'Language', 'Name', 'Err Msg'))
		for track, error in errors:
			display_track(track, track.track_id + 1, err=str(error))


	return count		


def main():
	create_folder()
	mkvfiles = sorted([item for item in current_directory.iterdir() if item.suffix == '.mkv' and not item.is_dir()])

	print('\n\n----------------------------------------------')
	print("Found the following files")
	print('----------------------------------------------')
	for i, mkvfile in enumerate(mkvfiles, 1):
		print(f"{i}) {mkvfile.name}",end="\n")
	print('----------------------------------------------\n\n')
		


	choice = input('1) Remove Only Dub\n2) Remove Only Commentary\nChoice: ')

	if choice not in  ['1', '2', '21', '12']:
		exit(0)

	for mkvfile in mkvfiles:
		print('\n\n----------------------------------------------')
		print('Working File: ', mkvfile.name, end='\n')
		print('----------------------------------------------')

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
	
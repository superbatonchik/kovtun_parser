import logging
import os
import requests
import yaml
from vk_api.audio import VkAudio
import get


DOWNLOAD_THREADS = 4

class TracksProcessor:
    #__slots__ = ('_api', '_session', '_vkAudio')

    def __init__(self, session, output_dir):
        self._logger = logging.getLogger(__name__)
        self._api = session.get_api()
        self._session = session
        self._vk_audio = VkAudio(self._session)
        self._me = self._api.users.get()[0]
        self._tracks = []
        self._last_added_tracks = []
        self._output_dir = output_dir
        self._history = self.reload_history(output_dir)

    def reload_history(self, odir):
        path = os.path.join(odir, '_history.yaml')
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.load(f.read())
        return {}

    def save_history(self, odir):
        path = os.path.join(odir, '_history.yaml')
        with open(path, 'w') as f:
            yaml.dump(self._history, f)

    def populate(self):
        self._tracks = self._vk_audio.search_user(self._me['id'], 'Anxietas')
        for track in self._tracks:
            track['dur'] = int(track['dur'])
            track['id'] = int(track['id'].split('_')[1])
            track['filename'] = '{} - {}.mp3'.format(track['artist'], track['title'])
        return self._tracks

    def get_tracks(self):
        return self._tracks

    def find_track(self, track_id):
        track = next((x for x in self._tracks if x['id'] == track_id), None)
        return track

    def find(self, audio_artist, audio_title):
        track_id = next((x['id'] for x in self._tracks if x['title'] == audio_title and x['artist'] == audio_artist), None)
        return track_id

    def add(self, owner_id, audio_id):
        new_id = self._api.audio.add(audio_id=audio_id, owner_id=owner_id)
        self._last_added_tracks.append(new_id)
        self.populate()

    def set_track_data(self, track_id, track_data):
        track = self.find_track(track_id)
        track['track_data'] = track_data
        last = track['track_data'][-1]
        last['end'] = track['dur'] - last['start']

    def process(self, track_id):
        if track_id not in self._history:
            self._history[track_id] = {
                'download_status': 'new',
                'split_status': 'new'
            }
        hst = self._history[track_id]
        track = self.find_track(track_id)
        if hst['download_status'] == 'new' \
                and get.download(track['url'], os.path.join(self._output_dir, track['filename']), DOWNLOAD_THREADS):
            hst['download_status'] = 'downloaded'
        self.save_history(self._output_dir)

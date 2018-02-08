import re

class ProstsProcessor:

    def __init__(self):
        self._empty_post = {'empty': True}
        self._re_all_tracks = re.compile('\d{2}:\d{2}\s*.+\s*-\s*.+')
        self._re_track = re.compile('(?P<start>\d{2}:\d{2})\s*(?P<artist>.+)\s*-\s*(?P<title>.+)')

    def extract(self, post_data):
        post = {'empty': False}
        if 'copy_history' in post_data or 'attachments' not in post_data:
            self._empty_post['empty_reason'] = 'no attachments or this is repost'
            return self._empty_post
        audio_attachment = next((x['audio'] for x in post_data['attachments'] if 'audio' in x), None)
        if not audio_attachment:
            self._empty_post['empty_reason'] = 'no audio attachments'
            return self._empty_post
        post['audio_attachment'] = audio_attachment
        if 'Anxietas' not in audio_attachment['title']:
            self._empty_post['empty_reason'] = 'this is not Anxietas track, skipping'
            return self._empty_post
        text = post_data['text']
        post['audio_attachment']['tracks_info'] = []
        all_tracks_info_str = self._re_all_tracks.findall(text)
        for i in range(len(all_tracks_info_str)):
            tracks_info_str = all_tracks_info_str[i]
            matches = self._re_track.search(tracks_info_str)
            track_info = {
                'start': self.__get_secs(matches.group('start'), ':'),
                'end': -1,
                'artist': matches.group('artist'),
                'title': matches.group('title')
            }
            if i < len(all_tracks_info_str) - 1:
                tracks_info_str_n = all_tracks_info_str[i+1]
                matches_n = self._re_track.search(tracks_info_str_n)
                track_info['end'] = self.__get_secs(matches_n.group('start'), ':')
            post['audio_attachment']['tracks_info'].append(track_info)
        return post

    def __get_secs(self, hh_ss, delim):
        time_hh_ss = [int(x) for x in hh_ss.split(delim)]
        return time_hh_ss[0] * 60 + time_hh_ss[1]

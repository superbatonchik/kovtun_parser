import logging
import argparse
import vk_api
import tracks_processor
import posts_processor
import setup_logging

setup_logging.setup_logging()

KOVTUN_ID = 138383535


def auth(login, password):
    session = vk_api.VkApi(login, password)
    #session = vk_api.VkApi(login, password, scope='notes,audio,wall,nohttps')
    session.auth()
    return session


def main(args):
    logger = logging.getLogger('main')

    login = args.user
    password = args.password
    session = auth(login, password)
    tools = vk_api.VkTools(session)

    logger.info('vk version: %s', session.api_version)

    track_processor = tracks_processor.TracksProcessor(session, args.output)
    #track_processor.populate()
    post_processor = posts_processor.PostsProcessor()

    posts = tools.get_all_iter('wall.get', 1, {'owner_id': KOVTUN_ID, 'filter': 'owner'})
    for post in posts:
        print('##################################')
        post_info = post_processor.extract(post)
        if post_info['empty']:
            continue
        audio_attachment = post_info['audio_attachment']
        track_id = track_processor.find(audio_attachment['artist'], audio_attachment['title'])
        if not track_id:
            # track_id = track_processor.add(audio_attachment['owner_id'], audio_attachment['id'])
            logger.info('added track %d %s %s', track_id, audio_attachment['artist'], audio_attachment['title'])
        track_processor.set_track_data(track_id, audio_attachment['tracks_info'])
        track_processor.process(track_id)


if __name__ == '__main__':
    cli = argparse.ArgumentParser()
    cli.add_argument('-o', '--output', help='Output directory', action='store')
    cli.add_argument('-u', '--user', help='VK Login', action='store')
    cli.add_argument('-p', '--password', help='VK Password', action='store')
    args = cli.parse_args()
    main(args)

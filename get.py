import requests
import threading
import logging
import tqdm

logger = logging.getLogger('download')


def handle_chunk(start, end, url, filename, chunk_num):
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url, headers=headers, stream=True)
    with open(filename, "r+b") as file:
        file.seek(start)
        file.tell()
        for data in tqdm.tqdm(r.iter_content(),
                              total=end - start,
                              unit='B',
                              unit_scale=True,
                              desc='Downloading part ' + chunk_num):
            file.write(data)


def download(url, filename, thread_count):
    main_thread = threading.current_thread()
    head = requests.head(url)
    try:
        file_size = int(head.headers['Content-Length'])
    except:
        logger.error('Invalid URL ')
        return False
    with open(filename, 'wb') as file:
        file.write('\0' * file_size)
    chunk_size = int(file_size / thread_count)

    for i in range(thread_count):
        start = i * chunk_size
        end = start + chunk_size
        i_thread = threading.Thread(target=handle_chunk, kwargs={'start': start, 'end': end, 'url': url, 'filename': filename, 'chunk_num': i})
        i_thread.setDaemon(True)
        i_thread.start()

    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    return True

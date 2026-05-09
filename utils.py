import os
from urllib.parse import urlencode, parse_qs, urlparse


def format_bytes(n):
    if n is None:
        return 'Unknown'
    n = float(n)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}'
        n /= 1024
    return f'{n:.1f} PB'


def format_eta(seconds):
    if seconds is None:
        return '--:--:--'
    seconds = int(seconds)
    h, s = divmod(seconds, 3600)
    m, s = divmod(s, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def default_output_dir():
    return os.path.expanduser('~/Downloads/nj-downloader')


def clean_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    if 'youtube.com' not in netloc and 'youtu.be' not in netloc:
        return url

    is_single_video = (
        parsed.path.startswith('/watch')
        or 'youtu.be' in netloc
        or parsed.path.startswith('/shorts')
    )

    if not is_single_video:
        return url

    params = parse_qs(parsed.query)
    if 'list' not in params:
        return url

    cleaned = {k: v for k, v in params.items() if k not in ('list', 'index')}
    new_query = urlencode(cleaned, doseq=True) if cleaned else ''

    return parsed._replace(query=new_query).geturl()

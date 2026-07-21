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


def extract_size_for_quality(info, quality):
    if not info:
        return None

    quality_map = {
        'Best': float('inf'),
        '4K (2160p)': 2160,
        '2K (1440p)': 1440,
        '1080p': 1080,
        '720p': 720,
        '480p': 480,
        '360p': 360,
        'Audio Only': 0,
    }
    max_height = quality_map.get(quality)
    if max_height is None:
        return None

    formats = info.get('formats', [])
    if not formats:
        return info.get('filesize') or info.get('filesize_approx')

    if max_height == 0:
        best_size = None
        for f in formats:
            if f.get('acodec') and f.get('acodec') != 'none':
                size = f.get('filesize') or f.get('filesize_approx')
                if size and (best_size is None or size > best_size):
                    best_size = size
        return best_size

    best_video_size = None
    best_audio_size = None
    for f in formats:
        h = f.get('height')
        vcodec = f.get('vcodec', '')
        acodec = f.get('acodec', '')
        size = f.get('filesize') or f.get('filesize_approx')

        is_video = vcodec and vcodec != 'none'
        is_audio = (not is_video) and acodec and acodec != 'none'

        if is_video and h and h <= max_height:
            if size and (best_video_size is None or size > best_video_size):
                best_video_size = size

        if is_audio:
            if size and (best_audio_size is None or size > best_audio_size):
                best_audio_size = size

    if best_video_size is not None and best_audio_size is not None:
        return best_video_size + best_audio_size
    if best_video_size is not None:
        return best_video_size
    return best_audio_size

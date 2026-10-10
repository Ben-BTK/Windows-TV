from windows_tv.playlist import parse_m3u


def test_parses_extinf_metadata_and_url():
    text = '''#EXTM3U
#EXTINF:-1 tvg-id="demo.one" tvg-name="Demo Eins" tvg-logo="https://example.com/logo.png" group-title="Regional",Demo Sender
https://example.com/live.m3u8
'''
    channels = parse_m3u(text)
    assert len(channels) == 1
    channel = channels[0]
    assert channel.name == "Demo Eins"
    assert channel.tvg_id == "demo.one"
    assert channel.logo == "https://example.com/logo.png"
    assert channel.group == "Regional"
    assert channel.url == "https://example.com/live.m3u8"


def test_ignores_unsupported_schemes():
    channels = parse_m3u("#EXTM3U\n#EXTINF:-1,Local file\nfile:///C:/video.mp4\n")
    assert channels == []


def test_accepts_bare_http_stream_url():
    channels = parse_m3u("https://example.com/channel")
    assert len(channels) == 1
    assert channels[0].url == "https://example.com/channel"

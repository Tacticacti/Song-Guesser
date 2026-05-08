import vlc
import time

test_audio_link = 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/a3/99/47/a3994781-df89-22dc-06c5-48a5ceeead17/mzaf_15097120298091479602.plus.aac.p.m4a'

instance = vlc.Instance('--quiet')
player = instance.media_player_new()
player.set_media(instance.media_new(test_audio_link))

player.play()
time.sleep(40)
import vlc

def play_audio(preview_link):
    test_audio_link = f'{preview_link}'
    instance = vlc.Instance('--quiet')
    player = instance.media_player_new()
    player.set_media(instance.media_new(test_audio_link))

    player.play()
    return player
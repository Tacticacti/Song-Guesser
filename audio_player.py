import vlc

def play_audio(preview_link):
    test_audio_link = f'{preview_link}'
    instance = vlc.Instance('--quiet')
    player = instance.media_player_new()
    player.set_media(instance.media_new(test_audio_link))

    player.play()
    return player

def set_volume(player, volume_level):
    safe_volume = max(0, min(100, volume_level))
    player.audio_set_volume(safe_volume)
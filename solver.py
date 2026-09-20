

def design_playlist(tracks, target_min):
    print(f"Number of tracks selected: {len(tracks)}")
    possible_times = {0:[]}
    for track in tracks:
        track_id = track[0]
        track_time = track[1]
        for time in possible_times.copy().keys():
            new_time = time + track_time
            if new_time > target_min*60*1.1:
                 continue
            if track_id in possible_times[time]:
                continue
            new_track_path = possible_times[time]+[track_id]
            possible_times.update({new_time:new_track_path})

    best_time = min(possible_times.keys(), key= lambda x: abs(x-target_min*60))
    playlist_track_ids = possible_times[best_time]
    return playlist_track_ids
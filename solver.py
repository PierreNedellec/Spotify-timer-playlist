import random


def design_playlist(tracks, target_s, tolerance=0.1):
    tracks = tracks[:]
    random.shuffle(tracks)
    limit = target_s * (1 + tolerance)

    possible_times = {0: []}
    for track_id, track_time in tracks:
        for time, path in list(possible_times.items()):
            new_time = time + track_time
            if new_time > limit or new_time in possible_times:
                continue
            possible_times[new_time] = path + [track_id]

    best_time = min(possible_times, key=lambda t: abs(t - target_s))
    return possible_times[best_time], best_time
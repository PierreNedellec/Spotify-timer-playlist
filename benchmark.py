import random
import time
import multiprocessing as mp
import pandas as pd
random.seed(0)

"""
v1: heuristic - fill playlist to overshoot target, then swap until a close match is made
v2: brute force - every possible playlist time computed
v3: dynamic programming - one playlist per reachable time in seconds
v4: v3 with snapshot fix and shuffle capability

track data: [(t0,time_in_ms),...]
"""
                         
def execute_benchmark():
    # [algo, # tracks, target, runtime, gap]
    results = []
    possible_targets_min = [5,10,20,60,120]
    numbers_of_tracks = [10,30,50,100,200,400]
    for cycle in range(5):
        for target_min in possible_targets_min:
            target_s = target_min*60
            for n_tracks in numbers_of_tracks:
                print(f"Running test {n_tracks} tracks and target {target_min}min. Cycle {cycle}.")
                tracks_data = generate_tracks(n_tracks)
                for algo in [design_playlist_v1,design_playlist_v2,design_playlist_v3,design_playlist_v4]:
                    playlist_time, runtime = time_it(algo,tracks_data,target_s)
                    if runtime == None:
                        gap = None
                        timed_out = True
                    else:
                        gap = abs(playlist_time - target_s)
                        timed_out = False
                    results.append({
                        "round": cycle,
                        "algo": algo.__name__,
                        "n_tracks": n_tracks,
                        "target_s": target_s,
                        "runtime_s": runtime,
                        "gap_s": gap,
                        "timed_out": timed_out
                    })
                    df = pd.DataFrame(results)
                    df.to_csv("docs/benchmark_results.csv", index=False)


def _worker(algo, tracks, target_s, queue):
    start = time.perf_counter()
    playlist_ids, playlist_time = algo(tracks, target_s)
    queue.put((playlist_time, time.perf_counter() - start))


def time_it(algo, tracks, target_s, limit=5):
    """Run algo in a separate process.
    Returns (playlist_time, seconds), or None if it ran longer than limit."""
    queue = mp.Queue()
    p = mp.Process(target=_worker, args=(algo, tracks[:], target_s, queue))
    p.start()
    p.join(timeout=limit)
    if p.is_alive():
        p.terminate()
        p.join()
        return None, None
    if p.exitcode != 0:
        return None, None
    return queue.get()

def generate_tracks(n):
    tracks = []
    for i in range(n):
        tracks.append(("t"+str(i),random.randint(45000,480000)))
    return tracks

def transform_track_ms_to_s(tracks):
    new_tracks = []
    for track_id, track_time in tracks:
        new_tracks.append((track_id,round(track_time/1000)))
    return new_tracks

def design_playlist_v4(tracks, target_s, tolerance=0.1):
    tracks = tracks[:]
    tracks = transform_track_ms_to_s(tracks)
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

def design_playlist_v3(tracks, target_s, tolerance=0.1):
    tracks = tracks[:]
    tracks = transform_track_ms_to_s(tracks)
    possible_times = {0:[]}
    for track in tracks:
        track_id = track[0]
        track_time = track[1]
        for time in possible_times.copy().keys():
            new_time = time + track_time
            if new_time > target_s*1.1:
                 continue
            if track_id in possible_times[time]:
                continue
            new_track_path = possible_times[time]+[track_id]
            possible_times.update({new_time:new_track_path})

    best_time = min(possible_times.keys(), key= lambda x: abs(x-target_s))
    return possible_times[best_time], best_time

def design_playlist_v2(tracks, target_s, tolerance=0.1):
    target_ms = target_s * 1000
    playlist = []
    possible_times = [0]
    possible_playlists = [[]]
    for track in tracks:
        new_times = []
        for n,time in enumerate(possible_times):
            if time > target_ms*(1+tolerance):
                continue
            new_times.append(track[1]+time)
            possible_playlists.append(possible_playlists[n] + [track[0]])
        possible_times += new_times

    best_time = min(possible_times, key= lambda x: abs(x-target_ms))
    playlist = possible_playlists[possible_times.index(best_time)]
    return playlist, round(best_time/1000)

def design_playlist_v1(tracks, target_s, tolerance=0.1):
    playlist = []
    target_ms = target_s * 1000

    def time(pl):
        playlist_time = 0
        for item in pl:
            playlist_time += item[1]
        return playlist_time

    while tracks and time(playlist) < target_ms:
        playlist.append(tracks.pop(0))

    def shouldBeSwapped(pl,duration_target):
        best = ['',-999999]
        for item in pl:
            if abs(item[1]-duration_target) < abs(best[1]-duration_target):
                best = item
        return best
    
    difference = time(playlist) - target_ms
    while tracks and abs(difference) > 100 : # Acceptable margin of error in ms
        next_track_length = tracks[0][1]
        tracks.append(playlist.pop(playlist.index(shouldBeSwapped(playlist,next_track_length + difference))))
        playlist.append(tracks.pop(0))
        difference = time(playlist) - target_ms

    playlist_ids = [track_id for track_id, time in playlist]
    return playlist_ids, round(time(playlist)/1000)

if __name__ == "__main__":
    execute_benchmark()
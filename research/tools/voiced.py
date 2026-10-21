"""Voice-led timing for narrated rationale videos.

Every cue is spoken first (Kokoro, offline), and the cue then lasts exactly as long as its
spoken line plus a short breath, so the picture, the subtitles and the voice move together
with no dead air. The same timeline renders the picture; the voice is then mixed over the
music bed (ducked) and muxed onto the picture.

    scenes, end, clips = lay_out(SCENES, cache_dir)
    ... V.render(spec, out_dir, name)              # picture + music bed
    narrated(spec, clips, music_mp4, narrated_mp4)  # picture + voice + ducked bed
"""

import hashlib
import os
import subprocess

import numpy as np
import soundfile as sf

import narrate as N
import rationale_video as V

_VOICE = {}


def _voice(name):
    if name not in _VOICE:
        _VOICE[name] = N.Voice(name)
    return _VOICE[name]


def speak(text, cache, voice="af_heart", speed=1.0):
    os.makedirs(cache, exist_ok=True)
    key = hashlib.sha1(("%s|%.3f|%s" % (voice, speed, text)).encode()).hexdigest()[:16]
    path = os.path.join(cache, key + ".wav")
    if os.path.exists(path):
        a, _ = sf.read(path, dtype="float32")
        return a
    a, _, _ = _voice(voice).say(text, speed)
    sf.write(path, a, N.TTS_SR)
    return a


def lay_out(scenes, cache, voice="af_heart", speed=1.0, gap=0.3, lead=0.35, tail=0.45):
    """Like rationale_video.layout, but each cue lasts as long as its spoken line.
    A cue may carry 'pause' (extra silence before it), 'hold' (after it) and 'speed'."""
    t = 0.0
    out, clips = [], {}
    for sc in scenes:
        s0 = t
        t += sc.get("lead", lead)
        cues = []
        for c in sc["cues"]:
            t += c.get("pause", 0.0)
            text = N.clean(c["text"])
            a = speak(text, cache, voice, c.get("speed", speed))
            d = len(a) / N.TTS_SR
            cues.append(dict(c, text=text, start=round(t, 3), end=round(t + d, 3), words=len(text.split())))
            clips[c["id"]] = a
            t += d + c.get("gap", gap) + c.get("hold", 0.0)
        t += sc.get("tail", tail)
        out.append(dict(sc, start=round(s0, 3), end=round(t, 3), cues=cues))
    return out, t, clips


def narrated(spec, clips, music_mp4, out_mp4, brand):
    """Mix the spoken cues over the ducked music bed and mux onto the rendered picture."""
    cues = [dict(c, audio=clips[c["id"]]) for sc in spec.scenes for c in sc["cues"]]
    bed = V.soundtrack(spec.total, spec.mcs_start, spec.boom_t, spec.title_start,
                       [sc["start"] for sc in spec.scenes], brand)
    v = N.voice_track(cues, spec.total)
    g = N.duck_gain(v)
    mix = bed * g[:, None] * 1.15 + v[:, None]
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak
    tmp = out_mp4 + ".wav"
    V.write_wav(tmp, mix)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", music_mp4, "-i", tmp,
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-map_metadata", "-1", "-metadata", "title=", "-shortest", "-movflags", "+faststart",
                    out_mp4], check=True)
    os.remove(tmp)
    return out_mp4

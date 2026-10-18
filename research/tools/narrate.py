"""Narrated version of a rationale video: reads every cue of the timeline with an offline
neural voice (Kokoro-82M, ONNX), fits each line inside its subtitle window, ducks the music
bed under the voice, and muxes the new soundtrack onto the existing (subtitled) picture.

Usage:
  python3 narrate.py timeline.json BRAND in.mp4 out.mp4 [--voice af_heart] [--report out.json]
         [--only 1.1,4.10]   (synthesise only these cues and write their WAVs next to out.mp4)

The voice model is the Apache-2.0 Kokoro-82M q8 export (npm package kokoro-q8-shards) and the
voice styles come from the npm package kokoro-js. Both are fetched once into ~/.cache/kokoro.
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request

import numpy as np
from scipy.signal import butter, resample_poly, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rationale_video as V  # noqa: E402

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "kokoro")
MODEL = os.path.join(CACHE, "kokoro-q8.onnx")
VOICES = os.path.join(CACHE, "voices.npz")
MODEL_SHA256 = "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478"
TTS_SR = 24000
SR = V.SR

# words read out differently from how they are spelled (phonemes in Kokoro's IPA set);
# each key is the phoneme string espeak gives, so a miss is detected
PHONEME_FIX = {
    "lˈɪɡtəˈɛs": "lˈɪɡtɑːs",            # LIGTA-S: LIG-tas
    "lˈɪɡtəz": "lˈɪɡtɑːs",              # Ligtas (Pinoy Centers)
    "bˈæntəwˈaɪ": "bˈɑːntaɪ",           # BANTA-Y: BAN-tai
    "ˈælbeɪ": "ɑːlbˈaɪ",                # Albay: al-BYE
    "mˈeɪɑːn": "mɑːjˈoʊn",              # Mayon: mah-YON
    "kˈæmɐlˌɪɡ": "kɑːmˈɑːlɪɡ",          # Camalig: kah-MAH-lig
    "lˈɛɡæzpi": "lɛɡˈɑːspi",            # Legazpi: leh-GAHS-pee
    "bˈæɹɐŋɡˌeɪ": "bɑːɹɑːŋɡˈaɪ",        # barangay: ba-rang-GUY
    "bˈæɹɐŋɡˌeɪz": "bɑːɹɑːŋɡˈaɪz",
    "ˈiːdz ˈiːdʒɪpti": "eɪˈiːdiːz iːdʒˈɪptaɪ",   # Aedes aegypti
    "pˈɪnɔɪ": "pɪnˈɔɪ",                 # Pinoy
    "lˈæhɑːɹ": "lˈɑːhɑːɹ",              # lahar: LAH-har
}

# spelled-out forms read more naturally than espeak's defaults
TEXT_FIX = [
    (r"\b(January|February|March|April|May|June|July|August|September|October|November|December) 2026\b",
     r"\1 twenty twenty-six"),
    (r"\bMCS\b", "M C S"),
    (r"\bCUSUM\b", "cue-sum"),
]


def fetch_npm(pkg, version, dest):
    url = "https://registry.npmjs.org/%s/-/%s-%s.tgz" % (pkg, pkg.split("/")[-1], version)
    data = urllib.request.urlopen(url, timeout=120).read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            if m.isfile():
                out = os.path.join(dest, pkg, os.path.normpath(m.name).lstrip("./"))
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "wb") as f:
                    f.write(tf.extractfile(m).read())
    return os.path.join(dest, pkg, "package")


def ensure_model():
    import hashlib
    os.makedirs(CACHE, exist_ok=True)
    if not os.path.exists(MODEL):
        d = fetch_npm("kokoro-q8-shards", "1.0.0", CACHE)
        with open(MODEL, "wb") as f:
            for i in range(6):
                f.write(open(os.path.join(d, "kokoro-q8.part%d.bin" % i), "rb").read())
    h = hashlib.sha256(open(MODEL, "rb").read()).hexdigest()
    if h != MODEL_SHA256:
        raise SystemExit("kokoro model checksum mismatch: " + h)
    if not os.path.exists(VOICES):
        d = fetch_npm("kokoro-js", "1.2.1", CACHE)
        vd = os.path.join(d, "voices")
        v = {f[:-4]: np.fromfile(os.path.join(vd, f), dtype=np.float32).reshape(510, 1, 256)
             for f in sorted(os.listdir(vd)) if f.endswith(".bin")}
        np.savez(VOICES, **v)


class Voice:
    def __init__(self, voice):
        import logging
        logging.getLogger("kokoro_onnx").setLevel(logging.ERROR)
        from kokoro_onnx import Kokoro
        ensure_model()
        self.k = Kokoro(MODEL, VOICES)
        self.voice = voice

    def phonemes(self, text):
        for pat, rep in TEXT_FIX:
            text = re.sub(pat, rep, text)
        ph = self.k.tokenizer.phonemize(text, "en-us")
        fixed = []
        for a, b in PHONEME_FIX.items():
            if a in ph:
                ph = ph.replace(a, b)
                fixed.append(b)
        return ph, fixed

    def say(self, text, speed=1.0):
        ph, fixed = self.phonemes(text)
        audio, sr = self.k.create(ph, voice=self.voice, speed=speed, lang="en-us", is_phonemes=True)
        assert sr == TTS_SR
        return trim(np.asarray(audio, dtype=np.float32)), ph, fixed


def trim(a, thr=0.012, pad=0.04):
    """Cut leading/trailing silence, keeping a short pad."""
    env = np.convolve(np.abs(a), np.ones(240) / 240, mode="same")
    idx = np.where(env > thr)[0]
    if not len(idx):
        return a
    i0 = max(0, idx[0] - int(pad * TTS_SR))
    i1 = min(len(a), idx[-1] + int(pad * TTS_SR))
    out = a[i0:i1].copy()
    f = int(0.01 * TTS_SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-f:] *= np.linspace(1, 0, f)
    return out


def clean(text):
    return text.replace("[pause]", "").strip()


def plan(tl):
    """Per cue: subtitle window and the latest moment the line may end."""
    cues = [(sc, c) for sc in tl["scenes"] for c in sc["cues"]]
    out = []
    for i, (sc, c) in enumerate(cues):
        if i + 1 < len(cues):
            nxt = cues[i + 1][1]["start"]
            hard = min(nxt - 0.12, sc["end"] - 0.25)
        else:
            hard = tl["title_start"] - 0.25
        soft = min(hard, c["end"] + 0.3)
        out.append({"id": c["id"], "text": clean(c["text"]), "start": c["start"], "end": c["end"],
                    "soft": soft, "hard": hard})
    return out


def synth(voice, cues, min_speed=0.85, max_speed=1.32, fill=0.92):
    """Pace each line to fill most of its subtitle window, so speech starts and ends with the subtitle."""
    for cu in cues:
        window = cu["end"] - cu["start"]
        room_hard = cu["hard"] - cu["start"]
        a, ph, fixed = voice.say(cu["text"], 1.0)
        d1 = len(a) / TTS_SR
        speed = min(max_speed, max(min_speed, d1 / (fill * window)))
        for _ in range(3):
            if abs(speed - 1.0) > 1e-3:
                a, ph, fixed = voice.say(cu["text"], speed)
            d = len(a) / TTS_SR
            # Kokoro's speed is not exactly proportional to length; correct and retry
            if d > room_hard and speed < max_speed:
                speed = min(max_speed, speed * d / room_hard * 1.02)
            elif d < 0.8 * window and speed > min_speed:
                speed = max(min_speed, speed * d / (fill * window))
            else:
                break
        cu.update({"audio": a, "phonemes": ph, "fixed": fixed, "speed": round(speed, 3),
                   "dur": round(len(a) / TTS_SR, 3), "dur_at_1": round(d1, 3)})
        cu["ends"] = round(cu["start"] + cu["dur"], 3)
        cu["fits"] = cu["ends"] <= cu["hard"] + 1e-6
        print("%-5s speed %.2f  %.2fs in %.2fs window (+%.2fs gap)  %s" % (
            cu["id"], speed, cu["dur"], cu["end"] - cu["start"], cu["hard"] - cu["end"], "ok" if cu["fits"] else "OVERRUN"),
            flush=True)
    return cues


def voice_track(cues, total):
    n = int(total * SR)
    v = np.zeros(n)
    hp = butter(2, 80, "highpass", fs=SR, output="sos")
    for cu in cues:
        a = resample_poly(cu["audio"].astype(np.float64), SR, TTS_SR)
        a = sosfilt(hp, a)
        rms = np.sqrt(np.mean(a[np.abs(a) > 0.01] ** 2)) if np.any(np.abs(a) > 0.01) else 1.0
        a *= 0.16 / rms                         # same speech level for every line
        i0 = int(round(cu["start"] * SR))
        i1 = min(n, i0 + len(a))
        v[i0:i1] += a[: i1 - i0]
    return v


def duck_gain(v, depth_db=-11.0, attack=0.08, release=0.45):
    """Gain for the music bed: down by depth_db while the voice is active."""
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, mode="same"))
    act = (env > 0.01).astype(float)
    g = np.empty_like(act)
    a_c = np.exp(-1 / (attack * SR))
    r_c = np.exp(-1 / (release * SR))
    s = 0.0
    # one-pole smoothing, faster going down than coming back up
    for i in range(0, len(act), 64):
        tgt = act[i]
        c = a_c if tgt > s else r_c
        s = tgt + (s - tgt) * c ** 64
        g[i:i + 64] = s
    return 10 ** (depth_db * g / 20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("brand")
    ap.add_argument("video_in")
    ap.add_argument("video_out")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--report")
    ap.add_argument("--only")
    ap.add_argument("--stem", help="also write the voice-only track (WAV) here")
    args = ap.parse_args()

    tl = json.load(open(args.timeline))
    cues = plan(tl)
    voice = Voice(args.voice)
    if args.only:
        keep = set(args.only.split(","))
        cues = synth(voice, [c for c in cues if c["id"] in keep])
        import soundfile as sf
        for c in cues:
            sf.write(os.path.join(os.path.dirname(os.path.abspath(args.video_out)), "cue_%s.wav" % c["id"]), c["audio"], TTS_SR)
        return
    cues = synth(voice, cues)

    total = tl["total"]
    scene_starts = [sc["start"] for sc in tl["scenes"]]
    mcs_start = tl["scenes"][-1]["cues"][0]["start"]
    bed = V.soundtrack(total, mcs_start, tl["boom"], tl["title_start"], scene_starts, args.brand)
    v = voice_track(cues, total)
    if args.stem:
        import soundfile as sf
        sf.write(args.stem, v.astype(np.float32), SR)
    g = duck_gain(v)
    mix = bed * g[:, None] * 1.15 + v[:, None]
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak
    tmp = args.video_out + ".wav"
    V.write_wav(tmp, mix)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", args.video_in, "-i", tmp,
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-map_metadata", "-1", "-metadata", "title=", "-shortest", "-movflags", "+faststart",
                    args.video_out], check=True)
    os.remove(tmp)
    if args.report:
        rep = [{k: v for k, v in c.items() if k != "audio"} for c in cues]
        json.dump({"voice": args.voice, "cues": rep}, open(args.report, "w"), indent=1, ensure_ascii=False)
    bad = [c["id"] for c in cues if not c["fits"]]
    print(args.video_out, "overruns:", bad or "none")


if __name__ == "__main__":
    main()

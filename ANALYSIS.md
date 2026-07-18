# MIDI Sequencer — Project Analysis & Nostalgia Tour

Handcoded ~2017–2019 personal generative MIDI performance environment.  
Analyses written July 2026 after revisiting the codebase.

---

## Part 1 — Project analysis

### What it is

A **generative live MIDI performance environment**: Tkinter front panel, text-sequence DSL, up to 8 parallel channels, Akai/Novation as a second UI, and Volca/Monologue-oriented CC “wobblers.” Roughly **~5k LOC** in `source/`, plus hundreds of `.state` / `.memory` files that read like a practice journal from ~2018.

No README or `requirements.txt` existed originally — intent is inferred from code and session artifacts (~292 `.state` files, 7 `.memory` files).

### Project structure

```
midi-sequencer-master/
├── source/          # Application code (main package)
├── state/           # Saved UI/session snapshots (*.state)
├── memory/          # Saved melody sequences (*.memory)
├── other/           # Logs, scale lists, wobbler dumps, MIDI files, TODO
├── read.py          # Vendored/copied python-rtmidi util (open ports)
├── release.py       # Vendored python-rtmidi package metadata (not app code)
└── music21_test.py  # Tiny music21 experiment (unused by app)
```

| File | Role |
|------|------|
| `source/run.py` | Entry: open MIDI out (Bespeco USB), launch `Sequencer` on a thread |
| `source/sequencer.py` | God-object UI + playback engine (~1170 LOC) |
| `source/context.py` | Shared runtime state (BPM, sequences, scales, channels, paths) |
| `source/parser_my.py` | Text DSL → MIDI/`NoteObject` sequences |
| `source/midi_input_listener.py` | Poll Akai Midimix / APC Mini / Launchkey |
| `source/wobbler.py` | LFO-style CC automation UI + loops |
| `source/scales.py` + `scale_names.py` | Built-in scales + huge binary→name dictionary |
| `source/b__i__n__a__r__y.py` | Pitch-class set ↔ integer ↔ binary ↔ scale name |
| `source/note_*.py` | Note model, durations, scheduling, containers, decay |
| `source/akai_*.py`, `launchkey_*.py`, `novation_callbacks.py` | Hardware message maps & callbacks |
| `source/cc.py` | Volca Keys/FM/Sample/Kick + Monologue CC numbers |
| `source/_____G_e__n_e__r_a__t_o__r_________.py` | Procedural sequence generator (`G...G` DSL) |
| `source/memory.py` | Listbox memory bank with save/load |
| `source/delay.py` | Recursive echoing delay via threads |
| `source/evolver.py` | Stub for sequence mutation (mostly empty `pass`) |
| `source/midi_clock.py` | Stub: send MIDI clock byte `248` |
| `other/TODO` | Personal backlog (Slovak/English) |

### Architecture overview

```
run.py
  └─ rtmidi.MidiOut → Sequencer (tk.Frame / Tk root)
         ├─ Context (shared state + Parser + Scales)
         ├─ MIDIInputListener (daemon poll thread)
         │     ├─ Midimix / APC / Launchkey callbacks
         │     └─ mutate Context / Sequencer UI
         ├─ Playback thread: _play_sequence()
         │     ├─ play_midi_notes() × up to 8 channels
         │     ├─ play_sample_notes()
         │     └─ sleep(eighth note @ BPM)
         ├─ NoteObject / NoteContainer threads (note-on/off)
         ├─ Wobbler threads (CC LFOs)
         └─ Delay threads (echo)
```

**MIDI I/O**

- **Out:** one shared `MidiOut` (prefer “USB MIDI Interface” / Bespeco), used for notes, CC, pitch bend, all-notes-off.
- **In:** polled every 1 ms for controllers whose names match hardcoded strings (`MIDI Mix`, `APC MINI`, Launchkey ports).

**Sequencing**

- Text entry boxes define parallel lanes (notes, scheduling, polyphony, skip patterns, root/scale/octave/BPM sequences, MIDI channels).
- `Parser` expands DSL into `NoteObject`s; playback indexes them with wrap-around counters.
- Timing is **sleep-based** at eighth-note resolution (`NoteLengthsOld`), not a sample-accurate clock.

**UI**

- Tkinter, large fixed window (`1850x1000`), many labeled entry rows + sliders + memory listboxes + wobbler frames + sample mute frame.
- Controllers act as a second UI: RecArm toggles play/stop, knobs map to BPM/velocity, bank buttons change “modes,” APC grid colors via MIDI out.

**Hardware personality**

- MIDI channel constants target Volcas + Roland D-05 + Monologue — this is a **studio performance tool**, not a generic DAW plugin.

### Notable technical choices

**Libraries**

- `python-rtmidi` for realtime MIDI
- `tkinter` for UI
- `pyparsing` (`nestedExpr`) for nested DSL bits
- stdlib: `threading`, `time.sleep`, `copy`, `random`
- Optional/experimental: `music21` (not wired in)

**Patterns**

- **Shared mutable `Context`** bag of lists/vars instead of a clean model layer
- **Callback dictionaries** for controller events (readable, hand-maintained)
- **DSL-first composition**: sequences typed as strings, not piano-roll data
- **Fire-and-forget threads** for almost everything that needs duration

**Threading / timing**

- Main loop sleeps eighth notes; notes themselves sleep for duration/attack in their own threads.
- MIDI input is busy-poll, not callback-driven.
- Delay is recursive + threaded (clever, but unbounded thread growth under load).

### Code quality

**Strengths (typical of careful handcoded hobby work)**

- Clear separation where it mattered: parser / note model / hardware maps / CC tables
- Domain depth: scales, modes, tuplets, scheduling with attack/decay/repeat/dots
- Live performance pragmatism: save/load state, memory banks, mute/solo, controller sync (“knob must get close before it takes over”)
- Honest comments about pain (“THIS TOOK FUCKING FOREVER…”, Launchkey port hack TODOs)
- Working session archive proves the tool was *used*, not abandoned mid-sketch

**Rough edges**

- **Monolith:** `sequencer.py` owns layout, I/O, playback, state, polyphony
- **Bare `except:` / broad catches** with `continue` or silent pass — survival coding for live edits mid-play
- **Naming theater:** `B__i__n__a__r__y`, `_____G_e__n_e__r_a__t_o__r_________`, `loggger`, `Eigtht`, `_____fun.py`
- **Hardcoded paths/device names** (`I:\Pycharm projects\MIDI\memory`, Bespeco/Akai strings)
- **Incomplete features left in tree:** `evolver.py` stubs, `midi_clock.py` stub, TODO still open
- **Thread hygiene:** status bar update thread every step; note threads per hit; no join/shutdown discipline beyond closing ports
- **Python 2/3 mix:** `super(CC, self)`, `setDaemon`, `print` style, vendored `raw_input` helpers
- **No packaging:** no README, no `requirements.txt`, imports assume repo root on `PYTHONPATH`

### Interesting / creative bits

1. **Text DSL with generators & groups** — Digits/scale degrees, pauses (`,` `.` `-`), memory refs (`&`), groups (`g...g`), procedural blocks (`Gsin;len=16;...G`) that map LFO values onto a note alphabet.
2. **Binary pitch-class theory as scales** — Any of 4096 12-bit masks can name a scale via `scale_names.py` (hundreds of Raga / ethno names). Scales can be entered by name *or* binary/integer.
3. **Relative polyphony in scale space** — Absolute semitone poly + scale-degree-relative poly with probability sliders — intentional “generative harmony” feel.
4. **Wobblers as musical LFOs** — Dedicated CC modulators with sin / stacked sins / tilted sin / cycloid / square / rand, targeting Volca/Monologue CCs — modulation as first-class UI.
5. **Note scheduling mini-language** — Strings like duration + dots + times + attack + decay function attach timing envelopes to steps (`NoteSchedulingObject`).
6. **Controller as mode machine** — Midimix bank left/right either changes UI “state” (main vs sample frame) or scale mode — hardware UX designed around how the author actually played.
7. **Session archaeology** — State files show multi-channel patches (e.g. channels 15/11/10/13) with memory sequences like `&0-560-78x4` — a private composition language.

### Approximate size

| Scope | Lines (approx.) |
|-------|-----------------|
| All `.py` in project | ~5,350 |
| `source/` app modules | ~5,000 |
| Largest file: `sequencer.py` | ~1,170 |
| Next: `midi_input_listener.py`, `parser_my.py` | ~490 each |
| Data: `state/` | ~292 session files |
| Data: `memory/` | 7 memory banks |

### Dependencies and how to run

**Runtime deps (from imports)**

- **Required:** `python-rtmidi`, `pyparsing`, Python 3.x with `tkinter`
- **Optional / unused by main path:** `music21`
- **Stdlib only otherwise**

**Hardware assumptions (from constants)**

- MIDI out interface containing `"USB MIDI Interface"` (Bespeco)
- Optionally: Akai MIDI Mix, APC Mini, Novation Launchkey
- Synths on fixed channels (Volca Keys/FM/Kick, D-05, Monologue)

```text
# from midi-sequencer-master/ (parent of source/)
pip install python-rtmidi pyparsing
python -m source.run
```

### Verdict

As pre-AI Python: **this is good.** Not “clean architecture textbook” good — **instrument-builder** good. A private composition language wired to real hardware. The value is in the DSL, the scale/binary system, and the performance loop, not in whether `Context` is elegant.

If revived, highest-leverage upgrades: a proper clock (instead of eighth-note sleeps), device/path config instead of hardcoded names, and packaging so it runs without tribal knowledge — but the musical core still holds up.

---

## Part 2 — Nostalgia tour

### Stop 1 — Power-on ritual

`run.py` is pure studio folklore: list ports, hunt for `"USB MIDI Interface"`, fall back to port 0, launch the sequencer on a thread. There’s even a commented-out second instance — past-you briefly wondered if two sequencers on one MIDI out was a good idea.

Studio map etched in constants: Keys=10, FM=11, Kick=13, D-05=14, Monologue=15. Not configurable. *Your* desk.

### Stop 2 — The private language

You didn’t draw notes. You *typed* them. Digits for scale degrees, commas/dots/dashes for silence, `&` for memory banks, `g…g` for groups, `G…G` for procedural generators. Separators include `|` between channels and the gloriously unhinged `§` for container timing.

`joker and thief.state` still looks like spellcasting:

```
&034367 | (&t7b7+§64t,==.=== &t6a6+§64t,...)x2 ...
```

That’s not a bug. That’s composition as CLI.

### Stop 3 — Binary mysticism

`B__i__n__a__r__y` (yes, with the dramatic underscores) treats every 12-bit mask as a scale. `scale_names.py` is a museum of pitch-class sets: Raga Lavangi, Hirajoshi, Iwato, Messiaen truncated mode 6…

You could type `lydian`, a raga name, or a binary string and get the same pitch-class set. In `very_nice_melody_again_v2` you were already doing long-form scale choreography:

```
lydianx256 balinesex64 lydianx256 balinesex128
```

Hundreds of bars of Lydian → Balinese → Lydian. Patient music.

### Stop 4 — The forever comment

Relative polyphony — “play a harmony that stays *in* the scale, not a fixed semitone offset” — earned the project’s emotional climax in `sequencer.py`:

```python
# THIS TOOK FUCKING FOREVER TO FIGURE OUT
added = (int(scales.get_note_by_index_wrap(note_entry + poly, scale))
         - int(scales.get_note_by_index_wrap(note_entry, scale)))
note.play_transposed(added)
```

That comment is a monument. Interval arithmetic in wrapped scale space, mid-gig, with probability sliders. Of course it took forever.

Nearby, softer wisdom: bare `except` blocks because *you edit the entry box while it’s playing* and the show must go on.

### Stop 5 — Wobblers

Dark-blue Tk frames. Vertical sliders. Sin, stacked sins, tilted sins, cycloid, rand. Aimed at Volca Keys/FM/Sample/Kick and Monologue CCs. Someone once dumped wobbler values as ASCII bar graphs (`"#"*int(value/3)`) and then commented it out like a secret.

Modulation wasn’t an afterthought — it had its own UI species.

### Stop 6 — Controllers as co-pilots

Akai Midimix, APC Mini, Launchkey — all polled at 1ms. Soft-takeover so a knob only bites when it gets within 5 of the UI value. Bank buttons flip “main vs sample” modes. And a permanent scar in `midi_input_listener.py`:

> TODO: hack to make Launchkey work — both ports somehow map the same…

Every MIDI musician has that one device that never quite behaved.

### Stop 7 — The session attic

~300 `.state` files. Timestamps from **2018-09** through **2019-01**, plus named vibes:

| Patch name | Mood |
|---|---|
| `very_nice_melody_again_v2` | You liked it. Twice. |
| `hard bass` | BPM ~178, `super_locrian`, octave −1 everywhere |
| `joker and thief` | Dense memory/group sorcery |
| `F O U R T H S` | Aesthetic capitalization as genre |
| `metal harp` / `fast harp aeolian` | Harp era |
| `tectonic` / `octatonic` / `8044` | Theory brain on |

Memory banks dated April 2018 (`2018-04-08.memory` … `04-20`) — a week of melodic archaeology.

Also: a state literally named `0,,0,,0,,0,,0,,0,0,0,0,0,.state`. Past-you saved a rhythm of rests. Relatable.

### Stop 8 — The unfinished dream: Evolver

`evolver.py` is the most nostalgic file in the repo. Probabilities for grow/shrink/replace notes and pauses… then mostly `pass`. You designed genetic mutation of sequences, wired the knobs, and never finished the organism. The TODO list still wants it — next to MIDI clock and “logical functions (and/or/xor…) for rhythm.” Ambition parked mid-flight.

### Stop 9 — Personality leftovers

- `loggger.py` — three g’s. Fine.
- `pitch_bend.py`: `# print("Reconsutzcted: ...")` — typo fossil, never cleaned.
- German `h` for B in `note_dict` (`"h": b2`) — Central European keyboard brain.
- Scale aliases commented out: Byzantine = double harmonic, Geez = Dorian…
- `_____G_e__n_e__r_a__t_o__r_________` and `_____fun.py` — filenames as performance art.
- Migrating 7 → 8 sequences and *padding old state files on load* so yesterday’s patches still opened. That’s love.

### Closing the door

This project doesn’t feel like “early Python.” It feels like a **desk instrument with a dialect** — Volcas, D-05, Monologue, Midimix, and a text language only you spoke fluently. The unfinished Evolver and the `THIS TOOK FUCKING FOREVER` comment are the same person: patient enough to solve scale-relative harmony, restless enough to leave genetic sequencing as `pass`.

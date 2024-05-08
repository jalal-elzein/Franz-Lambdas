def get_midi_program_mapping():
    return [
        {"class": "Piano", "instrument": "Acoustic Grand Piano"},
        {"class": "Piano", "instrument": "Bright Acoustic Piano"},
        {"class": "Piano", "instrument": "Electric Grand Piano"},
        {"class": "Piano", "instrument": "Honky-tonk Piano"},
        {"class": "Piano", "instrument": "Rhodes Piano"},
        {"class": "Piano", "instrument": "Chorused Piano"},
        {"class": "Piano", "instrument": "Harpsichord"},
        {"class": "Piano", "instrument": "Clavinet"},
        {"class": "Chromatic", "instrument": "Percussion Celesta"},
        {"class": "Chromatic", "instrument": "Percussion Glockenspiel"},
        {"class": "Chromatic", "instrument": "Percussion Music box"},
        {"class": "Chromatic", "instrument": "Percussion Vibraphone"},
        {"class": "Chromatic", "instrument": "Percussion Marimba"},
        {"class": "Chromatic", "instrument": "Percussion Xylophone"},
        {"class": "Chromatic", "instrument": "Percussion Tubular Bells"},
        {"class": "Chromatic", "instrument": "Percussion Dulcimer"},
        {"class": "Organ", "instrument": "Hammond Organ"},
        {"class": "Organ", "instrument": "Percussive Organ"},
        {"class": "Organ", "instrument": "Rock Organ"},
        {"class": "Organ", "instrument": "Church Organ"},
        {"class": "Organ", "instrument": "Reed Organ"},
        {"class": "Organ", "instrument": "Accordion"},
        {"class": "Organ", "instrument": "Harmonica"},
        {"class": "Organ", "instrument": "Tango Accordion"},
        {"class": "Guitar", "instrument": "Acoustic Guitar (nylon)"},
        {"class": "Guitar", "instrument": "Acoustic Guitar (steel)"},
        {"class": "Guitar", "instrument": "Electric Guitar (jazz)"},
        {"class": "Guitar", "instrument": "Electric Guitar (clean)"},
        {"class": "Guitar", "instrument": "Electric Guitar (muted)"},
        {"class": "Guitar", "instrument": "Overdriven Guitar"},
        {"class": "Guitar", "instrument": "Distortion Guitar"},
        {"class": "Guitar", "instrument": "Guitar Harmonics"},
        {"class": "Bass", "instrument": "Acoustic Bass"},
        {"class": "Bass", "instrument": "Electric Bass (finger)"},
        {"class": "Bass", "instrument": "Electric Bass (pick)"},
        {"class": "Bass", "instrument": "Fretless Bass"},
        {"class": "Bass", "instrument": "Slap Bass 1"},
        {"class": "Bass", "instrument": "Slap Bass 2"},
        {"class": "Bass", "instrument": "Synth Bass 1"},
        {"class": "Bass", "instrument": "Synth Bass 2"},
        {"class": "Strings", "instrument": "Violin"},
        {"class": "Strings", "instrument": "Viola"},
        {"class": "Strings", "instrument": "Cello"},
        {"class": "Strings", "instrument": "Contrabass"},
        {"class": "Strings", "instrument": "Tremolo Strings"},
        {"class": "Strings", "instrument": "Pizzicato Strings"},
        {"class": "Strings", "instrument": "Orchestral Harp"},
        {"class": "Strings", "instrument": "Timpani"},
        {"class": "Ensemble", "instrument": "String Ensemble 1"},
        {"class": "Ensemble", "instrument": "String Ensemble 2"},
        {"class": "Ensemble", "instrument": "Synth Strings 1"},
        {"class": "Ensemble", "instrument": "Synth Strings 2"},
        {"class": "Ensemble", "instrument": "Choir Aahs"},
        {"class": "Ensemble", "instrument": "Voice Oohs"},
        {"class": "Ensemble", "instrument": "Synth Voice"},
        {"class": "Ensemble", "instrument": "Orchestra Hit"},
        {"class": "Brass", "instrument": "Trumpet"},
        {"class": "Brass", "instrument": "Trombone"},
        {"class": "Brass", "instrument": "Tuba"},
        {"class": "Brass", "instrument": "Muted Trumpet"},
        {"class": "Brass", "instrument": "French Horn"},
        {"class": "Brass", "instrument": "Brass Section"},
        {"class": "Brass", "instrument": "Synth Brass 1"},
        {"class": "Brass", "instrument": "Synth Brass 2"},
        {"class": "Reed", "instrument": "Soprano Sax"},
        {"class": "Reed", "instrument": "Alto Sax"},
        {"class": "Reed", "instrument": "Tenor Sax"},
        {"class": "Reed", "instrument": "Baritone Sax"},
        {"class": "Reed", "instrument": "Oboe"},
        {"class": "Reed", "instrument": "English Horn"},
        {"class": "Reed", "instrument": "Bassoon"},
        {"class": "Reed", "instrument": "Clarinet"},
        {"class": "Pipe", "instrument": "Piccolo"},
        {"class": "Pipe", "instrument": "Flute"},
        {"class": "Pipe", "instrument": "Recorder"},
        {"class": "Pipe", "instrument": "Pan Flute"},
        {"class": "Pipe", "instrument": "Bottle Blow"},
        {"class": "Pipe", "instrument": "Shakuhachi"},
        {"class": "Pipe", "instrument": "Whistle"},
        {"class": "Pipe", "instrument": "Ocarina"},
        {"class": "Synth", "instrument": "Lead Lead 1 (square)"},
        {"class": "Synth", "instrument": "Lead Lead 2 (sawtooth)"},
        {"class": "Synth", "instrument": "Lead Lead 3 (calliope lead)"},
        {"class": "Synth", "instrument": "Lead Lead 4 (chiffer lead)"},
        {"class": "Synth", "instrument": "Lead Lead 5 (charang)"},
        {"class": "Synth", "instrument": "Lead Lead 6 (voice)"},
        {"class": "Synth", "instrument": "Lead Lead 7 (fifths)"},
        {"class": "Synth", "instrument": "Lead Lead 8 (brass + lead)"},
        {"class": "Synth", "instrument": "Pad Pad 1 (new age)"},
        {"class": "Synth", "instrument": "Pad Pad 2 (warm)"},
        {"class": "Synth", "instrument": "Pad Pad 3 (polysynth)"},
        {"class": "Synth", "instrument": "Pad Pad 4 (choir)"},
        {"class": "Synth", "instrument": "Pad Pad 5 (bowed)"},
        {"class": "Synth", "instrument": "Pad Pad 6 (metallic)"},
        {"class": "Synth", "instrument": "Pad Pad 7 (halo)"},
        {"class": "Synth", "instrument": "Pad Pad 8 (sweep)"},
        {"class": "Synth", "instrument": "Effects FX 1 (rain)"},
        {"class": "Synth", "instrument": "Effects FX 2 (soundtrack)"},
        {"class": "Synth", "instrument": "Effects FX 3 (crystal)"},
        {"class": "Synth", "instrument": "Effects FX 4 (atmosphere)"},
        {"class": "Synth", "instrument": "Effects FX 5 (brightness)"},
        {"class": "Synth", "instrument": "Effects FX 6 (goblins)"},
        {"class": "Synth", "instrument": "Effects FX 7 (echoes)"},
        {"class": "Synth", "instrument": "Effects FX 8 (sci-fi)"},
        {"class": "Ethnic", "instrument": "Sitar"},
        {"class": "Ethnic", "instrument": "Banjo"},
        {"class": "Ethnic", "instrument": "Shamisen"},
        {"class": "Ethnic", "instrument": "Koto"},
        {"class": "Ethnic", "instrument": "Kalimba"},
        {"class": "Ethnic", "instrument": "Bagpipe"},
        {"class": "Ethnic", "instrument": "Fiddle"},
        {"class": "Ethnic", "instrument": "Shana"},
        {"class": "Percussive", "instrument": "Tinkle Bell"},
        {"class": "Percussive", "instrument": "Agogo"},
        {"class": "Percussive", "instrument": "Steel Drums"},
        {"class": "Percussive", "instrument": "Woodblock"},
        {"class": "Percussive", "instrument": "Taiko Drum"},
        {"class": "Percussive", "instrument": "Melodic Tom"},
        {"class": "Percussive", "instrument": "Synth Drum"},
        {"class": "Percussive", "instrument": "Reverse Cymbal"},
        {"class": "Sound", "instrument": "Effects Guitar Fret Noise"},
        {"class": "Sound", "instrument": "Effects Breath Noise"},
        {"class": "Sound", "instrument": "Effects Seashore"},
        {"class": "Sound", "instrument": "Effects Bird Tweet"},
        {"class": "Sound", "instrument": "Effects Telephone Ring"},
        {"class": "Sound", "instrument": "Effects Helicopter"},
        {"class": "Sound", "instrument": "Effects Applause"},
        {"class": "Sound", "instrument": "Effects Gunshot"},
    ]
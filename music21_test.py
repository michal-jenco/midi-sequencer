import music21 as m

littleMelody = m.converter.parse("tinynotation: 3/4 c4 d8 f g16 a g f#")
# littleMelody.show("midi")



s1 = m.stream.Stream()
s1.append(m.meter.TimeSignature('9/8'))

myTup = m.ElementWrapper(m.duration.Tuplet(numberNotesActual=5, numberNotesNormal=4))

s1.append(myTup)

s1.show()


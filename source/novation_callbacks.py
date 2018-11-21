from source.cc import CCFM
from source.functions import range_to_range
from source.button_numbers import ButtonNumbers
from source.constants import Ranges, MIDIChannels
from source.pitch_bend import PitchBend, PitchBendRanges
from source.note_object import NoteObject
from source.note_types import NoteTypes


class NovationCallbacks(object):
    def __init__(self, sequencer, context):
        self.sequencer = sequencer
        self.context = context
        self.pitchbend = PitchBend("0", None, self.context.midi)

    def __call__(self, msg, *args, **kwargs):
        one, two, three = msg

        if NovationCallbacks._msg_is_key(msg):
            self.key(msg)
        else:
            try:
                controller_name = ButtonNumbers.Novation.get_by_number(two).lower()
                print("Novation Launchkey: {} pressed.".format(controller_name))

                if "button" in controller_name and three:
                    self.button_wrapper(msg, controller_name)
                else:
                    getattr(self, controller_name)(three)

            except AttributeError:
                ...

    @staticmethod
    def _msg_is_key(msg):
        """Is the message coming from the keyboard?"""
        return msg[0] in (130, 146, 128, 144, 131, 147)

    @staticmethod
    def _get_button_from_message(msg):
        """Get the name of the button from the message."""
        if msg[0] in ButtonNumbers.Novation._CODES_BASIC:
            return ButtonNumbers.Novation.get_by_number(msg[1])
        else:
            return None

    def key(self, msg):
        """What happens when a key on the keyboard is pressed."""
        _, pitch, _original_velocity = msg

        velocity = int(range_to_range(Ranges.MIDI_CC,
                                      self.context.get_novation_velocity_range(),
                                      _original_velocity)) if _original_velocity != 0 else 0

        if self.context.novation_record_on:
            """We are going to record the keyboard notes."""
            if not _original_velocity:
                return

            for i in self._get_entry_memory_seq_indices():
                self.context.note_sequences[i] += [
                    NoteObject(context=self.context, pitch=pitch, channel=0x90, velocity=velocity)]
                self.context.str_sequences[i] += ["0"]
                print(self.context.note_sequences[i])

        else:
            """We're just playing keyboard notes."""
            if not _original_velocity and self.context.novation_dont_end_notes:
                return

            note = [0x90 + self.context.novation_midi_channel, msg[1], velocity]

            if self.context.novation_midi_channel == MIDIChannels.volca_fm:
                self.context.midi.send_message([0xb0 + self.context.novation_midi_channel,
                                                CCFM().velocity, velocity])

            if not velocity and self.context.novation_dont_end_notes:
                return
            else:
                self.context.midi.send_message(note)
                self.context.novation_logger.log(note)

            # print("original velocity: %s" % original_velocity)
            # print("new velocity: %s" % velocity)
            # print("sending note: %s" % note)

    def pitch(self, value):
        self.pitchbend.channel = self.context.novation_midi_channel
        self.pitchbend.integer_bend = range_to_range(
            Ranges.MIDI_CC, (PitchBendRanges.minimum, PitchBendRanges.maximum), value, int)
        self.pitchbend()

    def modulation(self, value):
        self.context.midi.send_message([0xb0 + self.context.novation_midi_channel, 1, value])

    def record(self, value):
        if value == 0:
            return
        self.context.novation_record_on = not self.context.novation_record_on

    def midi_channel_down(self, value):
        if value == 0:
            return

        self.context.novation_midi_channel -= 1
        self.sequencer.label_novation_launchkey_note_channel.config(
            text=str(self.context.novation_midi_channel))

    def midi_channel_up(self, value):
        if value == 0:
            return

        self.context.novation_midi_channel += 1
        self.sequencer.label_novation_launchkey_note_channel.config(
            text=str(self.context.novation_midi_channel))

    def button_wrapper(self, msg, controller_name):
        if self.context.novation_record_on:
            count = int(controller_name[-1])

            for i in self._get_entry_memory_seq_indices():
                if count != 9:
                    self.context.note_sequences[i] += [
                        NoteObject(context=self.context, type_=NoteTypes.NOTE_PAUSE) for _ in range(count)]
                    self.context.str_sequences[i] += ["," for _ in range(count)]
                else:
                    self.context.note_sequences[i] = []
        else:
            getattr(self, controller_name)(msg[-1])

    def _get_entry_memory_seq_indices(self):
        return [i for i, channel_list in enumerate(self.context.midi_channels)
                if [self.context.novation_midi_channel] == channel_list][:1]

    def play(self, value):
        if value:
            self.context.playback_on = not self.context.playback_on

    def button_1(self, value):
        if value:
            self.context.novation_dont_end_notes = not self.context.novation_dont_end_notes

    def button_2(self, value):
        if value:
            for i in range(128):
                self.context.midi.send_message([0x90 + self.context.novation_midi_channel, i, 0])

    def slider_1(self, value):
        self.context.novation_velocity_min = value

    def slider_2(self, value):
        self.context.novation_velocity_max = value

    def slider_3(self, value):
        ...

    def slider_4(self, value):
        ...

    def slider_5(self, value):
        ...

    def slider_6(self, value):
        ...

    def slider_7(self, value):
        ...

    def slider_8(self, value):
        ...

    def slider_9(self, value):
        ...

    def knob_1(self, value):
        ...

    def knob_2(self, value):
        ...

    def knob_3(self, value):
        ...

    def knob_4(self, value):
        ...

    def knob_5(self, value):
        ...

    def knob_6(self, value):
        ...

    def knob_7(self, value):
        ...

    def knob_8(self, value):
        ...

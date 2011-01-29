from pygame import mixer

__doc__ = """Sound effects module.

The L{Sound} class represents a sound effect. Sound objects can be created
from any supported format, or even from a sample buffer. Sound effects have
the expected controls: play, pause, stop, loop, as well as fade-in and fade-out,
volume control, and stereo panning control (if the internal mixer is initialized
for stereo support).

Sound objects are different from Music objects in that a sound is completely
loaded into memory when the object is created, but music is streamed from its
original location. Sound objects could be used for music as well, at a higher
memory cost.
"""

__all__ = ['Sound']

class Sound(object):
    """An object representing a sound effect. Pyrge's Sound object wraps the
       underlying pygame Sound and Channel objects to allow finer control of
       a game's sounds. Sounds can be programatically started, stopped, paused,
       and unpaused, and they also support fading in and out, volume control,
       and stereo panning. There is also a callback mechanism that posts a
       specific pygame Event when the sound is done playing.

       Sounds can be in any format supported by pygame and SDL, but OGG and WAV
       work best.

       (Note: For simpler, and probably faster, sound support, the pygame Sound
       object -- pygame.mixer.Sound -- can be used instead.)

       @param soundfile: A filename, file object, or sound buffer object.
    """

    def __init__(self, soundfile):
        self.__sound = mixer.Sound(soundfile)
        self.__channel = None
        self.__volume = 1.0
        self.__panning = 0.0
        self.__endevent = None

    def play(self, loops=0, maxtime=0, fadein=0):
        """Starts playback of this Sound.

           @param loops: The number of times this Sound will be repeated, not
           including the first playback. Therefore, the default of 0 will play
           the sound once, while higher numbers will play the sound once, then
           repeat it the given number of times. Using -1 as the argument will
           cause the playback to repeat indefinitely.
           @param maxtime: The maximum length of time (in milliseconds) to play
           this Sound. The default of 0 plays the Sound in its entirety.
           @param fadein: The amount of time to fade in the Sound. The playback
           will start at 0 volume, and ramp up to full volume over this many
           milliseconds.
        """
        self.__channel = mixer.find_channel()
        if self.__channel is not None:
            self.__channel.play(self.__sound, loops, maxtime, fadein)
            if self.panning:
                self.__channel.set_volume(*self.__doPan())
            if self.endevent is not None:
                self.__channel.set_endevent(self.endevent)

    def stop(self):
        """Stops playback of this Sound completely."""
        self.__channel.stop()

    def pause(self):
        """Pauses playback of this Sound. The Sound can be restarted at the same
           position by calling unpause()."""
        self.__channel.pause()

    def unpause(self):
        """Unpauses this Sound. This resumes playing the Sound at the position
           where it was paused."""
        self.__channel.unpause()

    def fadeout(self, time):
        """Fade out this Sound. This lowers the volume to 0 over a period of time,
           then stops.

           @param time: The amount of time (in milliseconds) to fade out this Sound.
        """
        self.__channel.fadeout(time)

    def __get_volume(self):
        return self.__volume

    def __set_volume(self, vol):
        self.__volume = vol
        self.__sound.set_volume(vol)

    volume = property(__get_volume, __set_volume, \
                      doc="The volume level of this sound, from 0.0 to 1.0.")

    def __get_panning(self):
        return self.__panning

    def __set_panning(self, pan):
        self.__panning = pan
        if self.__channel is not None:
            self.__channel.set_volume(*self.__doPan())

    panning = property(__get_panning, __set_panning, \
                       doc="The panning level of this sound, from full left (-1.0) to full right (1.0)")

    # TODO: maybe make a better panning function
    def __doPan(self, pan):
        pl = 1.0 if pan <= 0.0 else 1.0 - pan
        pr = 1.0 if pan >= 0.0 else 1.0 + pan
        return (pl, pr)

    def __get_endevent(self):
        return self.__endevent

    def __set_endevent(self, evttype):
        self.__endevent = evttype
        if self.__channel is not None:
            if evttype is not None:
                self.__channel.set_endevent(evttype)
            else:
                self.__channel.set_endevent()

    endevent = property(__get_endevent, __set_endevent, \
                        doc = "The type of event that will be posted when this Sound has finished playing.""")

    @property
    def length(self):
        """The length of this Sound, in seconds."""
        return self.__sound.get_length()

    @property
    def sampleBuffer(self):
        """A buffer object containing the samples for this sound."""
        return self.__sound.get_buffer()

if __name__ == '__main__':
    pass

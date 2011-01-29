import pygame

__doc__ = """Module for streamed sound or music.

The L{Music} class can be used to play any sound, but it is particularly
useful for the playback of large music files, since it is optimized for
low memory usage. This object builds on the functionality provided by Pygame,
mainly by supporting more than a single music track. Only one track can be
played at any time, but multiple Music objects can be created.

The Music object supports a variety of formats, including both sample-based
(MP3, OGG) and pattern-based (MOD, XM) formats. Also, there are methods for
playback control, including pause, stop, rewind, looping, and volume control.
"""

__all__ = ['Music']

class Music(object):
    """A background music object. The file passed to the constructor will
       not be loaded into memory yet, and playback will not be started. This
       allows for multiple music streams, though, due to a limitation in the
       underlying system, only one Music object can be playing at a time.

       The music file can be in any format supported by Pygame and SDL,
       including MP3, OGG, and MOD.

       @cvar current: The filename or file object of the currently-playing Music.

       @param musicfile: The filename or file object of the music.
    """
    current = None
    
    def __init__(self, musicfile):
        self.filename = musicfile
        self.__pausetime = 0.0
        self.__volume = None
        self.__endevent = None

    def play(self, times=0, startpos=0.0, volume=None, endevent=None):
        """Starts playback of this object's music file.

           @param times: The number of times this music will be played.
           0 will play music once, -1 will loop indefinitely, and any
           other number will cause the music to loop that many times.
           @param startpos: The starting position of music playback.
           This is in seconds for sample-based music formats like MP3,
           or in patterns for pattern-based formats such as MOD.
           @param volume: The volume level of the music, from 0.0 to 1.0.
           @param endevent: The type of Pygame event that will be posted
           when playback is finished. (If looping, the event will be posted
           after each loop.)
        """
        if Music.current != self.filename:
            pygame.mixer.music.load(self.filename)
            Music.current = self.filename
        self.__pausetime = startpos

        # restore volume and end event state
        if volume is not None:
            self.volume = volume
        elif self.volume is not None:
            pygame.mixer.music.set_volume(self.volume)

        if endevent is not None:
            self.endevent = endevent
        elif self.endevent is not None:
            pygame.mixer.music.set_endevent(self.endevent)
            
        pygame.mixer.music.play(times, startpos)

    def loop(self):
        """Play this music repeatedly. This is the same as calling play()
           with times = -1, but the intent is clearer."""
        self.play(-1)

    
    def pause(self):
        """Pause the music playback. Calling unpause() will restart playback
           from the position where it was paused."""
        self.__pausetime = pygame.mixer.music.get_pos() / 1000.
        pygame.mixer.music.pause()

    def unpause(self):
        """Resumes playback a paused music stream. This method is aware of
           multiple music streams, but it can't keep track of loops."""
        if Music.current == self.filename:
            pygame.mixer.music.unpause()
        else:
            self.play(0, self.__pausetime)

    def stop(self):
        """Completely stops playback of this music."""
        self.__pausetime = 0.0
        pygame.mixer.music.stop()

    def rewind(self):
        """Resets playback of this music to the beginning."""
        self.__pausetime = 0.0
        if Music.current == self.filename:
            pygame.mixer.music.rewind()

    def __get_volume(self):
        return self.__volume

    def __set_volume(self, vol):
        self.__volume = vol
        if Music.current == self.filename:
            pygame.mixer.music.set_volume(self.__volume)

    volume = property(__get_volume, __set_volume, \
                      doc="The volume level of this object's music")

    def __get_endevent(self):
        return self.__endevent

    def __set_endevent(self, evttype):
        self.__endevent = evttype
        if Music.current == self.filename:
            if evttype is not None:
                pygame.mixer.music.set_endevent(evttype)
            else:
                pygame.mixer.music.set_endevent()

    endevent = property(__get_endevent, __set_endevent, \
                        doc="The type of pygame Event that will be posted after playback")

if __name__ == '__main__':
    pass

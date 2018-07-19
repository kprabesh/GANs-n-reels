# Author: Caleb Graves
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random

VECTOR_DIR = '../../../Data/Vectors/'


def load_vector(fname):
    fname = VECTOR_DIR + fname
    array = np.load(fname)
    return array


number_notes = {
    60: 'C',
    62: 'D',
    64: 'E',
    65: 'F',
    67: 'G',
    69: 'A',
    71: 'B',
    72: 'c',
    74: 'd',
    76: 'e',
    77: 'f',
    79: 'g',
    81: 'a',
    83: 'b',
    0: 'z'
}


class Decoder:
    """
    A class which helps control the variables for playing the music.
    """
    def __init__(self, time='1/48', key='Cmaj'):
        self.time = time
        self.key = key

    def gen_header(self):
        header = '''X: 1\n
                    T: AI Music\n
                    R: reel\n
                    M: 4/4\n
                    L: ''' + self.time + '''\n
                    K: ''' + self.key + '''\n'''
        return header

    def set_key(self, key):
        self.key = key

    def set_time(self, time):
        self.time = time

    def play_from_dict(self, dic, time='1/8'):
        """
        Plays a song given the dictionary.
        :param dic: The tune as a dictionary
        :param time: ABC L: field; Default -> '1/8'
        :return: None. Plays the song.
        """
        self.set_key(dic['mode'])
        self.set_time(time)
        self.play(dic['abc'])

    def play_from_single_vector(self, vec, time='1/16'):
        """
        Plays a song given the vector
        :param vec: The tune as a 2D array
        :param time: ABC 'L:' field; Default -> '1/16'
        :return: None. Plays the song.
        """
        self.set_key('Cmaj')
        self.set_time(time)
        abc = decode_single_vector([vec])[0]
        self.play(abc)

    def play_from_dual_vector(self, vec, time='1/48'):
        self.set_key('Cmaj')
        self.set_time(time)
        # TODO - Reconfigure the abc generator
        self.play(abc)

    def play(self, abc):
        """
        This function takes in a song in ABC format string and plays it using music21 and pygame modules
        Note: Timidity must also be installed, as it's config file is required for the stream object.
        :param abc: Generated song in ABC format
        :return: None
        """

        abc = self.gen_header() + abc

        # convert abc format to stream object
        tune = converter.parseData(abc, format='abc')

        # add harp instrument
        for p in tune.parts:
            p.insert(0, instrument.Harp())

        # play music using pygame stream player
        player = StreamPlayer(tune)
        player.play()

        return


def convert_note_list(lst):
    """
    Converts a vectorized tune to ABC
    :param lst: The list of bars in the tune
    :return: The ABC string
    """
    out = ''
    for x in lst:
        prepend = ''
        append = ''
        hold = ''
        num = x[0]
        if not (num == 0 or (60 <= num <= 83)):
            if num > 83:
                mult = (num - 72) // 12
                append = '\'' * mult
                num = num - (12 * mult)
            else:  # x[0] < 60
                mult = ((num - 60) // 12) * -1
                append = ',' * mult
                num = num + (12 * mult)

        if num not in number_notes:
            num = num - 1
            prepend = '^'

        char = number_notes[num]

        if len(x) != 1: hold = str(len(x))
        out += prepend + char + append + hold
    return out


def pitches_to_img(songs, numcols=3, out='bars.png'):
    """
    Takes an array of vectorized tunes and return an image representation of them. 
    :param songs: The 3D array of songs.
    :param numcols: Number of columns; Default -> 3
    :param out: Name of output file; Default -> 'bars.png'
    :return: None. Saves an image to disk.
    """
    f, axs = plt.subplots(len(songs), numcols, figsize=(10, len(songs) * 2))
    plt.tight_layout()
    for num, song in enumerate(songs):
        img = song[:16]
        width = img.shape[1]
        index = num * numcols + 1
        plt.subplot(len(songs), numcols, index)
        plt.axis('off')
        plt.title("1 bar per line", fontsize=10)
        plt.matshow(img.reshape(16, width), cmap='gray', interpolation='nearest', fignum=0, aspect="auto")
        plt.subplot(len(songs), numcols, index + 1)
        plt.axis('off')
        plt.title("2 bars per line", fontsize=10)
        plt.matshow(img.reshape(8, width*2), cmap='gray', interpolation='nearest', fignum=0, aspect="auto")
        plt.subplot(len(songs), numcols, index + 2)
        plt.axis('off')
        plt.title("4 bars per line", fontsize=10)
        plt.matshow(img.reshape(4, width*4), cmap='gray', interpolation='nearest', fignum=0, aspect="auto")
    plt.savefig('../../../Data/Images/' + out)


def decode_single_vector(array):
    """
    Takes an array of tunes in vectorized form and returns a dictionary of abc strings.
    :param array: A 3 dimensional array of pieces, in the form pieces[tune][bar]
    :return: A dictionary of abc strings.
    """

    def decode_song(vec):
        dur = [vec[0][0]]
        master = []
        for x in vec:
            for y in x:
                if y == dur[0]:
                    dur.append(y)
                else:
                    master.append(dur)
                    dur = [y]
        return master

    songs = dict()
    c = 0
    for x in array:
        tune = decode_song(x)
        songs[c] = convert_note_list(tune)
        c += 1
    return songs


def decode_dual_vector(pitches, held):
    # TODO - Finish

    def decode_song(pitches, held):
        x = 0
        master = []
        lst = list()
        while x < len(pitches):
            lst.append(pitches[x])
            x += 1
            if x == len(pitches) or held[x] == 1:
                master.append(lst)
                lst = []

        return master

    songs = dict()
    for c in range(pitches.shape[0]):
        tune = decode_song(pitches[c], held[c])
        songs[c] = convert_note_list(tune)
    return songs


if __name__ == '__main__':
    drowsy_maggie = '''|:E2BE dEBE|E2BE AFDF|E2BE dEBE|1 BABc dAFD:|2 BABc dAFA||
                    |:d2fd cdec|defg afge|1 d2fd c2ec|BABc dAFA:|2 afge fdec|BABc dAFA||
                    |:dBfB dBfB|cAeA cAeA|1 dBfB dBfB|defg aece:|2 defg aecA|BABc dAFA||
                    |:dffe dfBf|ceed ceAe|1 dffe defg|a2ag aece:|2 af=ge fdec|BABc dAFD||'''

    decode = Decoder(time='1/12')

    from src.Model.Tunes_16th_V2 import tunes

    # decode.play(tunes[18])

    generated = load_vector('generated_samples.npy')
    # pitches_to_img(generated)
    generated = decode_single_vector(generated)



    decode.play('C16')

    for x in range(20):
        print('Playing tune #{}'.format(x))
        print(generated[x])
        decode.play(generated[x] + 'z12A')
        print('Next...\n')


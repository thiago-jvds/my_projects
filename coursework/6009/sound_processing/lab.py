'''
Sounds are assumed to be a dictionary as:       
            
    {
       'samples' : list - list of samples,
       'rate' : int - units of samples per second,
       'left' : list - list of samples on left speaker
       'right' : list - list of samples on right speaker              
    }
            
If it is a mono sound, 'left' and 'right' are not available. If stereo sound, then 'samples' is not available.
Some (given) helper functions are available at the end for converting .WAV files
'''

def backwards(sound):
    '''
    Assumes sound as dictionary
    Does not modify current parameter

    Parameters
    ----------
        sound : dictionary 
            Sound to be inverted as a dictionary 

    Returns
    -------
        rev_sound : dictionary
            Reverted sound
    '''
    
    # get sample list
    samples = sound['samples']

    # make a new sound object
    rev_sound = sound.copy()

    # invert sample list
    inv_samples = samples[::-1]

    # change sample list 
    rev_sound['samples'] = inv_samples

    # return new dictionary
    return rev_sound


def mix(sound1, sound2, p):
    '''
    Assumes sound1, sound2 in the dictionary form.
    Does not modify the current parameters

    Parameters
    ----------
        sound1, sound2 : dictionary
            The sounds to be mixed

        p : float
            Mixing parameter

    Returns
    -------
        mixed_sound : dictionary
            Mixed sound

    '''

    # check sampling rates
    if sound1['rate'] != sound2['rate']: return None

    # get min
    arg_min = min(len(sound1['samples']),len(sound2['samples']))

    # Init variables
    mixed_sound = {}
    mixed_sound['rate'] = sound1['rate']
    mixed_sound['samples'] = []

    # loop to build sample list
    for i in range(arg_min):
        
        # get new sample
        new_sample = sound1['samples'][i]*(p) + sound2['samples'][i]*(1-p)

        # append new sample
        mixed_sound['samples'].append(new_sample)

    return mixed_sound


def convolve(sound, kernel):
    '''
    Assumes sound in the dictionary form
    Does not modify original parameters

    Parameters
    ----------
        sound : dictionary
            Sound to be convolved

        kernel : list
            Kernel to be convolved

    Returns
    -------
        conv_sound : dictionary
            Convolved sound
    '''

    # Init variables
    n_samples = len(sound['samples'])
    n_kernel = len(kernel)
    samples = sound['samples']
    conv_sound = {}
    conv_sound['rate'] = sound['rate']
    conv_sound['samples'] = [0 for _ in range(n_samples + n_kernel -1)]

    for disp in range(n_kernel):
        
        # init samples as array of 0's
        temp_samples = [0 for _ in range(n_samples + n_kernel -1)]
        
        # assignment the operation according to the displacement disp
        temp_samples[disp:disp+n_samples-1] = [kernel[disp]*sample for sample in samples]

        # add new contribution to conv_sound
        for i, item in enumerate(conv_sound['samples']):
            conv_sound['samples'][i] = item + temp_samples[i]

    return conv_sound


def echo(sound, num_echoes, delay, scale):
    '''
    Assumes sound in dictionary form
    Does not modify the current parameters

    Parameters
    ----------
        sound : dictionary
            The original sound

        num_echoes -> int
            Number of times the 
            sound will be echoed

        delay : float
            Amount in seconds 
            by which each echo 
            will be delayed

        scale : float
            Amount by which each
            echo's sample should
            be scaled

    Returns
    -------
        echoed_sound : dictionary
            Original echoed sound
    '''

    # Init variables
    echoed_sound = {}
    echoed_sound['rate'] = sound['rate']
    
    samples = sound['samples']
    sample_delay = int(round(delay * sound['rate']))
    n = len(samples)

    # Init as num_echoes*sample_delay longer than previously
    echoed_sound['samples'] = [0 for _ in range(n + num_echoes * sample_delay)]

    # Create echoes
    # +1 to account for original sound then copies
    for ech in range(num_echoes+1):

        # Init new sample as array of 0's
        new_samples = [0 for _ in range(n + num_echoes * sample_delay)]

        # Adjust new displacement of size len(samples) starting at sample_delay*ech
        new_samples[sample_delay*ech:n+sample_delay*ech] = [sample*(scale**ech) for sample in samples]

        # Add new sample contribution
        for i, prev_samp in enumerate(echoed_sound['samples']):
            echoed_sound['samples'][i] = prev_samp + new_samples[i]
    
    return echoed_sound


def pan(sound):
    '''
    Assumes sound in dictionary form
    Does not change current parameter

    Parameters
    ----------
        sound : dictionary
            Sound to be pan-modified

    Returns
    -------
        mod_sound : dictionary
            Modified sound 
    '''

    # Init variables
    mod_sound = {}
    mod_sound['rate'] = sound['rate']
    mod_sound['left'] = []
    mod_sound['right'] = []
    N = len(sound['left'])

    # Create pan effect
    for n in range(N):
        
        # n starts at 0
        # new_left goes from 1 to 0
        # new_right goes from 0 to 1
        new_left = (N-1-n)/(N-1) * sound['left'][n]
        new_right = (n)/(N-1) * sound['right'][n]

        # Append new contribuitions to mod_sound
        mod_sound['left'].append(new_left)
        mod_sound['right'].append(new_right)

    return mod_sound

def remove_vocals(sound):
    '''
    Assumes sound in dictionary form
    Does not modify current parameter

    Parameters
    ----------
        sound : dictionary
            Sound to get vocals
            removed

    Returns
    -------
        no_voc_sound : dicionary
            Original sound without 
            vocals
    '''

    # Init variables
    no_voc_sound = {}
    no_voc_sound['rate'] = sound['rate']

    # mono
    no_voc_sound['samples'] = []
    N = len(sound['left'])

    # Create sound
    for i in range(N):

        # Compute difference
        dif = sound['left'][i] - sound['right'][i]

        # Append new difference
        no_voc_sound['samples'].append(dif)

    return no_voc_sound

def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel

#------ comment this line out--------
# outdated library
#from asyncore import write 

import io
from json import load
from turtle import back, backward
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


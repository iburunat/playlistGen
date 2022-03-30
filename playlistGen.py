#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Ibichka 2022 https://github.com/iburunat
"""
Takes a path to audio files and outputs two audio files into disk:
1. playlist of randomized 90sec song excerpts preceeded by 1sec of beep + silence.
2. medley  of 5sec excerpts per song from playlist separated by 3sec
Usage: pythonw playlistGen.py
"""
# {libs}
import os, random
import pathlib
import shlex
from tqdm import tqdm
import pandas as pd
import numpy as np
from tabulate import tabulate
from pydub import AudioSegment
from pydub.playback import play
from pydub.generators import Sine

# {code}
def playlistGen(songsPath, outputFile):
    # generate 500 ms and 3s silence
    silence500ms = AudioSegment.silent(duration=500)
    silence3s = AudioSegment.silent(duration=3000)
    # generate beep
    beep  = Sine(500).to_audio_segment(duration=500).apply_gain(-3)
    # create a list with song names
    songList = [f for f in os.listdir(songsPath) if not f.startswith('.')]
    # generate random song sequence
    RsongList = random.sample(songList, len(songList))
    # use whole path
    RsongListfp = [os.path.join(songsPath, s) for s in RsongList]
    # exportable table of randomized playlist
    D = pd.DataFrame(data=RsongList, columns=['PLAYLIST SONG ORDER [randomized]'])
    D.index = np.arange(1, len(D)+1)
    os.system("clear")
    print("""\n
    █▀█ █░░ ▄▀█ █▄█ █░░ █ █▀ ▀█▀ █▀▄▀█ █▀▀ █▀▄ █░░ █▀▀ █▄█   █▀▀ █▀▀ █▄░█ █▀▀ █▀█ ▄▀█ ▀█▀ █▀█ █▀█
    █▀▀ █▄▄ █▀█ ░█░ █▄▄ █ ▄█ ░█░ █░▀░█ ██▄ █▄▀ █▄▄ ██▄ ░█░   █▄█ ██▄ █░▀█ ██▄ █▀▄ █▀█ ░█░ █▄█ █▀▄
    \n\n""")
    print(tabulate(D, headers='keys', tablefmt='grid'))
    print("""\n\n""")
    # concatenate each clip in "clips"
    clipsPlaylist = []
    clipsMedley = []
    # for songPath in tqdm(RsongListfp, "Loading songs",leave=True):

    print("Preprocessing songs...\n")
    for songPath in RsongListfp:
        # get extension of the audio file
        extension = getFileExt(songPath)
        # load the audio clip and append it to our list
        clipW = AudioSegment.from_file(songPath, extension)

        # Playlist: prepend beep + silence to audio files + 4s fade out & concatenate
        clipPlaylist = beep + silence500ms + clipW[:90000].fade_out(4000)
        clipsPlaylist.append(clipPlaylist)

        # Medley: extract mid 5 sec and append 3 seconds & concatenate
        clipMedley =  clipW[45000:45000+5000] + silence3s
        clipsMedley.append(clipMedley)

    # concatenate each list element into a series
    PlayList_final = clipsPlaylist[0]
    Medley_final = clipsMedley[0]

    print("exporting files...\n")
    # range_loop = tqdm(range(1, len(clipsPlaylist)), "Concatenating songs")
    for i in range(1, len(clipsPlaylist)):
        # concatenate pydub.audio_segment together + keep order
        PlayList_final = PlayList_final + clipsPlaylist[i]
        Medley_final = Medley_final + clipsMedley[i]

    # export the final clip
    OP = shlex.quote(os.path.dirname(outputFile)+"/playlist_"+os.path.basename(outputFile))
    OM = shlex.quote(os.path.dirname(outputFile)+"/medley_"+os.path.basename(outputFile))

    extFinalClip = getFileExt(outputFile)
    print(f"\n+-----------------------------------+\nResulting audio files exported to: \n -> {OP} \n -> {OM}\n+-----------------------------------+\n")
    PlayList_final.export(OP, format=extFinalClip)
    Medley_final.export(OM, format=extFinalClip)
    os.system("open " + shlex.quote(os.path.dirname(outputFile)))

###### clear screen in terminal ##################################################################
def getFileExt(filename):
    """helper function to read a file's extension"""
    return os.path.splitext(filename)[1].lstrip(".")

###### PySimpleGUI user interface ##################################################################
import PySimpleGUI as sg
sg.theme('Dark') #NeutralBlue Dark #DarkAmber Light Blue 2, Dark Blue 3

layout = [[sg.Text('Playlist+Medley Generator', font='Courier 20')],
          [sg.Output(size=(100, 30),font='Courier 12')],
          [sg.Text('songs folder:', font='Courier 14',size=(18, 1)), sg.Input(), sg.FolderBrowse(size=(18, 1))],
          [sg.Text('output file name:', font='Courier 14',size=(18, 1)), sg.Input(), sg.FileSaveAs(size=(18, 1))],
          [sg.Submit('Generate', font='Courier 12',size=(23, 1)), sg.Button('Quit', font='Courier 12',size=(18, 1))]]

window = sg.Window('Generate Playlist + Medley', layout)
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        window.close()
    # Do something with the information gathered
    playlistGen(values[0],values[1])

##### parser for command-line options #############################################################
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="playlist random generator from songs in folder")
    parser.add_argument("-p", "--path", required=True, help="path to songs folder")
    parser.add_argument("-o", "--output", required=True, help="name of the output audio file (include the extension eg., .mp3)")
    args = parser.parse_args()
    playlistGen(args.path, args.output)

if __name__ == "__main__":
    main()

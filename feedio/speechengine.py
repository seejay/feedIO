"""
SpeechEngine module for feedIO. Provides the interface to communicate with speech engine
which installed in operating system and generating a speech for a given text.
The module also capable of making the text more friendly for the particular tts engine.
"""

__version__ = "0.0.5"

__license__ = """
    Copyright (C) 2011 Sri Lanka Institute of Information Technology.

    feedIO is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    feedIO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with feedIO.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Viraj Senarathna <virajsrc@gmail.com>"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Viraj Senarathna"]

import logging
import subprocess
import os

class SpeechEngine:
    def __init__(self,pitch,speed):
            # assigning the values for the speech engine.
            self.pitch = "-p" + pitch
            self.speed = "-s" + speed
            self.engine = "espeak"

    def festivalText(self,text):
        """
        function to make the text more friendly for the festival speech engine. it enhance the quality.
        """
        mList={'u\'re':'u are','ey\'re':'ey are'}
        # mList contains the words to be replaced and replace words.
        for i, j in mList.iteritems():
            text = text.replace(i, j)  # replacing each word mentioned in mList.
        return text

    def espeakText(self,text):
        """
        function to make the text more friendly for the espeak speech engine. it enhance the quality.
        """
        mList={'\n':'...','\t':' '}
        # mList contains the words to be replaced and replace words.
        for i, j in mList.iteritems():
            text = text.replace(i, j)  # replacing each word mentioned in mList.
        return text

    def textFileMaker(self,text):
        """
        function to make a text file for the provided text.
        """
        text_file = open("test.txt", "w")  # opening text file for writing.
        text_file.writelines(text)
        text_file.close()

    def say(self,text):
        """
        function to select the speech engine and speaking out the text.
        """
        if (self.engine == "espeak"):
            text=self.espeakText(text)  # get a more espeak friendly text
            call = [self.engine, self.pitch, self.speed, "%s" %  text]  # command to call the speech engine.
        elif (self.engine == "festival"):
            self.textFileMaker(self.festivalText(text))
            call= ["festival", "--tts","test.txt"]
        else :
            logging.debug("text to speech engine not found. please install espeak.")
        logging.debug(call)
        startupinfo = None
        try:
            self.proc = subprocess.Popen(call,startupinfo=startupinfo)  # calling speech engine in a subprocess.
        except OSError:
            logging.debug("Calling to speech engine from operating system failed.")

    def stop(self):
        """
        function to stop the speech engine.
        """
        if self.proc:
            try:
                self.proc.terminate()
            except WindowsError:
                pass

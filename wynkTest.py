import os
import sys
from time import sleep
from collections import OrderedDict
import unittest
from appium import webdriver
import requirements as req

class SimpleAndroidTests(unittest.TestCase):
    def setUp(self):
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '8.0'
        desired_caps['deviceName'] = 'Android Emulator'
        desired_caps['appPackage'] = 'com.bsbportal.music'
        desired_caps['appActivity'] = 'com.bsbportal.music.activities.LauncherScreenActivity'
        # The below thingy prevents the app from restoring to original state
        desired_caps['noReset']=True
        desired_caps['fullReset']=False
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    def tearDown(self):
        # end the session
        self.driver.quit()

    '''
    Test Case : Finding Songs from a playlist
    Description : Find playlist, parse songs in playlist, remove duplicates, write to file
    Working : 
        Given a playlist name from the command-line, the playlist is searched for in the "My Music" tab.
        The search is performed by the playlistName. If the playlist is not found in the first view, the page is scrolled.
        On load, all the playlist names are taken using xpath and the names of the same are populated in the names list.
        If the name is found in the first view, the found flag is set to True, so the loop doesn't execute.
        If not, the loop will scroll through the playlists to search. On every scroll, the names of the viewable playlists are taken and checked.
        If the playlist is not found, an error is raised
        Once found, the songs from the playlist are captured in the songs list and is scrolled until the end of page
        The songs array is checked for duplicates because of imperfect scrolling and duplicates are filtered.    
        The songs are written to a textfile with the playlist name as title     

    '''
    def test_find_songs(self):
        prevNames = list()
        el = self.driver.find_element_by_id(req.MY_MUSIC_BUTTON_ID)
        songs = list()
        el.click()
        sleep(4)
        found = False
        playlistName = sys.argv[1]
        fileName = sys.argv[2]
        el = self.driver.find_elements_by_xpath(req.XPATH_FOR_PLAYLIST_NAME_FIELD)
        names = [x.text for x in el]
        if(playlistName in names):
            found = True

        while(not found):
            linLayoutIndex0 = self.driver.find_elements_by_xpath(req.XPATH_FOR_LINEAR_LAYOUT_INDEX_0)
            linLayoutIndex0X, linLayoutIndex0Y = linLayoutIndex0[0].location['x'], linLayoutIndex0[0].location['y']
            linLayoutIndex8 = self.driver.find_elements_by_xpath(req.XPATH_FOR_LINEAR_LAYOUT_INDEX_8)
            linLayoutIndex8X, linLayoutIndex8Y = linLayoutIndex8[0].location['x'], linLayoutIndex8[0].location['y']
            self.driver.swipe(linLayoutIndex8X, linLayoutIndex8Y, linLayoutIndex0X, linLayoutIndex0Y, 800)
            el = self.driver.find_elements_by_xpath(req.XPATH_FOR_PLAYLIST_NAME_FIELD)
            names = [x.text for x in el]
            if(prevNames == names):
                raise ValueError("Playlist Not Found")
            prevNames = names
            if(playlistName in names):
                found = True
        uiAutomatorPath = 'text("'+playlistName+'")'
        el = self.driver.find_elements_by_android_uiautomator(uiAutomatorPath)
        el[0].click()
        sleep(3)        
        el = self.driver.find_elements_by_xpath(req.XPATH_FOR_SONG_TITLE)
        for element in el:
            songs.append(element.text)
        songsOnPreviousScreen = songs
        linLayoutIndex1 = self.driver.find_elements_by_xpath(req.XPATH_FOR_LINEAR_LAYOUT_INDEX_1)
        linLayoutIndex5 = self.driver.find_elements_by_xpath(req.XPATH_FOR_LINEAR_LAYOUT_INDEX_5)
        linLayoutIndex1X, linLayoutIndex1Y = linLayoutIndex1[0].location['x'], linLayoutIndex1[0].location['y'] # Dictoinary with keys 'x' and 'y'
        linLayoutIndex5X, linLayoutIndex5Y = linLayoutIndex5[0].location['x'], linLayoutIndex5[0].location['y']
        self.driver.swipe(linLayoutIndex5X, linLayoutIndex5Y, linLayoutIndex1X, linLayoutIndex1Y, 800)
        sleep(2)
        duplicate = False
        while(not duplicate):
            el = self.driver.find_elements_by_xpath(req.XPATH_FOR_SONG_TITLE)
            songsOnScreen = [x.text for x in el]
            duplicate = sorted(songsOnScreen) == sorted(songsOnPreviousScreen)
            songs = songs + songsOnScreen
            songsOnPreviousScreen = songsOnScreen
            linLayoutIndex0 = self.driver.find_elements_by_xpath(req.XPATH_FOR_LINEAR_LAYOUT_INDEX_0)
            linLayoutIndex0X, linLayoutIndex0Y = linLayoutIndex0[0].location['x'], linLayoutIndex0[0].location['y']
            linLayoutIndex8 = self.driver.find_elements_by_xpath(req.XPATH_FOR_LINEAR_LAYOUT_INDEX_8)
            try:
                linLayoutIndex8X, linLayoutIndex8Y = linLayoutIndex8[0].location['x'], linLayoutIndex8[0].location['y']
            except(IndexError):
                break
            self.driver.swipe(linLayoutIndex8X, linLayoutIndex8Y, linLayoutIndex0X, linLayoutIndex0Y, 800)
            sleep(2)
        f = open(fileName,"w")
        songs = list(OrderedDict.fromkeys(songs))
        print(len(songs))
        for song in songs:
            f.write(song+"\n")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)


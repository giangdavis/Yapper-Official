import queue, threading, sys
# import time

import PySimpleGUI as sg
import yapper_client_class as yapper

client = yapper.Client()
client.start('127.0.0.1')

lock = threading.Lock()

guiQueue = queue.Queue()
threading.Thread(target=client.getData, args=(500, lock, guiQueue)).start()
# threading.Thread(target=client.getData, args=(200, guiQueue), daemon=True).start()

menu = [['Lobby', ['View current Rooms', 'Broadcast']],
        ['Room', ['Create/Join', 'List Members']],
            ['Friend', ['Add', 'Remove']]]

layout = [[sg.Menu(menu)], [(sg.Text('Chat Feed', size=[40,1]))],
          [sg.Output(key='feed', size=(80,20))],
          [sg.Multiline(key='input', size=(70,5), enter_submits=True, disabled=False, do_not_clear=True, autoscroll=True)],
          [sg.Button('EXIT')]]

'''
layout = [[sg.Menu(menu)],[(sg.Text('Chat Feed', size=[40, 1]))],
          [sg.Output(key='FEED', size=(80, 20)), sg.RealtimeButton('chat')],
          [sg.Multiline(key='INPUT', size=(70, 5), enter_submits=True, disabled=False, do_not_clear=True,
                        autoscroll=True),
           sg.RealtimeButton('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0])), sg.RealtimeButton('members'),
           sg.RealtimeButton('create'),
           sg.RealtimeButton('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]
'''

window = sg.Window('Yapper', layout, default_element_size=(30, 2), finalize=True)

num = 0

while True:

    event, values = window.read(timeout=100)

    #    EXAMPLE UPDATES: (KEEP FOR REFERENCE)
    #    window['FEED'].update(message)
    #    window['INPUT'].update(disabled=False)

    # LOCK EXAMPLE
    # elif event == 'commands':
    #    if lock.locked(): # second thread trying to do the same, continue tho
    #        continue
    #    else:
    #        lock.acquire() # acquire here, release: when server returns and msg is printed
    #        client.displayCommands()

    if event == 'Create/Join':
        client.createRoom()
    elif event == 'View current rooms':
        client.roomInfo()
    elif event == 'List Members':
        client.listMembers()
    elif event == 'Broadcast':
        client.listMembers()
    elif event == 'SEND':  # add enter key
        if lock.locked():
            continue
        else:
            lock.acquire()
            msg = values.get('INPUT')
            client.chat(msg)
            window['INPUT'].update("")
    elif event in (None, 'EXIT'):
        break

        # loop through messages coming in from threads
    activeRoomW = False
    while True:
        try:
            message = guiQueue.get_nowait()
        except queue.Empty:  # get_nowait() will get exception when queue is empty
            break
        # if msg received from queue, display the message in the window
        if message:
            if message == 'You have successfully connected to the Lobby!!! What is your name?\n':
                client.welcomeMenu()
            elif message == '!!!!!norooms@!@!@!':
                sg.popup("There are no rooms right now!")
            elif 'listOfRooms!!@!' in message:
                activeRoomW = True
                client.displayRooms(message)
            else:
                print(message)
                if lock.locked():
                    lock.release()
window.close()
sys.exit()

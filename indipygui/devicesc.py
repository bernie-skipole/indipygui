
import collections

import customtkinter

from .vectorsc import LightPane, SwitchPane, TextPane, NumberPane, BLOBPane


def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"


class DeviceScreen:

    def __init__(self, ipygui, devicename):
        """A Device screen, opens a CTkToplevel when user picks a device."""
        self.ipygui = ipygui
        self.devicename = devicename
        self.devicewin = customtkinter.CTkToplevel(ipygui.app)
        self.devicewin.geometry("1000x800")
        self.devicewin.title("Device : " + devicename)
        self.devicewin.grid_columnconfigure(0, weight=1)
        self.devicewin.grid_rowconfigure(1, weight=1)

        # create two frames, a messages frame holding device messages
        #                    a frame to hold the tabbed device contents

        self.devicemessagepane = DeviceMessagePane(self.ipygui, self.devicewin, self.devicename)

        self.main_frame = customtkinter.CTkScrollableFrame(self.devicewin)
        self.main_frame.grid(row=1, column=0, padx=4, pady=4, sticky="nswe")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Set a tabview into self.main_frame
        self.grouptabview = customtkinter.CTkTabview(self.main_frame, anchor="nw")
        self.grouptabview.grid(row=0, column=0, padx=4, sticky="nswe")
        groupset = set(vector.group for vector in self.ipygui.snapshot[devicename].values())
        groups = list(groupset)
        groups.sort()
        self.grouptabs = {}   # name:tab
        for group in groups:
            gtab = self.grouptabview.add(group)
            gtab.grid_columnconfigure(0, weight=1)
            self.grouptabs[group] = gtab

        # create a vector frame, set in dictionary of name:vectorpane object
        self.vectorframes = {}
        # vector_row - the grid row of each vector frame
        self.vector_row = 0

        # add vectors to the gtabs
        for vectorname in self.ipygui.snapshot[devicename].keys():
            self.add_vector(vectorname)       

    def add_message(self, message):
        self.devicemessagepane.add_message(message)

    def add_vector(self, vectorname):
        "Called when a define vector is called, if this vector not already known about, it is added"
        if vectorname in self.vectorframes:
            # must update the frame here since defines can include up to date values
            self.set_vector(vectorname)
            return
        # get the vector
        vector = self.ipygui.snapshot[self.devicename][vectorname]
        if vector.group not in self.grouptabs:
            gtab = self.grouptabview.add(vector.group)
            gtab.grid_columnconfigure(0, weight=1)
            self.grouptabs[vector.group] = gtab
        else:
            gtab = self.grouptabs[vector.group]
        # make vector object which creates the frame
        if vector.vectortype == "LightVector":
            self.vectorframes[vectorname] = LightPane(self.ipygui, gtab, vector, self.vector_row)
        elif vector.vectortype == "SwitchVector":
            self.vectorframes[vectorname] = SwitchPane(self.ipygui, gtab, vector, self.vector_row)
        elif vector.vectortype == "TextVector":
            self.vectorframes[vectorname] = TextPane(self.ipygui, gtab, vector, self.vector_row)
        elif vector.vectortype == "NumberVector":
            self.vectorframes[vectorname] = NumberPane(self.ipygui, gtab, vector, self.vector_row)
        elif vector.vectortype == "BLOBVector":
            self.vectorframes[vectorname] = BLOBPane(self.ipygui, gtab, vector, self.vector_row)

        self.vector_row += 1


    def set_vector(self, vectorname):
        "Called when a set vector is called"
        if vectorname not in self.vectorframes:
            # No need to update the frame, as it is not known about
            return
        # get the vector
        vector = self.ipygui.snapshot[self.devicename][vectorname]
        if not vector.enable:
            return
        # get the vector pane and call its set_vector method
        vectorpane = self.vectorframes[vectorname]
        vectorpane.set_vector(vector)


class DeviceMessagePane:

    def __init__(self, ipygui, devicewin, devicename):
        self.ipygui = ipygui
        self.devicewin = devicewin
        self.devicename = devicename

        self.device_message_frame = customtkinter.CTkFrame(self.devicewin)
        self.device_message_frame.grid(row=0, column=0, padx=4, pady=4, sticky="nswe")
        self.device_message_frame.grid_columnconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(self.device_message_frame, corner_radius=0, fg_color="transparent", height=120, wrap="none")
        self.textbox.grid(row=0, column=0, sticky="nsew")

        # self.textlist is a deque of messages
        self.textlist = collections.deque(maxlen=4)

        self.add_message(f"Messages from {self.devicename} will appear here")
        # add messages
        messagelist = list(self.ipygui.snapshot[devicename].messages)
        for message in reversed(messagelist):
            self.add_message(message)


    def add_message(self, message):
        "Adds latest message to MessagePane, and limits the number of messages to 4"
        if isinstance(message, str):
            self.textlist.append(message)
        else:
            self.textlist.append(localtimestring(message[0]) + "  " + message[1])
        self.textbox.configure(state="normal")
        self.textbox.delete('0.0', "end")
        self.textbox.insert("0.0", "\n".join(list(self.textlist)) + "\n")
        self.textbox.configure(state="disabled")
        self.textbox.see(f"{len(self.textlist)-1}.0")








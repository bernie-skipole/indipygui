
import collections, pathlib, functools

import customtkinter


def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"


class StartScreen:


    def __init__(self, ipygui):
        """The top start screen."""
        self.ipygui = ipygui
        self.app = self.ipygui.app
        self.app.grid_columnconfigure(0, weight=2)
        self.app.grid_columnconfigure(1, weight=3)
        self.app.grid_rowconfigure((0,1), weight=1)
        self.app.grid_rowconfigure(2, weight=4)

        self.devicepane = DevicePane(self.ipygui)
        self.connectionpane = ConnectionPane(self.ipygui)
        self.blobpane = BlobPane(self.ipygui)
        self.messagepane = MessagePane(self.ipygui)

    def add_device(self, devicename):
        self.devicepane.add_device(devicename)

    def remove_device(self, devicename):
        self.devicepane.remove_device(devicename)

    def clear_devices(self):
        self.devicepane.clear()

    def add_message(self, message):
        self.messagepane.add_message(message)

    def set_connected(self):
        self.connectionpane.set_connected()

    def set_disconnected(self):
        self.connectionpane.set_disconnected()




class MessagePane:

    def __init__(self, ipygui):

        self.ipygui = ipygui
        self.app = self.ipygui.app

        self.message_frame = customtkinter.CTkFrame(self.app)
        self.message_frame.grid_columnconfigure(0, weight=1)
        self.message_frame.grid_rowconfigure(0, weight=1)
        self.message_frame.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="nswe")

        self.textbox = customtkinter.CTkTextbox(self.message_frame, corner_radius=0, fg_color="transparent", wrap="none")
        self.textbox.grid(row=0, column=0, sticky="nsew")

        # self.textlist is a deque of messages
        self.textlist = collections.deque(maxlen=6)

        self.mode_button = customtkinter.CTkSegmentedButton(self.message_frame, values=["Light", "Dark"],
                                                            command=self.change_mode)
        self.mode_button.grid(row=1, column=0, sticky="ns")
        self.mode_button.set("Light")

    def add_message(self, message):
        "Adds latest message to MessagePane, and limits the number of messages to 6"

        if isinstance(message, str):
            self.textlist.append(message)
        else:
            self.textlist.append(localtimestring(message[0]) + "  " + message[1])

        self.textbox.configure(state="normal")
        self.textbox.delete('0.0', "end")
        self.textbox.insert("0.0", "\n".join(list(self.textlist)) + "\n")
        self.textbox.configure(state="disabled")
        self.textbox.see(f"{len(self.textlist)-1}.0")

    def change_mode(self, mode):
        customtkinter.set_appearance_mode(mode)


class DevicePane:

    def __init__(self, ipygui):

        self.ipygui = ipygui
        self.app = self.ipygui.app

        self.device_frame = customtkinter.CTkScrollableFrame(self.app, label_text="Devices", width=200)
        self.device_frame.grid_columnconfigure(0, weight=1)
        self.device_frame.grid_rowconfigure(0, weight=1)
        self.device_frame.grid(row=0, column=0, rowspan=2, padx=4, pady=4, sticky="nswe")

        self.devicelist = []  # list of devicenames
        self.buttonlist = []

    def add_device(self, devicename):
        if devicename in self.devicelist:
            return
        listlength = len(self.devicelist)
        self.devicelist.append(devicename)
        self.devicelist.sort()
        row = self.devicelist.index(devicename)
        command = functools.partial(self.ipygui.open_devicesc, devicename)
        button = customtkinter.CTkButton(self.device_frame, text=devicename, command = command)
        if row == listlength:
            # button has been added
            button.grid(row=row, column=0, padx=10, pady=10)
            self.buttonlist.append(button)
        else:
            # button has been inserted
            self.buttonlist.insert(row, button)
            for r, btn in enumerate(self.buttonlist):
                btn.grid(row=r, column=0, padx=10, pady=10)

    def remove_device(self, devicename):
        if devicename not in self.devicelist:
            return
        row = self.devicelist.index(devicename)
        self.devicelist.pop(row)
        button = self.buttonlist.pop(row)
        button.destroy()
        for r, btn in enumerate(self.buttonlist):
            btn.grid(row=r, column=0, padx=10, pady=10)

    def clear(self):
        for btn in self.buttonlist:
            btn.destroy()
        self.devicelist.clear()
        self.buttonlist.clear()


class ConnectionPane:

    def __init__(self, ipygui):

        self.ipygui = ipygui
        self.app = self.ipygui.app

        self.connection_frame = customtkinter.CTkFrame(self.app)
        self.connection_frame.grid_columnconfigure(0, weight=1)
        self.connection_frame.grid(row=0, column=1, padx=4, pady=4, sticky="nswe")

        self.toplabel = customtkinter.CTkLabel(self.connection_frame, text="Set INDI server")
        self.toplabel.grid(row=0, column=0, padx=20, sticky="we")

        self.hostport = customtkinter.CTkEntry(self.connection_frame, corner_radius=0, placeholder_text="Hostname:Port")
        self.hostport.grid(row=1, column=0, padx=20, pady=20, sticky="we")

        self.hostportstring = f"{self.ipygui.indihost}:{self.ipygui.indiport}"

        self.hostport.insert(0, self.hostportstring)

        self.currentlabel = customtkinter.CTkLabel(self.connection_frame, text="Current server : " + self.hostportstring, width=600, anchor="w")

        if self.ipygui.qclient is None:
            self.hostport.configure(state="normal")
            self.currentlabel.configure(text="Disconnected. Input Hostname:Port and press Connect")
        else:
            self.hostport.configure(state="disabled")

        self.currentlabel.grid(row=2, column=0, padx=20, sticky="we")

        self.button = customtkinter.CTkButton(self.connection_frame, text="Disconnect", command=self.ipygui.closeconnection)
        self.button.grid(row=3, column=0, padx=20, pady=(20,30))

    def set_connected(self):
        self.hostport.configure(state="normal")
        self.hostport.delete(0, "end")
        self.hostport.insert(0, self.hostportstring)
        self.hostport.configure(state="disabled")
        self.currentlabel.configure(text="Current server : " + self.hostportstring)
        self.button.configure(text="Disconnect", command=self.ipygui.closeconnection)

    def set_disconnected(self):
        self.hostport.configure(state="normal")
        self.button.configure(text="Connect", command=self.makenewconnection)
        self.currentlabel.configure(text="Disconnected. Input Hostname:Port and press Connect")

    def makenewconnection(self):
        # Find the host and port, and set into self.ipygui.indihost, self.ipygui.indiport
        value = self.hostport.get()
        self.hostportstring, hoststring, portint = self.test_hostport(value)
        self.ipygui.indihost = hoststring
        self.ipygui.indiport = portint
        self.ipygui.newconnection()
        # the newconnection call creates a new qclient and then calls set_connected


    def test_hostport(self,value):
        "Returns string hostport, string host, integer port"
        hostport = value.strip()
        if hostport:
            hostportlist = hostport.split(":")
            if len(hostportlist) == 2:
                host = hostportlist[0].strip()
                port = hostportlist[1].strip()
                if not host:
                    host = "localhost"
                if not port.isdigit():
                    port = "7624"
                hostport = f"{host}:{port}"
            else:
                host = hostportlist[0].strip()
                if host:
                    hostport = host +":7624"
                else:
                    hostport = "localhost:7624"
        else:
            hostport = "localhost:7624"
        host,port = hostport.split(":")
        port = int(port)
        return hostport, host, port


class BlobPane:

    def __init__(self, ipygui):

        self.ipygui = ipygui
        self.app = self.ipygui.app

        self.blob_frame = customtkinter.CTkFrame(self.app)
        self.blob_frame.grid_columnconfigure(0, weight=1)
        self.blob_frame.grid(row=1, column=1, padx=4, pady=4, sticky="nswe")

        self.toplabel = customtkinter.CTkLabel(self.blob_frame, text="Set BLOB folder")
        self.toplabel.grid(row=0, column=0, padx=20, sticky="we")

        self.blobfolder = customtkinter.CTkEntry(self.blob_frame, corner_radius=0, placeholder_text="Set BLOB folder here")
        self.blobfolder.grid(row=1, column=0, padx=20, pady=20, sticky="we")

        self.bloblabel = customtkinter.CTkLabel(self.blob_frame, text="Received BLOBs disabled", anchor="w")
        self.bloblabel.grid(row=2, column=0, padx=20, sticky="we")

        self.button = customtkinter.CTkButton(self.blob_frame, text="Set Folder", command=self.setblobfolder)
        self.button.grid(row=3, column=0, padx=20, pady=(20,30))


    def setblobfolder(self):
        value = self.blobfolder.get()
        if not value:
            self.ipygui.blobfolder = None
            self.blobfolder.delete(0, "end")
            self.blobfolder.configure(placeholder_text="Set BLOB folder here")
            self.bloblabel.configure(text="Received BLOBs disabled")
            return

        blobfolder = pathlib.Path(value).expanduser().resolve()
        if not blobfolder.is_dir():
            self.ipygui.blobfolder = None
            self.blobfolder.delete(0, "end")
            self.blobfolder.configure(placeholder_text="Invalid Folder! Set BLOB folder here")
            self.bloblabel.configure(text="Received BLOBs disabled")
            return

        self.ipygui.blobfolder = blobfolder
        self.blobfolder.delete(0, "end")
        self.blobfolder.insert(0, blobfolder)
        self.bloblabel.configure(text="Received BLOBs enabled")



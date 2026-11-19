
import pathlib, queue, threading, asyncio, logging

from indipyclient.queclient import QueClient

import customtkinter

from . import startsc, devicesc


logger = logging.getLogger()
logger.addHandler(logging.NullHandler())




version = "0.0.1"



class IPyGui():
    """An INDI GUI."""

    def __init__(self, host="localhost", port=7624, blobfolder=None):
        self.indihost = host
        self.indiport = port
        if blobfolder:
            bf = pathlib.Path(blobfolder).expanduser().resolve()
            if bf.is_dir():
                self._blobfolder = bf
            else:
                self._blobfolder = None
        else:
            self._blobfolder = None

        # create two queues
        # rxque giving received data
        self._rxque = queue.Queue(maxsize=4)
        # txque transmit data
        self._txque = queue.Queue(maxsize=4)

        # An INDI QueClient will be created in a thread when rungui is called
        self.qclient = None
        self._clientthread = None

        # create a tkinter app
        self.app = customtkinter.CTk()
        self.app.title(f"indipygui version {version}")

        # self.sc will be the main startscreen, created when rungui is called
        self.sc = None

        # This dictionary will be a dictionary of devicename:devicesc, created as device windows are created
        self.devicewindows = {}

        # This is updated with the latest client snapshot
        self.snapshot = None



    def newconnection(self):
        "Creates a new instance of self.qclient, with a new connection"

        if self._clientthread is None or not self._clientthread.is_alive():
            self.qclient = QueClient(self._txque, self._rxque, self.indihost, self.indiport, self._blobfolder)
            self._clientthread = threading.Thread(target=asyncio.run, args=(self.qclient.asyncrun(),))
            self._clientthread.start()
            self.sc.set_connected()


    def send_data(self, data):
        "Send data down self._txque"
        self._txque.put(data)


    def closeconnection(self):
        "Shut down the connection"
        # Send a None value to shut down the queclient
        self._txque.put(None)
        # and wait for the clientthread to stop
        if self._clientthread is not None and self._clientthread.is_alive():
            self._clientthread.join()
            self.qclient = None
            self.sc.set_disconnected()
            self.sc.add_message("Client disconnected")
            self.sc.clear_devices()
            for dsc in self.devicewindows.values():
                if dsc.devicewin.winfo_exists():
                    dsc.devicewin.destroy()
            self.devicewindows.clear()


    def _set_blobfolder(self, blobfolder):
        self._blobfolder = blobfolder
        if self.qclient is not None:
            self.qclient.BLOBfolder = blobfolder

    def _get_blobfolder(self):
        return self._blobfolder

    blobfolder = property(fget=_get_blobfolder, fset=_set_blobfolder)

    def rungui(self):
        "Create INDI QueClient and run it in a thread Make the StartScreen and run the gui app"

        self.app.geometry("1000x600")


        # create the startscreen
        self.sc = startsc.StartScreen(self)

        # run the queclient in its own thread
        self.newconnection()


        # start checking the rxque
        self.readrxque()

        self.app.mainloop()

        # When the gui loop ends, close the connection
        self._txque.put(None)

        if self._clientthread is not None and self._clientthread.is_alive():
            self._clientthread.join()


    def open_devicesc(self, devicename):
        if devicename not in self.devicewindows or not self.devicewindows[devicename].devicewin.winfo_exists():
            self.devicewindows[devicename] = devicesc.DeviceScreen(self, devicename)
        else:
            self.devicewindows[devicename].devicewin.lift()
            self.devicewindows[devicename].devicewin.focus()  # if window exists focus it


    def readrxque(self):
        "Read rxque"
        try:
            event = self._rxque.get_nowait()
        except queue.Empty:
            # and read again after 100ms
            self.app.after(100, self.readrxque)
            return

        self.snapshot = event.snapshot

        if event.eventtype == "Message":
            if event.devicename is None:
                # Add client message to the startscreen
                self.sc.add_message(self.snapshot.messages[0])
            elif event.devicename in self.devicewindows and self.devicewindows[event.devicename].devicewin.winfo_exists():
                dsc = self.devicewindows[event.devicename]
                # so dsc is the displayed device screen object, update it with the new message
                message = self.snapshot[event.devicename].messages[0]
                dsc.add_message(message)


        elif event.eventtype == "Define" or event.eventtype == "DefineBLOB":
            # Define, get the devicename
            self.sc.add_device(event.devicename)

        elif event.eventtype == "Set" or event.eventtype == "SetBLOB":
            if event.devicename in self.devicewindows and self.devicewindows[event.devicename].devicewin.winfo_exists():
                dsc = self.devicewindows[event.devicename]
                # so dsc is the displayed device screen object, update it with the new vector
                dsc.set_vector(event.vectorname)


        elif event.eventtype == "Delete":
            devicename = event.devicename
            if devicename in self.snapshot:
                device = self.snapshot[devicename]
                if not device.enable:
                    self.sc.remove_device(devicename)
                    # and shutdown device window if openned
                    if devicename in self.devicewindows:
                        dsc = self.devicewindows[devicename]
                        if dsc.devicewin.winfo_exists():
                            dsc.devicewin.destroy()
                            del self.devicewindows[devicename]





        # and read again after 100ms
        self.app.after(100, self.readrxque)













import functools

from datetime import datetime, timezone

import customtkinter

from indipyclient import getfloat


def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"


def valuecolor(value):
    if value == "Ok":
        background = "darkgreen"
        color = "white"
    elif value == "Alert":
        background = "red"
        color = "white"
    elif value == "Busy":
        background = "yellow"
        color = "black"
    elif value == "Idle":
        background = "black"
        color = "white"
    else:
        # unknown value, flag it with red on red
        background = "red"
        color = "red"

    return background, color

class VectorParentPane:

    "This creates the full vector frame, and sets label, message and state"

    def __init__(self, ipygui, gtab, vector, row):
        self.ipygui = ipygui
        self.gtab = gtab
        self.vector = vector

        self.vector_frame = customtkinter.CTkFrame(self.gtab, border_color=("white", "grey"), border_width=2)
        self.vector_frame.grid(row=row, column=0, padx=4, pady=4, sticky="nswe")
        self.vector_frame.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self.vector_frame, text=self.vector.label, anchor="w")
        self.label.grid(row=0, column=0, padx=10, pady=(4,0), sticky="w")

        if self.vector.message:
            message = localtimestring(self.vector.message_timestamp) + "  " + self.vector.message
        else:
            message = ""

        self.message = customtkinter.CTkLabel(self.vector_frame, text=message, anchor="w")
        self.message.grid(row=2, column=0, padx=10, pady=(0,4), sticky="w")

        # message is on row 2, so members start on row 3
        self.members_frame = customtkinter.CTkFrame(self.vector_frame, fg_color="transparent")
        self.members_frame.grid(row=3, column=0, padx=4, pady=4, sticky="nswe")

        background, color = valuecolor(self.vector.state)

        self.statetime = customtkinter.CTkLabel(self.vector_frame, text=localtimestring(self.vector.timestamp), anchor="e")
        self.statetime.grid(row=0, column=0, padx=(10,140), pady=(4,0), sticky="e")
 
        self.state = customtkinter.CTkLabel(self.vector_frame, text=self.vector.state, width=100, fg_color=background, text_color=color)
        self.state.grid(row=0, column=0, padx=10, pady=(4,0), sticky="e")


    def set_vector(self, vector):
        "Vector has changed, update the frame"
        self.vector = vector
        # update the message
        if self.vector.message:
            message = localtimestring(self.vector.message_timestamp) + "  " + self.vector.message
            self.message.configure(text=message)
        # update the state
        background, color = valuecolor(self.vector.state)
        self.statetime.configure(text=localtimestring(self.vector.timestamp))
        self.state.configure(text=self.vector.state, fg_color=background, text_color=color)




class LightPane(VectorParentPane):

    def __init__(self, ipygui, gtab, vector, row):
        super().__init__(ipygui, gtab, vector, row)
        self.members_frame.grid_columnconfigure(0, weight=1)
        self.members_frame.grid_columnconfigure(1, weight=1)
        self.members = {} # dictionary of membername: [CTkLabel showing label, CTkLabel showing value, value]
        memberrow = 0
        lastrow = len(vector)-1
        for membername, value in vector.items():
            background, color = valuecolor(value)
            label = vector.memberlabel(membername)

            self.members[membername] = [ customtkinter.CTkLabel(self.members_frame, text=label, anchor="e"),
                                         customtkinter.CTkLabel(self.members_frame, text=value, width=100, fg_color=background, text_color=color),
                                         value ]
            if memberrow == lastrow:
                # extra space beneath the last member
                self.members[membername][0].grid(row=memberrow, column=0, padx=20, pady=(10,20), sticky="e")
                self.members[membername][1].grid(row=memberrow, column=1, padx=10, pady=(10,20), sticky="w")
            else:
                self.members[membername][0].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                self.members[membername][1].grid(row=memberrow, column=1, padx=10, pady=10, sticky="w")

            memberrow += 1          
    
    def set_vector(self, vector):
        super().set_vector(vector)
        for membername, value in vector.items():
            if membername not in self.members:
                continue
            if value == self.members[membername][2]:
                # no change
                continue
            background, color = valuecolor(value)
            self.members[membername][1].configure(text=value, fg_color=background, text_color=color)
            self.members[membername][2] = value



class TextPane(VectorParentPane):

    def __init__(self, ipygui, gtab, vector, row):
        super().__init__(ipygui, gtab, vector, row)

        permission = vector.perm

        self.submit_button = None

        self.members = {}
        memberrow = 0
        if vector.perm == "ro":
            # there is no data submission

            self.members_frame.grid_columnconfigure(1, weight=3) # column 1 for the received text

            lastrow = len(vector)-1
            for membername, value in vector.items():

                if not value:
                    value = "Waiting for received value"
                    color = "white"
                else:
                    color = "black"

                label = vector.memberlabel(membername)

                self.members[membername] = [ value,
                                             customtkinter.CTkLabel(self.members_frame, text=label, anchor="e"),
                                             customtkinter.CTkLabel(self.members_frame, text=value, anchor="w",
                                                                fg_color=("light grey", "dark grey"),
                                                                text_color=color),
                                            ]
                if memberrow == lastrow:
                    # extra space beneath the last member
                    self.members[membername][1].grid(row=memberrow, column=0, padx=20, pady=(10,20), sticky="e")
                    self.members[membername][2].grid(row=memberrow, column=1, padx=(10,50), pady=(10,20), sticky="we")
                else:
                    self.members[membername][1].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                    self.members[membername][2].grid(row=memberrow, column=1, padx=(10,50), pady=10, sticky="we")

                memberrow += 1
        else:

            self.members_frame.grid_columnconfigure(1, weight=3) # column 1 for the received text, and input field
                                                                 # column 2, unweighted, for the clear field
 

            for membername, value in vector.items():

                if not value:
                    value = "Waiting for received value"
                    color = "white"
                else:
                    color = "black"

                label = vector.memberlabel(membername)
                clearcommand = functools.partial(self._clear_input, membername)

                self.members[membername] = [ value,
                                             customtkinter.CTkLabel(self.members_frame, text=label, anchor="e"),
                                             customtkinter.CTkLabel(self.members_frame, text=value, anchor="w",
                                                                fg_color=("light grey", "dark grey"),
                                                                text_color=color),
                                             customtkinter.CTkEntry(self.members_frame, corner_radius=0, placeholder_text="Input new text"),
                                             customtkinter.CTkButton(self.members_frame, text="Clear", command=clearcommand)

                                           ]
                self.members[membername][1].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                self.members[membername][2].grid(row=memberrow, column=1, padx=(10,50), pady=10, sticky="we")
                self.members[membername][3].grid(row=memberrow+1, column=1, padx=(10,50), pady=10, sticky="we")
                if vector[membername]:
                    self.members[membername][3].set(value)
                self.members[membername][4].grid(row=memberrow+1, column=2, padx=(10,50), pady=10)
                memberrow += 2

            self.submit_button = customtkinter.CTkButton(self.members_frame, text="Submit", command=self._submit)
            self.submit_button.grid(row=memberrow, column=1, padx=(10,50), pady=(10, 20), sticky="e")


    def set_vector(self, vector):
        super().set_vector(vector)

        for membername, value in vector.items():
            if membername not in self.members:
                continue
            if value == self.members[membername][0]:
                # no change
                continue
            self.members[membername][0] = value
            self.members[membername][2].configure(text=value, text_color="black")

    def _clear_input(self, membername):
        if self.vector.perm == "ro":
            return
        if membername not in self.members:
            return
        value = self.members[membername][3].get()
        if value:
            self.members[membername][3].delete(0, len(value))

    def _submit(self):
        "Get data from entry widgets and send to queclient using ipygui.send_data"
        if self.vector.perm == "ro":
            return
        valuedict = {}
        for membername, widgets in self.members.items():
            value = widgets[3].get()
            if value:
                valuedict[membername] = value
        # send (devicename, vectorname, valuedict)
        # where valuedict is a membername to membervalue dictionary, which will be transmitted to the server.
        if valuedict:
            data = (self.vector.devicename, self.vector.name, valuedict)
            self.ipygui.send_data(data)
            # update the state
            background, color = valuecolor('Busy')
            self.statetime.configure(text=localtimestring(datetime.now(tz=timezone.utc)))
            self.state.configure(text='Busy', fg_color=background, text_color=color)

        
class NumberPane(VectorParentPane):

    def __init__(self, ipygui, gtab, vector, row):
        super().__init__(ipygui, gtab, vector, row)

        permission = vector.perm

        self.members = {}
        memberrow = 0
        if vector.perm == "ro":
            # there is no data submission

            self.members_frame.grid_columnconfigure(1, weight=3) # column 1 for the received numbers

            lastrow = len(vector)-1
            for membername in vector:

                value = vector.getformattedvalue(membername)

                label = vector.memberlabel(membername)

                self.members[membername] = [ value,
                                             customtkinter.CTkLabel(self.members_frame, text=label, anchor="e"),
                                             customtkinter.CTkLabel(self.members_frame, text=value, anchor="w",
                                                                fg_color=("light grey", "dark grey"),
                                                                text_color="black"),
                                            ]
                if memberrow == lastrow:
                    # extra space beneath the last member
                    self.members[membername][1].grid(row=memberrow, column=0, padx=20, pady=(10,20), sticky="e")
                    self.members[membername][2].grid(row=memberrow, column=1, padx=(10,50), pady=(10,20), sticky="we")
                else:
                    self.members[membername][1].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                    self.members[membername][2].grid(row=memberrow, column=1, padx=(10,50), pady=10, sticky="we")

                memberrow += 1
        else:

            self.members_frame.grid_columnconfigure(1, weight=3) # column 1 for the received text, and input field
                                                                 # column 2, unweighted, for the clear field
 
            for membername, value in vector.items():

                value = vector.getformattedvalue(membername)

                label = vector.memberlabel(membername)
                clearcommand = functools.partial(self._clear_input, membername)

                self.members[membername] = [ value,
                                             customtkinter.CTkLabel(self.members_frame, text=label, anchor="e"),
                                             customtkinter.CTkLabel(self.members_frame, text=value, anchor="w",
                                                                fg_color=("light grey", "dark grey"),
                                                                text_color="black"),
                                             customtkinter.CTkEntry(self.members_frame, corner_radius=0, placeholder_text="Input new value"),
                                             customtkinter.CTkButton(self.members_frame, text="Clear", command=clearcommand)

                                           ]
                self.members[membername][1].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                self.members[membername][2].grid(row=memberrow, column=1, padx=(10,50), pady=10, sticky="we")
                self.members[membername][3].grid(row=memberrow+1, column=1, padx=(10,50), pady=10, sticky="we")
                if vector[membername]:
                    self.members[membername][3].set(value)
                self.members[membername][4].grid(row=memberrow+1, column=2, padx=(10,50), pady=10)
                memberrow += 2

            self.submit_button = customtkinter.CTkButton(self.members_frame, text="Submit", command=self._submit)
            self.submit_button.grid(row=memberrow, column=1, padx=(10,50), pady=(10, 20), sticky="e")

            # create an error message and immediately remove it, ready to be shown when needed
            self.errormessage = customtkinter.CTkLabel(self.members_frame, text="Invalid number!", anchor="e")
            self.errormessage.grid(row=memberrow, column=1, padx=10, pady=(10, 20), sticky="w")
            self.errormessage.grid_remove()


    def set_vector(self, vector):
        super().set_vector(vector)

        for membername in vector:

            value = vector.getformattedvalue(membername)

            if membername not in self.members:
                continue
            if value == self.members[membername][0]:
                # no change
                continue
            self.members[membername][0] = value
            self.members[membername][2].configure(text=value, text_color="black")


    def _clear_input(self, membername):
        if self.vector.perm == "ro":
            return
        if membername not in self.members:
            return
        value = self.members[membername][3].get()
        if value:
            self.members[membername][3].delete(0, len(value))


    def _submit(self):
        "Get data from entry widgets and send to queclient using ipygui.send_data"
        if self.vector.perm == "ro":
            return
        valuedict = {}
        allok = True
        # show the error message, to be removed if submit is ok
        self.errormessage.grid()
        for membername, widgets in self.members.items():
            widgets[3].configure(border_color="black")
            value = widgets[3].get().strip()
            if value:
                try:
                    floatvalue = getfloat(value)
                except TypeError:
                    allok = False
                    widgets[3].configure(border_color="red")
                else:            
                    valuedict[membername] = value
            else:
                # an empty string is an error
                allok = False
                widgets[3].configure(border_color="red")
        # send (devicename, vectorname, valuedict)
        # where valuedict is a membername to membervalue dictionary, which will be transmitted to the server.
        if allok:
            self.errormessage.grid_remove()
            data = (self.vector.devicename, self.vector.name, valuedict)
            self.ipygui.send_data(data)
            # update the state
            background, color = valuecolor('Busy')
            self.statetime.configure(text=localtimestring(datetime.now(tz=timezone.utc)))
            self.state.configure(text='Busy', fg_color=background, text_color=color)




class SwitchPane(VectorParentPane):

    def __init__(self, ipygui, gtab, vector, row):
        super().__init__(ipygui, gtab, vector, row)

        permission = vector.perm

        self.members_frame.grid_columnconfigure(0, weight=1, uniform='tag')
        self.members_frame.grid_columnconfigure(1, weight=1, uniform='tag')

        self.switch_vars = {}

        self.members = {}
        memberrow = 0
        if vector.perm == "ro":
            # there is no data submission

            lastrow = len(vector)-1
            for membername, value in vector.items():

                self.switch_vars[membername] = customtkinter.StringVar(value=value)

                label = vector.memberlabel(membername)
 
                self.members[membername] = [
                                             customtkinter.CTkLabel(self.members_frame, text=value, anchor="e"), 
                                             customtkinter.CTkSwitch(self.members_frame, text=label, variable=self.switch_vars[membername],
                                                                     onvalue="On", offvalue="Off", state="disabled", text_color_disabled=("black","white"))
                                            ]
                if memberrow == lastrow:
                    # extra space beneath the last member
                    self.members[membername][0].grid(row=memberrow, column=0, padx=20, pady=(10,20), sticky="e")
                    self.members[membername][1].grid(row=memberrow, column=1, padx=(10,50), pady=(10,20), sticky="w")
                else:
                    self.members[membername][0].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                    self.members[membername][1].grid(row=memberrow, column=1, padx=(10,50), pady=10, sticky="w")

                memberrow += 1
        else:
 
            for membername, value in vector.items():

                setswitchcommand = functools.partial(self._set_switch, membername)

                self.switch_vars[membername] = customtkinter.StringVar(value=value)

                label = vector.memberlabel(membername)
 
                self.members[membername] = [
                                             customtkinter.CTkLabel(self.members_frame, text=value, anchor="e"), 
                                             customtkinter.CTkSwitch(self.members_frame, text=label, variable=self.switch_vars[membername],
                                                                     onvalue="On", offvalue="Off", command=setswitchcommand )
                                            ]
                self.members[membername][0].grid(row=memberrow, column=0, padx=20, pady=10, sticky="e")
                self.members[membername][1].grid(row=memberrow, column=1, padx=(10,50), pady=10, sticky="w")

                memberrow += 1

            self.submit_button = customtkinter.CTkButton(self.members_frame, text="Submit", command=self._submit)
            self.submit_button.grid(row=memberrow, column=1, padx=(10,50), pady=(10, 20), sticky="e")

            # create an error message and immediately remove it, ready to be shown when needed
            self.errormessage = customtkinter.CTkLabel(self.members_frame, text="Invalid choice!", anchor="e")
            self.errormessage.grid(row=memberrow, column=0, padx=10, pady=(10, 20), sticky="e")
            self.errormessage.grid_remove()



    def _set_switch(self, membername):
        "Check switches"
        if self.vector.rule == 'AnyOfMany':
            return
        if self.errormessage.grid_info():
            self.errormessage.grid_remove()
        newvals = 0
        # get a count of how many switches are in the on position
        for eachswitch in self.switch_vars.values():
            if eachswitch.get() == "On":
                newvals += 1
        if self.vector.rule == 'OneOfMany':
            if newvals > 1:
                # can only be one
                for eachmember,valdict in self.members.items():
                    if eachmember != membername:
                        self.switch_vars[eachmember].set("Off")
            elif not newvals:
                self.errormessage.configure(text="Warning: At least one must be chosen!")
                self.errormessage.grid()
        elif self.vector.rule == 'AtMostOne':
            if newvals > 1:
                # can only be one
                for eachmember,valdict in self.members.items():
                    if eachmember != membername:
                        self.switch_vars[eachmember].set("Off")


    def _submit(self):
        "Get data from switches and send to queclient using ipygui.send_data"
        if self.vector.perm == "ro":
            return
        if self.vector.rule != 'AnyOfMany':
            newvals = 0
            # get a count of how many switches are in the on position
            for eachswitch in self.switch_vars.values():
                if eachswitch.get() == "On":
                    newvals += 1
            if self.vector.rule == 'OneOfMany':
                if newvals != 1:
                    # can only be one
                    self.errormessage.configure(text="Invalid switch combination!")
                    self.errormessage.grid()
                    return
            elif self.vector.rule == 'AtMostOne':
                if newvals > 1:
                    # cannot be more than one
                    self.errormessage.configure(text="Invalid switch combination!")
                    self.errormessage.grid()
                    return

        valuedict = {}
        for membername, switchvar in self.switch_vars.items():
           valuedict[membername] = switchvar.get()
        # submit the switches
        data = (self.vector.devicename, self.vector.name, valuedict)
        self.ipygui.send_data(data)
        # update the state
        background, color = valuecolor('Busy')
        self.statetime.configure(text=localtimestring(datetime.now(tz=timezone.utc)))
        self.state.configure(text='Busy', fg_color=background, text_color=color)




    def set_vector(self, vector):
        super().set_vector(vector)

        for membername, value in vector.items():
            if membername not in self.members:
                continue
            self.members[membername][0].configure(text=value)
            self.switch_vars[membername].set(value)



class BLOBPane(VectorParentPane):

    def __init__(self, ipygui, gtab, vector, row):
        super().__init__(ipygui, gtab, vector, row)

    def set_vector(self, vector):
        super().set_vector(vector)




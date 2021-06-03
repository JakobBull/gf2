"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import time
import sys
import os
import io
from wx.core import HORIZONTAL
import wx.lib.scrolledpanel as scrolled
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
from error import Error

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors, size):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0],
                         size=size)
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render_value(self, values):
        """Draw a trace"""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        print(len(values))
        for i in range(len(values)):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if values[i] == 1:
                y = 25
            else:
                y = 0
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 0
            else:
                y = 25
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def render_empty(self):
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        # self.render(text)
        self.render_empty()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class SidePanel(wx.Panel):

    def __init__(self, parent, scrolled_panel) -> None:
        super().__init__(parent=parent)

        self.parent = parent
        self.scrolled_panel = scrolled_panel

        # Configure the widgets

        # control setting number of cycles
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")

        # run and continue buttons
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")

        """Setting the value of a signal/ switch
        switch_box takes the value
        zero_button and one_button allow toggling between 0 and 1
        add_switch_executes the add button"""
        self.switch_box_text = wx.StaticText(self, wx.ID_ANY, "Set Switch")
        self.switch_box = wx.ComboBox(
            self, wx.ID_ANY, "Switch", choices=[
                self.parent.names.get_name_string(i) for i in self.parent.devices.find_devices(
                    self.parent.devices.SWITCH)])
        self.zero_button = wx.RadioButton(self, -1, "0", style=wx.RB_GROUP)
        self.one_button = wx.RadioButton(self, -1, "1")
        self.add_switch_button = wx.Button(self, -1, "Set")

        self.monitor_text = wx.StaticText(
            self, wx.ID_ANY, "Set outputs to monitor")
        # monitor_sizer
        all = [self.parent.names.get_name_string(
            i) for i in self.parent.devices.find_devices(None)]
        switches = [self.parent.names.get_name_string(
            i) for i in self.parent.devices.find_devices(self.parent.devices.SWITCH)]
        clocks = [self.parent.names.get_name_string(
            i) for i in self.parent.devices.find_devices(self.parent.devices.CLOCK)]
        choices = [i for i in all if i not in switches and i not in clocks]
        self.monitor_combobox = wx.ComboBox(
            self, wx.ID_ANY, "Select", choices=choices)
        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")

        self.remove_monitor_text = wx.StaticText(
            self, wx.ID_ANY, "Remove monitor")
        # remove_monitor_sizer
        self.remove_monitor_combobox = wx.ComboBox(
            self, wx.ID_ANY, "Select", choices=[
                item.name for item in self.scrolled_panel.item_list])
        self.remove_monitor_button = wx.Button(self, wx.ID_ANY, "Remove")
        self.remove_all_button = wx.Button(self, wx.ID_ANY, "Remove all")
        self.remove_all_button.SetForegroundColour('#ff1a1a')

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)

        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

        self.add_switch_button.Bind(wx.EVT_BUTTON, self.on_update_signal)

        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_monitor)

        self.remove_monitor_button.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.remove_all_button.Bind(wx.EVT_BUTTON, self.on_remove_all_monitors)

        self.side_sizer = wx.BoxSizer(wx.VERTICAL)

        self.cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.remove_monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.remove_monitor_subsizer = wx.BoxSizer(wx.VERTICAL)
        self.remove_monitor_bordersizer = wx.BoxSizer(wx.VERTICAL)
        self.binary_choice_sizer = wx.BoxSizer(wx.VERTICAL)

        self.side_sizer.SetMinSize(self.side_sizer.GetMinSize())
        self.side_sizer.Add(self.cycle_sizer, 1, wx.ALL | wx.EXPAND, 0)
        self.side_sizer.Add(self.button_sizer, 1, wx.ALL | wx.EXPAND, 0)
        self.side_sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL | wx.EXPAND, 5)
        self.side_sizer.Add(self.switch_box_text, 1, wx.ALIGN_CENTER, 0)
        self.side_sizer.Add(self.switch_sizer, 1, wx.EXPAND, 0)
        self.side_sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL | wx.EXPAND, 5)
        self.side_sizer.Add(self.monitor_text, 1, wx.ALL | wx.ALIGN_CENTER, 0)
        self.side_sizer.Add(self.monitor_sizer, 1, wx.ALL | wx.EXPAND, 0)
        self.side_sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL | wx.EXPAND, 5)
        self.side_sizer.Add(self.remove_monitor_text, 1,
                            wx.ALL | wx.ALIGN_CENTER, 5)
        self.side_sizer.Add(self.remove_monitor_sizer,
                            1, wx.ALL | wx.EXPAND, 0)

        self.cycle_sizer.Add(self.text, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        self.cycle_sizer.Add(self.spin, 2, wx.ALL, 5)

        self.button_sizer.Add(self.run_button, 1, wx.ALL | wx.EXPAND, 5)
        self.button_sizer.Add(self.continue_button, 1, wx.ALL | wx.EXPAND, 5)

        self.switch_sizer.Add(self.switch_box, 1, wx.ALL, 5)
        self.switch_sizer.Add(self.binary_choice_sizer, 1, wx.ALL, 5)
        self.switch_sizer.Add(self.add_switch_button, 1, wx.ALL, 5)

        self.binary_choice_sizer.Add(self.zero_button, 0, wx.ALL, 0)
        self.binary_choice_sizer.Add(self.one_button, 0, wx.ALL, 0)

        self.monitor_sizer.Add(self.monitor_combobox, 1, wx.ALL, 5)
        self.monitor_sizer.Add(self.add_monitor_button, 1, wx.ALL, 5)

        self.remove_monitor_sizer.Add(
            self.remove_monitor_bordersizer,
            1,
            wx.RIGHT | wx.LEFT | wx.EXPAND,
            5)
        self.remove_monitor_sizer.Add(
            self.remove_monitor_subsizer, 1, wx.ALL, 5)

        self.remove_monitor_bordersizer.Add(
            self.remove_monitor_combobox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 10)

        self.remove_monitor_subsizer.Add(
            self.remove_monitor_button, 0, wx.ALL | wx.EXPAND, 5)
        self.remove_monitor_subsizer.Add(
            self.remove_all_button, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(self.side_sizer)

    def read_name(self, name_string):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        if name_string is None:
            return None
        else:
            name_id = self.parent.names.query(name_string)
        if name_id is None:
            print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def on_add_monitor(self, event):
        """Handle the event when the add monitor button is pressed"""
        monitor = self.monitor_combobox.GetValue()

        if monitor != "Select":
            self.remove_monitor_combobox.Append(monitor)
            self.scrolled_panel.add_monitor(monitor)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.parent.network.execute_network():
                self.parent.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.parent.monitors.display_signals()
        self.parent.scrolled_panel.render_children()
        return True

    def on_update_signal(self, event):
        """Set the specified switch to the specified signal level."""
        name_string = self.switch_box.GetValue()
        switch_id = self.read_name(name_string)
        if switch_id is not None:
            if self.one_button.GetValue():
                switch_state = 1
            else:
                switch_state = 0
            if self.parent.devices.set_switch(switch_id, switch_state):
                print("Successfully set switch.")
            else:
                print("Error! Invalid switch.")

    def on_remove_monitor(self, event):
        """Handle the event when the remove monitor button is pressed"""
        self.remove_monitor_combobox.Clear()
        self.scrolled_panel.remove_monitor(self.remove_monitor_combobox.Value)
        for item in self.scrolled_panel.item_list:
            self.remove_monitor_combobox.Append(item.name)

    def on_remove_all_monitors(self, event):
        """Handle the event when removign all monitors."""
        self.scrolled_panel.remove_all_monitors()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        self.cycles_completed = 0
        cycles = self.spin.GetValue()
        self.parent.monitors.reset_monitors()
        print("".join(["Running for ", str(cycles), " cycles"]))
        self.parent.devices.cold_startup()
        if self.run_network(cycles):
            self.cycles_completed += cycles

    def on_continue_button(self, event):
        """Continue a previously run simulation."""
        cycles = self.spin.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_combo_select(self, event):
        """Handle event from selecting an event from the combobox dropdown menu"""
        self.canvas.render("selected")


class Monitor(scrolled.ScrolledPanel):
    """
    Scrolled Panel that contains all the monitor traces

    Paramaters:

    parent: Gui passes an instance of itself.
    monitors: Instance of the Monitor class.
    devices: Instance of the Devices class.
    names: Instance of the Names class.

    Public Methods:
    render_children(self): Calls all MonitorItems render method.
    add_monitor(self, text): Add a MonitorItem with name text
    remove_monitor(self, text): Removes the MonitorItem with name text.
    remove_child(self, child): Removes a specific MonitorItem.
    remove_all_monitors(self): Removes all MonitorItems.
    """

    def __init__(self, parent, monitors, devices, names) -> None:
        """Set up the scrolled panel and 
        initialise MonitorItems from definition file."""
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.parent = parent
        self.monitors = monitors
        self.devices = devices
        self.names = names

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.item_list = []

        for key, value in self.monitors.monitors_dictionary.items():
            self.item_list.append(
                MonitorItem(
                    self,
                    self.names.get_name_string(
                        key[0]),
                    self.monitors,
                    self.devices,
                    self.names))
            self.item_list[-1].SetBackgroundColour('#b0bcda')
            self.sizer.Add(self.item_list[-1], 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.sizer)
        self.SetupScrolling()

    def render_children(self):
        """Renders all MonitorItems."""
        for child in self.item_list:
            child.render()

    def add_monitor(self, text):
        """Adds a MonitorItem with name text."""
        self.item_list.append(
            MonitorItem(
                self,
                text,
                self.monitors,
                self.devices,
                self.names))
        self.item_list[-1].SetBackgroundColour('#b0bcda')
        self.sizer.Add(self.item_list[-1], 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetupScrolling()

    def remove_monitor(self, text):
        """Removes a MonitorItems with name text."""
        self.item_list = [item for item in self.item_list if item.name != text]
        for item in self.sizer.GetChildren():
            widget = item.GetWindow()
            if widget.name == text:
                self.sizer.Hide(widget)
                widget.Destroy()
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetupScrolling()

    def remove_child(self, child):
        """Removes the MonitorItem child."""
        for element in self.sizer.GetChildren():
            if element.GetWindow() == child:
                self.sizer.Hide(child)
                child.Destroy()
                self.SetSizer(self.sizer)
                self.sizer.Layout()
                self.SetupScrolling()

    def remove_all_monitors(self):
        """Remove all MonitorItems."""
        for item in self.sizer.GetChildren():
            self.sizer.Hide(item.GetWindow())
            item.GetWindow().Destroy()
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetupScrolling()


class Canvaspanel(scrolled.ScrolledPanel):
    """
    Creates a MyGLCanvas object for each MonitorItem to draw signal trace on.

    Paramaters
    """
    def __init__(self, parent, monitors, devices) -> None:
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.parent = parent
        self.monitors = monitors
        self.devices = devices

        self.canvas = MyGLCanvas(
            self, self.devices, self.monitors, size=(-1, 50))
        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.canvas, -1, 0, 0)
        self.SetSizer(self.sizer)
        self.SetupScrolling()


class MonitorItem(wx.Panel):

    def __init__(self, parent, name, monitors, devices, names) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.name = name
        self.names = names
        self.monitors = monitors
        self.devices = devices
        self.canvas_panel = Canvaspanel(self, self.monitors, self.devices)

        [self.device_id, self.output_id] = self.devices.get_signal_ids(
            self.name)

        self.name_text = wx.StaticText(
            self, wx.ID_ANY, label=self.name, size=(50, 50))
        self.remove_item = wx.Button(self, wx.ID_ANY, "Remove", size=(50, 50))

        self.remove_item.Bind(wx.EVT_BUTTON, self.on_remove_item)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer.Add(self.name_text, 1, wx.ALIGN_CENTER, 0)
        self.sizer.Add(self.canvas_panel, 6, wx.EXPAND, 0)
        self.sizer.Add(self.remove_item, 1, wx.ALIGN_CENTER, 0)
        self.SetSizer(self.sizer)

    def on_remove_item(self, event):
        self.parent.item_list = [
            item for item in self.parent.item_list if item.name != self.name]
        self.parent.parent.side_panel.remove_monitor_combobox.Clear()
        for item in self.parent.item_list:
            self.parent.parent.side_panel.remove_monitor_combobox.Append(
                item.name)
        self.parent.remove_child(self)

    def render(self):
        print(self.devices.get_device(self.device_id).device_kind)
        if self.devices.get_device(self.device_id).device_kind == self.devices.D_TYPE:
            self.values = self.parent.monitors.monitors_dictionary[self.device_id, None]
            self.canvas_panel.canvas.render_value(self.values)
        else:
            self.values = self.parent.monitors.monitors_dictionary[self.device_id, self.output_id]
            self.canvas_panel.canvas.render_value(self.values)


class MenuFrame(wx.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent=None)
        self.parent = parent

        self.Bind(wx.EVT_CLOSE, self.closeWindow)
        self.file_panel = FilePanel(self)
        self.text_editor = TextEditor(self)
        self.error_panel = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_MULTILINE)
        fo = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.text_editor.SetFont(fo)
        self.error_panel.SetFont(fo)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.file_panel, 1, wx.EXPAND, 0)
        main_sizer.Add(self.text_editor, 7, wx.EXPAND, 0)
        main_sizer.Add(self.error_panel, 2, wx.EXPAND, 0)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def closeWindow(self, event):
        sys.exit()


class FilePanel(wx.Panel):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.path = None

        search_file_button = wx.Button(self, wx.ID_ANY, "Search file")
        save_as_button = wx.Button(self, wx.ID_ANY, "Save as")
        gui_button = wx.Button(self, wx.ID_ANY, "Continue to GUI")

        search_file_button.Bind(wx.EVT_BUTTON, self.on_open_file)
        save_as_button.Bind(wx.EVT_BUTTON, self.on_save_file)
        gui_button.Bind(wx.EVT_BUTTON, self.on_gui_button)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(search_file_button, -1, 0, 0)
        main_sizer.Add(save_as_button, -1, 0, 0)
        main_sizer.Add(gui_button, -1, 0, 0)
        self.SetSizer(main_sizer)

    def on_open_file(self, event):
        self.currentDirectory = os.getcwd()
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentDirectory,
            defaultFile="",
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            print("You chose the following file:")
        dlg.Destroy()
        print("Filepath is", path)
        if path is not None:
            print("setting text")
            self.parent.text_editor.set_text(path)
            self.parent.error_panel.SetValue("")
            try:
                """Open and return the file specified by path for reading"""
                with open(path, "r") as f:
                    self.parent.parent.content = f.read()
                    self.parent.parent.file = io.StringIO(
                        self.parent.parent.content)
            except IOError:
                print("error, can't find or open file")
                sys.exit()
            self.path = path

    def on_gui_button(self, event):
        self.parent.parent.show_gui(self.path)

    def on_save_file(self, event):
        self.parent.parent.save_file(self)


class TextEditor(wx.Panel):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.file = None
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE)
        main_sizer.Add(self.text, -1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    def set_text(self, path):
        try:
            """Open and return the file specified by path for reading"""
            with open(path) as f:
                content = f.readlines()
            self.text.SetValue("".join(content))
        except IOError:
            print("error, can't find or open file")
            sys.exit()


class GuiControlPanel(wx.Panel):
    """
    Control panel that handles switching back to menu frame, saving and help button

    Parameters:

    parent: passes an instance of the GUI class

    size: passes size 
    
    Public Methods:

    on_return_button(self, event): event handler for the return_button, shows menu, hides gui

    on_save_file(self, event): event handler for the save_as button, opens save menu

    """
    def __init__(self, parent, size) -> None:
        """Initialises widgets and layout"""
        super().__init__(parent=parent, size=size)

        self.parent = parent
        self.path = None

        self.return_button = wx.Button(self, wx.ID_ANY, "Back to text editor")
        self.save_as_button = wx.Button(self, wx.ID_ANY, "Save as")
        self.help_button = wx.Button(self, wx.ID_ANY, "Help")

        self.return_button.Bind(wx.EVT_BUTTON, self.on_return_button)
        self.save_as_button.Bind(wx.EVT_BUTTON, self.on_save_file)

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.main_sizer.Add(self.return_button, 1, wx.ALL, 5)
        self.main_sizer.Add(self.save_as_button, 1, wx.ALL, 5)
        self.main_sizer.Add(self.help_button, 1, wx.ALL, 5)

        self.SetSizer(self.main_sizer)

    def on_return_button(self, event):
        """Calls the FrameManager show_menu method, hides gui, shows menu"""
        self.parent.parent.show_menu()

    def on_save_file(self, event):
        """Calls the FrameManager save_file method, opens file saving menu"""
        self.parent.parent.save_file(self)


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, parent, title, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        self.parent = parent
        self.Bind(wx.EVT_CLOSE, self.closeWindow)

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        # Canvas for drawing signals
        self.scrolled_panel = Monitor(
            self, self.monitors, self.devices, self.names)
        self.scrolled_panel.SetupScrolling()
        # Control side_panel
        self.side_panel = SidePanel(self, self.scrolled_panel)
        self.gui_control = GuiControlPanel(self, size=(-1, 75))

        # Configure sizers for layout
        self.top_level_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.top_level_sizer.Add(self.gui_control, 1, wx.EXPAND, 0)
        self.top_level_sizer.Add(self.main_sizer, 10, wx.EXPAND, 0)

        self.main_sizer.Add(self.scrolled_panel, 8, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.side_panel, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(self.top_level_sizer)

    def closeWindow(self, event):
        sys.exit()


class FrameManager:
    """
    Manage the two main frames for the GUI and starting menu, including showing and hiding frames
    
    Paramaters:

    title: title of the Logic simulator

    Public methods:

    show_gui(self, path): shows the gui, creates objects for devices, monitors, network

    process_content(self): reads in text_field and passes the text to parser, parsese and handles errors

    show_menu(self): shows menu, hides gui

    save_file(self, button): opens file saving menu

    """
    def __init__(self, title):
        """Launches app, creates MenuFrame"""
        self.title = title
        self.app = wx.App()
        self.menu = MenuFrame(self)
        self.menu.Show()
        self.app.MainLoop()

    def show_gui(self, path):
        self.path = path
        if self.menu.text_editor.text is not None:
            self.names = Names()
            self.devices = Devices(self.names)
            self.network = Network(self.names, self.devices)
            self.monitors = Monitors(self.names, self.devices, self.network)

            self.process_content()

        else:
            print("Please choose a file first!")

    def process_content(self):
        self.content = self.menu.text_editor.text.GetValue()
        self.file = io.StringIO(self.content)
        self.scanner = Scanner(self.path, self.file, self.names)
        self.parser = Parser(
            self.names,
            self.devices,
            self.network,
            self.monitors,
            self.scanner)

        if self.parser.parse_network():
            print("parsing")
            self.gui = Gui(
                self,
                self.title,
                self.names,
                self.devices,
                self.network,
                self.monitors)
            self.menu.Hide()
            self.gui.Show()
            self.gui.path = self.path
        else:
            error = Error.gui_report_error(self.scanner)
            Error.print_error(self.scanner)
            print("Sorry, can't parse network.")
            self.menu.error_panel.SetValue(error)

    def show_menu(self):
        self.menu.Show()
        self.gui.Hide()

    def save_file(self, button):
        self.content = self.menu.text_editor.text.GetValue()
        self.file = io.StringIO(self.content)
        print("content", self.content)
        self.currentDirectory = os.getcwd()
        dlg = wx.FileDialog(
            button, message="Save file as ...",
            defaultDir=self.currentDirectory,
            defaultFile="", style=wx.FD_SAVE
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            print(f"You chose the following filename: {path}")
            with open(path, "w") as file:
                file.write(self.content)
        dlg.Destroy()

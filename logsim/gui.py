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
import wx.lib.scrolledpanel as scrolled
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

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

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
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
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

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

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

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
        self.render(text)

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

    def __init__(self, parent, scrolled_panel)-> None:
        super().__init__(parent=parent)
        
        self.scrolled_panel = scrolled_panel
        for item in self.scrolled_panel.item_list:
            print(item.name)
        # Configure the widgets
        
        #cycle_sizer
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")

        #button_sizer
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        """
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)"""
        
        self.switch_box_text = wx.StaticText(self, wx.ID_ANY, "Set Switch")
        #switch_sizer
        self.switch_box = wx.ComboBox(self, wx.ID_ANY, "Switch")
        self.switch_box_inter_text = wx.StaticText(self, wx.ID_ANY, "set to", style= wx.ALIGN_CENTER)
        self.switch_box_values = wx.ComboBox(self, wx.ID_ANY, "Value", choices = ["0", "1"])

        
        self.monitor_text = wx.StaticText(self, wx.ID_ANY, "Set outputs to monitor")
        #monitor_sizer
        self.monitor_combobox = wx.ComboBox(self, wx.ID_ANY, "Select")
        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")

        
        self.remove_monitor_text = wx.StaticText(self, wx.ID_ANY, "Remove monitor")
        #remove_monitor_sizer
        self.remove_monitor_combobox = wx.ComboBox(self, wx.ID_ANY, "Select", choices = [item.name for item in self.scrolled_panel.item_list])
        self.remove_monitor_button = wx.Button(self, wx.ID_ANY, "Remove")
        self.remove_all_button = wx.Button(self, wx.ID_ANY, "Remove all")
        self.remove_all_button.SetBackgroundColour('#ff1a1a')

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)

        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

        #self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.switch_box.Bind(wx.EVT_COMBOBOX, self.on_combo_select)
        self.switch_box_values.Bind(wx.EVT_COMBOBOX, self.on_combo_select)

        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.remove_monitor_button.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.remove_all_button.Bind(wx.EVT_BUTTON, self.on_remove_all_monitors)
        #self.remove_monitor_combobox.Bind(wx.EVT_COMBOBOX, choices = self.scrolled_panel.item_list)

        #self.remove_monitor_combobox.Add

        self.side_sizer = wx.BoxSizer(wx.VERTICAL)

        self.cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.remove_monitor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.remove_monitor_subsizer = wx.BoxSizer(wx.VERTICAL)
        self.remove_monitor_bordersizer = wx.BoxSizer(wx.VERTICAL)

        self.side_sizer.SetMinSize(self.side_sizer.GetMinSize())
        self.side_sizer.Add(self.cycle_sizer, 1, wx.ALL | wx.EXPAND, 0)
        self.side_sizer.Add(self.button_sizer, 1, wx.ALL |wx.EXPAND, 0)
        self.side_sizer.Add(wx.StaticLine(self,-1), 0, wx.ALL|wx.EXPAND, 5)
        self.side_sizer.Add(self.switch_box_text, 1, wx.ALL | wx.ALIGN_CENTER, 0)
        self.side_sizer.Add(self.switch_sizer, 1, wx.ALL|wx.EXPAND, 0)
        self.side_sizer.Add(wx.StaticLine(self,-1), 0, wx.ALL|wx.EXPAND, 5)
        self.side_sizer.Add(self.monitor_text, 1, wx.ALL | wx.ALIGN_CENTER, 0)
        self.side_sizer.Add(self.monitor_sizer, 1, wx.ALL|wx.EXPAND, 0)
        self.side_sizer.Add(wx.StaticLine(self,-1), 0, wx.ALL|wx.EXPAND, 5)
        self.side_sizer.Add(self.remove_monitor_text, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        self.side_sizer.Add(self.remove_monitor_sizer, 1, wx.ALL|wx.EXPAND, 0)

        self.cycle_sizer.Add(self.text, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        self.cycle_sizer.Add(self.spin, 2, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.button_sizer.Add(self.run_button, 1, wx.ALL | wx.EXPAND, 5)
        self.button_sizer.Add(self.continue_button, 1, wx.ALL | wx.EXPAND, 5)

        self.switch_sizer.Add(self.switch_box, 0, wx.ALL, 5)
        self.switch_sizer.Add(self.switch_box_inter_text, 0, wx.ALL | wx.CENTRE, 5)
        self.switch_sizer.Add(self.switch_box_values, 0, wx.EXPAND | wx.ALL, 5)

        self.monitor_sizer.Add(self.monitor_combobox, 1, wx.ALL, 5)
        self.monitor_sizer.Add(self.add_monitor_button, 1, wx.ALL, 5)

        self.remove_monitor_sizer.Add(self.remove_monitor_bordersizer, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
        self.remove_monitor_sizer.Add(self.remove_monitor_subsizer, 1, wx.ALL, 5)

        self.remove_monitor_bordersizer.Add(self.remove_monitor_combobox, 0, wx.TOP  | wx.BOTTOM | wx.EXPAND, 10)

        self.remove_monitor_subsizer.Add(self.remove_monitor_button, 0, wx.ALL |wx.EXPAND, 5)
        self.remove_monitor_subsizer.Add(self.remove_all_button, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(self.side_sizer)

    def on_add_monitor(self, event):
        """Handle the event when the add monitor button is pressed"""
        self.remove_monitor_combobox.Append("testing")
        self.scrolled_panel.add_monitor("testing")

    def on_remove_monitor(self, event):
        """Handle the event when the remove monitor button is pressed"""
        self.scrolled_panel.remove_monitor("testing")

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

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)
    
    def on_continue_button(self, event):
        """Handle the event triggered by pressing the continue button"""
        text = "Contine button pressed."
        self.canvas.render(text)

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_combo_select(self, event):
        """Handle event from selecting an event from the combobox dropdown menu"""
        self.canvas.render("selected")

class Monitor(scrolled.ScrolledPanel):

    def __init__(self, parent) -> None:

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #self.text_1 = wx.StaticText(self, wx.ID_ANY, "Text1", size = (-1, 50))
        #self.text_2 = wx.StaticText(self, wx.ID_ANY, "Text2", size = (-1, 50))
        #self.text_1.SetBackgroundColour('#b0bcda')
        #self.text_2.SetBackgroundColour('#b0bcda')

        #self.sizer.Add(self.text_1, 0, wx.EXPAND | wx.ALL, 5)
        #self.sizer.Add(self.text_2, 0, wx.EXPAND |wx.ALL, 5)

        self.item_list = []

        self.item_list.append(MonitorItem(self, "text 1"))
        self.item_list.append(MonitorItem(self, "Text 2"))
        self.item_list[0].SetBackgroundColour('#b0bcda')
        self.item_list[1].SetBackgroundColour('#b0bcda')

        self.sizer.Add(self.item_list[0], 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.item_list[1], 0, wx.EXPAND |wx.ALL, 5)

        self.SetSizer(self.sizer)
        self.SetupScrolling()

    def add_monitor(self, text):
        self.item_list.append(MonitorItem(self, text))
        self.item_list[-1].SetBackgroundColour('#b0bcda')
        self.sizer.Add(self.item_list[-1], 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetupScrolling()

    def remove_monitor(self, text):
        for item in self.sizer.GetChildren():
            if (widget :=item.GetWindow()).name is text:
                self.sizer.Hide(widget)
                widget.Destroy()
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetupScrolling()

    def remove_all_monitors(self):
        for item in self.sizer.GetChildren():
            self.sizer.Hide(item.GetWindow())
            item.GetWindow().Destroy()
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetupScrolling()

class MonitorItem(wx.Panel):

    def __init__(self, parent, name) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.name_text = wx.StaticText(self, wx.ID_ANY, label= self.name)
        self.signal_trace = wx.StaticText(self, wx.ID_ANY, "We will add the signal trace here")
        self.remove_item = wx.Button(self, wx.ID_ANY, "Remove")

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizer.Add(self.name_text, 0 , wx.EXPAND | wx.ALL, 0)
        self.sizer.Add(self.signal_trace, 0 , wx.EXPAND | wx.ALL, 0)
        self.sizer.Add(self.remove_item, 0 , wx.EXPAND | wx.ALL, 0)

        self.SetSizer(self.sizer)

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

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        saveMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(saveMenu, "&Save")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.scrolled_panel = Monitor(self)
        self.scrolled_panel.SetupScrolling()
        #self.canvas = MyGLCanvas(self, devices, monitors)
        #Control side_panel
        self.side_panel = SidePanel(self, self.scrolled_panel)


        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self.scrolled_panel, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.side_panel, 1, wx.ALL, 5)


        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)


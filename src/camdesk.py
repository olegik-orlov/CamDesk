#!/usr/bin/env python
'''
Created on 2016.07.03

@author: <a href="mailto:info@olegorlov.com">Oleg Orlov</a>

https://wiki.ubuntu.com/Novacut/GStreamer1.0
https://python-gtk-3-tutorial.readthedocs.io/en/latest/introduction.html
https://www.freedesktop.org/software/gstreamer-sdk/data/docs/2012.5/gst-plugins-base-plugins-0.10/gst-plugins-base-plugins-textoverlay.html
'''

import gi 
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gst, Gdk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
gi.require_version('GstVideo', '1.0')
from gi.repository import GdkX11, GstVideo

class CamDesk(Gtk.Window):
    
    def closeme(self, widget, event) :
        if event.keyval == Gdk.KEY_Escape :
            self.quit(widget)


    def runme(self, widget, event) :
        if event.keyval == Gdk.KEY_F1 :
            self.run()


    def showhidemouse(self, widget, event) :
        if event.keyval == Gdk.KEY_F2 :
            if self.mouse == "Show" :
                self.mouse = "Hide"
                self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR))
            else :
                self.mouse = "Show"
                self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
                

    def pinme(self, widget, event) :
        if event.keyval == Gdk.KEY_F3 :
            self.set_keep_above(not self.pin)
            self.pin = not self.pin


    def flipme(self, widget, event) :
        if event.keyval == Gdk.KEY_F4 :
            self.flip()


    def properties(self, widget, event) :
        if event.keyval == Gdk.KEY_F5 :
            self.win = Gtk.Window(Gtk.WindowType.TOPLEVEL)
            self.win.set_position(Gtk.WindowPosition.CENTER)
            self.win.set_title("Properties")
            self.win.set_size_request(250, 120)
            self.win.set_resizable(False)
            self.win.set_keep_above(True)
            self.win.set_property('skip-taskbar-hint', True)
            self.win.connect("destroy", self.closeproperties)
            vbox = Gtk.VBox(spacing = 4)
            hbox = Gtk.HBox(spacing = 4)
            hbox2 = Gtk.HBox(spacing = 4)
            
            check = Gtk.CheckButton("Pin")
            check.set_active(self.pin)
            check.set_size_request(50, 35)
            check.connect("clicked", self.pinning)
            hbox.pack_start(check, False, False, 10)
            
            scale = Gtk.HScale()
            scale.set_range(1, 100)
            scale.set_value(self.scale)
            scale.set_size_request(200, 35)
            scale.connect("value-changed", self.opacity_slider)
            
            hbox.pack_start(scale, True, True, 10)
            
            self.widthSpinbutton = Gtk.SpinButton()
            self.widthSpinbutton.set_adjustment(Gtk.Adjustment(0, 0, 1920, 1, 10, 0))
            self.widthSpinbutton.set_value(640)
            hbox2.pack_start(self.widthSpinbutton, True, True, 10)
            self.widthSpinbutton.connect("value-changed", self.change_size)
            
            self.heigthSpinbutton = Gtk.SpinButton()
            self.heigthSpinbutton.set_adjustment(Gtk.Adjustment(0, 0, 1080, 1, 10, 0))
            self.heigthSpinbutton.set_value(360)
            hbox2.pack_start(self.heigthSpinbutton, True, True, 10)
            self.heigthSpinbutton.connect("value-changed", self.change_size)
            
            vbox.pack_start(hbox, True, True, 10)
            vbox.pack_start(hbox2, True, True, 10)
            
            self.win.add(vbox)
            self.win.show_all()


    def pinning(self, checkbox) :
        if checkbox.get_active() :
            self.set_keep_above(True)
            self.pin = True
        else :
            self.set_keep_above(False)
            self.pin = False


    def opacity_slider(self, w) :
        self.scale = w.get_value()
        self.set_opacity(self.scale / 100.0)


    def change_size(self, w) :
        width = int(self.widthSpinbutton.get_value())
        height = int(self.heigthSpinbutton.get_value())
        self.set_size_request(width, height)


    def closeproperties(self, w) :
        self.win.hide()
        

    def flip(self) :

        self.show_all()
        self.xid = self.movie_window.get_property('window').get_xid()
        self.player.set_state(Gst.State.NULL)

        if self.startcam == "Stop":
            if self.flipcam == True:
                self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! aspectratiocrop aspect-ratio=16/9 ! autovideosink")
                self.flipcam = False
            else:
                self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! aspectratiocrop aspect-ratio=16/9 ! videoflip method=horizontal-flip ! autovideosink")
                self.flipcam = True

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        self.player.set_state(Gst.State.PLAYING)
        
        
    def run(self) :

        self.show_all()
        self.xid = self.movie_window.get_property('window').get_xid()
        self.player.set_state(Gst.State.NULL)

        if self.startcam == "Start":
            if self.flipcam == True:
                self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! aspectratiocrop aspect-ratio=16/9 ! videoflip method=horizontal-flip ! autovideosink")
            else:
                self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! aspectratiocrop aspect-ratio=16/9 ! autovideosink")

#             Set up the gstreamer pipeline
#             self.player = Gst.parse_launch("v4l2src ! autovideosink")
#             self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! autovideosink")
#             self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! video/x-raw-yuv,width=320,height=240,framerate=30/1 ! autovideosink")
#             self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! video/x-raw-yuv,width=320,height=240,framerate=30/1 ! textoverlay font-desc=\"Sans 20\" text=\"Microsoft LifeCam NX-3000\" valign=top halign=left shaded-background=true ! timeoverlay halign=right valign=bottom font-desc=\"Sans 20\" ! clockoverlay halign=left valign=bottom text=\"\" time-format=\"%d.%m.%Y  %H:%M:%S \" font-desc=\"Sans 20\" ! autovideosink")
#             self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! autovideosink")
#             self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! aspectratiocrop aspect-ratio=16/9 ! textoverlay valignment=bottom xpad=450 ypad=25 color=4278255360 font-desc=\"Sans 20\" text=\"Microsoft LifeCam NX-3000\" shaded-background=true ! timeoverlay halignment=right color=4278255360 font-desc=\"Sans 20\" ! clockoverlay color=4278255360 text=\"\" time-format=\"%d.%m.%Y  %H:%M:%S \" font-desc=\"Sans 20\" ! autovideosink")
#             self.player = Gst.parse_launch("v4l2src device=\"/dev/video1\" ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! aspectratiocrop aspect-ratio=16/9 ! videoflip method=horizontal-flip ! autovideosink")
            self.startcam ="Stop"
        else:
            self.player = Gst.parse_launch("videotestsrc ! video/x-raw,width=640,height=480,framerate=30/1 ! aspectratiocrop aspect-ratio=16/9 ! autovideosink")
#             self.player = Gst.parse_launch("videotestsrc ! autovideosink")
            self.startcam = "Start"

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        self.player.set_state(Gst.State.PLAYING)
        
        
    def quit(self, w) :
        self.player.set_state(Gst.State.NULL)
        Gtk.main_quit()
        

    def __init__(self) :
        super(CamDesk, self).__init__()

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title("CamDesk")
        self.set_decorated(False)

#         aspect-ratio=16/9
#         self.set_size_request(400, 225)
#         self.set_size_request(533, 300)
#         self.set_size_request(560, 315)
        self.set_size_request(640, 360)
#         self.set_size_request(853, 480)
#         self.set_size_request(1280, 720)

#         aspect-ratio=4/3
#         self.set_size_request(320, 240)
#         self.set_size_request(640, 480)
#         self.set_size_request(533, 400)
#         self.set_size_request(640, 480)
#         self.set_size_request(640, 360)

        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_default_icon_from_file('logo.png')
        self.connect("destroy", self.quit)
        self.connect("key-press-event", self.closeme)
        self.connect("key-press-event", self.runme)
        self.connect("key-press-event", self.flipme)
        self.connect("key-press-event", self.showhidemouse)
        self.connect("key-press-event", self.pinme)
        self.connect("key-press-event", self.properties)

#         color = Gdk.color_parse("#f2f1f0")
#         rgba = Gdk.RGBA.from_color(color)
#         self.movie_window = Gtk.DrawingArea()
#         self.movie_window.override_background_color(0, rgba)
#         self.add(self.movie_window)
        
        vbox = Gtk.VBox()
        self.add(vbox)
        self.movie_window = Gtk.DrawingArea()
        vbox.pack_start(self.movie_window, True, True, 0)

        self.player = Gst.Pipeline()

#         Presets on load
        self.startcam = "Stop"
        self.flipcam = True
        self.mouse = "Show"
        self.scale = 100
        self.pin = True


    def on_message(self, bus, message) :
        t = message.type
        if t == Gst.MessageType.EOS :
            self.player.set_state(Gst.State.NULL)
            self.startcam = "Start"
        elif t == Gst.MessageType.ERROR :
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)
            self.startcam ="Start"


    def on_sync_message(self, bus, message) :
        if message.get_structure() is None :
            return
        if message.get_structure().get_name() == "prepare-window-handle" :
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.xid)


Gdk.threads_init()
Gst.init(None)
camDesk = CamDesk()
camDesk.run()
Gtk.main()

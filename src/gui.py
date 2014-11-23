#!/usr/bin/python
from gi.repository import Gtk
import ConfigParser
import dnf
import sys
from types import NoneType

class Handler:
    def btn_save(self, grid):
        config = ConfigParser.RawConfigParser()
        config.add_section("main")
        i = 0
        while type(grid.get_child_at(1, i)) != NoneType:
            label = grid.get_child_at(0, i).get_text()
            widget = grid.get_child_at(1, i)
            if type(widget) == Gtk.Switch:
                val = widget.get_active()
            elif type(widget) == Gtk.Scale or type(widget) == Gtk.SpinButton:
                val = int(widget.get_value())
            elif type(widget) == Gtk.Entry:
                val = widget.get_text()
            config.set("main", label, val)
            i += 1
        with open("dnf.conf", "wb") as configfile:
            config.write(configfile)


class DnfConfWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="DNF configuration manager", application=app)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("gui.ui")
        self.builder.connect_signals(Handler())
        self.window = self.builder.get_object("window1")

        base = dnf.Base()
        base.conf.read()
        self.dnf_conf = base.conf

        self.builder.get_object("best_sw").set_active(self.dnf_conf.best)
        self.builder.get_object("clean_requirements_on_remove_sw").set_active(self.dnf_conf.clean_requirements_on_remove)
        self.builder.get_object("debuglevel_adj").set_value(self.dnf_conf.debuglevel)
        self.builder.get_object("installonly_limit_spin").set_value(self.dnf_conf.installonly_limit)
        self.builder.get_object("keepcache_sw").set_active(self.dnf_conf.keepcache)
        self.builder.get_object("gpgcheck_sw").set_active(self.dnf_conf.gpgcheck)
        self.window.show()


class DnfConfApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = DnfConfWindow(self)
        win.window.show()

    def do_startup(self):
        Gtk.Application.do_startup(self)


app = DnfConfApplication()
exit_status = app.run(None)
sys.exit(exit_status)
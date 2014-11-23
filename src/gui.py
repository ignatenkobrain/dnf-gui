#!/usr/bin/python
from gi.repository import Gtk
import ConfigParser
import dnf
import sys
from types import NoneType


class DnfGuiApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        Gtk.Application.do_startup(self)
        self.main_window.show()
        Gtk.main()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("gui.ui")
        self.builder.connect_signals(self)
        self.main_window = self.builder.get_object("main_window")
        self.conf_window = self.builder.get_object("conf_window")

        base = dnf.Base()
        base.conf.read()
        self.dnf_conf = base.conf
        base.read_all_repos()
        from platform import machine
        cachedir = "/var/cache/dnf/{}/{}".format(machine(), dnf.rpm.detect_releasever("/"))
        self.dnf_conf.cachedir = cachedir
        for repo in base.repos.values():
            repo.basecachedir = cachedir
            repo.md_only_cached = True
        base.fill_sack()
        pkgs = base.sack.query().installed()
        for pkg in pkgs:
            to_ins = Gtk.Box()
            to_ins.pack_start(Gtk.Label(pkg.name), True, False, 0)
            to_ins.pack_end(Gtk.Button("Remove"), True, False, 0)
            self.builder.get_object("listbox1").insert(to_ins, -1)
        self.builder.get_object("listbox1").show_all()

    def on_main_window_destroy(self, window, event):
        Gtk.main_quit()

    def on_conf_window_delete_event(self, window, event):
        window.destroy()

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

    def btn_settings(self, widget):
        self.builder.get_object("best_sw").set_active(self.dnf_conf.best)
        self.builder.get_object("clean_requirements_on_remove_sw").set_active(self.dnf_conf.clean_requirements_on_remove)
        self.builder.get_object("debuglevel_adj").set_value(self.dnf_conf.debuglevel)
        self.builder.get_object("installonly_limit_spin").set_value(self.dnf_conf.installonly_limit)
        self.builder.get_object("keepcache_sw").set_active(self.dnf_conf.keepcache)
        self.builder.get_object("gpgcheck_sw").set_active(self.dnf_conf.gpgcheck)
        self.conf_window.show()

app = DnfGuiApplication()
exit_status = app.run(None)
sys.exit(exit_status)
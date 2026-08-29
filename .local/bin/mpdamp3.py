#!/usr/bin/env python3
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

try:
    from mpd import MPDClient
except ImportError:
    print('mpdamp: missing python3-mpd (Debian package: python3-mpd)', file=sys.stderr)
    raise SystemExit(2)

APP_VERSION = 'MPD⚡AMP 0.1-alpha-v16'
SOCKET = os.environ.get('MPD_SOCKET') or os.path.join(
    os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'), 'mpd', 'socket'
)
MUSIC_ROOT = os.environ.get('MPD_MUSIC_DIR', '/mnt/data/music')

THEMES = {
    'light': {
        'bg': '#e6e2dc', 'panel': '#f0ede8', 'panel2': '#ddd8d0',
        'text': '#292824', 'muted': '#706c65', 'accent': '#586b91',
        'accent2': '#7d6a52', 'list': '#faf8f4', 'select': '#6b7ea6',
        'select_text': '#ffffff', 'border': '#c6c0b7',
        'progress_fill': '#5f739f', 'progress_rest': '#c9c3ba',
        'volume_fill': '#6f7d65', 'volume_rest': '#c9c3ba',
        'status': '#5e625e', 'error': '#9a514c', 'button': '#d8d3ca',
        'button_active': '#c5beb4', 'display': '#262b26', 'display_text': '#c9e1a4',
    },
    'dark': {
        'bg': '#272522', 'panel': '#302e2a', 'panel2': '#3a3732',
        'text': '#e0ddd7', 'muted': '#a49f96', 'accent': '#8295bd',
        'accent2': '#b0926c', 'list': '#211f1c', 'select': '#56688e',
        'select_text': '#ffffff', 'border': '#4b4740',
        'progress_fill': '#8295bd', 'progress_rest': '#4a4640',
        'volume_fill': '#91a080', 'volume_rest': '#4a4640',
        'status': '#aaa59b', 'error': '#d08076', 'button': '#3b3833',
        'button_active': '#4a4640', 'display': '#181a18', 'display_text': '#c8e6a0',
    }
}


def fmt_time(seconds):
    try:
        sec = max(0, int(float(seconds)))
    except Exception:
        sec = 0
    return f'{sec // 60:02d}:{sec % 60:02d}'


def fmt_duration(seconds):
    try:
        sec = max(0, int(float(seconds)))
    except Exception:
        return '--:--'
    return fmt_time(sec)


def codec_from_song(song):
    fmt = (song.get('format') or '').strip()
    if fmt:
        parts = fmt.split(':')
        # MPD format is sample-rate:bits:channels; codec is not normally there.
    path = song.get('file', '')
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    return {'oga': 'OGG', 'ogg': 'OGG', 'opus': 'OPUS', 'mp3': 'MP3',
            'flac': 'FLAC', 'wav': 'WAV', 'm4a': 'AAC', 'aac': 'AAC',
            'ape': 'APE', 'wv': 'WAVPACK'}.get(ext, ext.upper() if ext else 'AUDIO')


class MPDCallPool:
    """Small worker pool. No MPD I/O is performed in Tk's main thread."""
    def __init__(self, socket_path, result_cb, error_cb):
        self.socket_path = socket_path
        self.result_cb = result_cb
        self.error_cb = error_cb
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix='mpdamp')
        self.closed = False

    def submit(self, method, *args, tag=None, **kwargs):
        if self.closed:
            return
        fut = self.pool.submit(self._call, method, args, kwargs)
        fut.add_done_callback(lambda f: self._done(f, tag))

    def _call(self, method, args, kwargs):
        c = MPDClient()
        c.timeout = 4
        c.idletimeout = None
        try:
            c.connect(self.socket_path)
            if method == '__load_playlist_replace':
                c.clear(); return c.load(*args, **kwargs)
            return getattr(c, method)(*args, **kwargs)
        finally:
            try:
                c.close(); c.disconnect()
            except Exception:
                pass

    def _done(self, future, tag):
        try:
            result = future.result()
            self.result_cb(tag, result)
        except Exception as exc:
            self.error_cb(tag, exc)

    def close(self):
        self.closed = True
        self.pool.shutdown(wait=False, cancel_futures=True)


class IdleWatcher(threading.Thread):
    def __init__(self, socket_path, notify):
        super().__init__(daemon=True)
        self.socket_path = socket_path
        self.notify = notify
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            c = MPDClient()
            c.timeout = 5
            c.idletimeout = None
            try:
                c.connect(self.socket_path)
                while not self.stop_event.is_set():
                    changed = c.idle('player', 'playlist', 'database', 'options')
                    if changed:
                        self.notify(changed)
            except Exception:
                if not self.stop_event.is_set():
                    time.sleep(1)
            finally:
                try: c.close(); c.disconnect()
                except Exception: pass

    def stop(self):
        self.stop_event.set()


class Bar(tk.Canvas):
    def __init__(self, master, height=9, filled='#668', rest='#444', command=None, **kw):
        super().__init__(master, height=height, bd=0, highlightthickness=0,
                         bg=kw.pop('bg', master.cget('bg')), **kw)
        self.filled = filled
        self.rest = rest
        self.value = 0.0
        self.command = command
        self.dragging = False
        self.bind('<Button-1>', self._press)
        self.bind('<B1-Motion>', self._motion)
        self.bind('<ButtonRelease-1>', self._release)
        self.bind('<Enter>', lambda e: self.configure(cursor='hand2'))
        self.bind('<Leave>', lambda e: self.configure(cursor=''))
        self.bind('<Configure>', lambda e: self._draw())

    def set_colors(self, filled, rest):
        self.filled, self.rest = filled, rest
        self._draw()

    def set(self, value):
        self.value = max(0.0, min(1.0, float(value or 0)))
        self._draw()

    def _fraction(self, x):
        w = max(1, self.winfo_width())
        return max(0.0, min(1.0, x / w))

    def _press(self, e):
        self.dragging = True
        f = self._fraction(e.x)
        self.set(f)
        if self.command: self.command(f, True)

    def _motion(self, e):
        if self.dragging:
            f = self._fraction(e.x)
            self.set(f)
            if self.command: self.command(f, True)

    def _release(self, e):
        if self.dragging:
            self.dragging = False
            f = self._fraction(e.x)
            self.set(f)
            if self.command: self.command(f, False)

    def _draw(self):
        self.delete('all')
        w, h = max(1, self.winfo_width()), max(1, self.winfo_height())
        self.create_rectangle(0, 0, w, h, outline='', fill=self.rest)
        self.create_rectangle(0, 0, int(w * self.value), h, outline='', fill=self.filled)


class MPDAmp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('mpdamp')
        # No external image/icon assets: mpdamp.py is self-contained.
        self.geometry('900x610')
        self.minsize(700, 480)
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.theme_name = 'dark'
        self.t = THEMES[self.theme_name]
        self.configure(bg=self.t['bg'])

        self.executor = MPDCallPool(SOCKET, self.on_result_thread, self.on_error_thread)
        self.idle = IdleWatcher(SOCKET, self.on_mpd_change)
        self.last_status = {}
        self.current = {}
        self.queue = []
        self.seek_drag = False
        self.volume_drag = False
        self.pending_volume = None
        self.pending_seek = None
        self.muted = False
        self.saved_volume = 90
        self.current_tab = 'PLAYING / QUEUE'
        self.time_remaining = False
        self.pending_volume_time = 0.0
        self.playlists = []
        self.playlist_rows = []
        self.db_path = '/'
        self.db_mode = 'dirs'
        self.search_results_data = []
        self.queue_rows = []
        self.db_rows = []
        self.search_rows = []
        self.font_family = self.find_nerd_font()
        self.icon_family = self.find_icon_font()
        self.font_normal = (self.font_family, 10)
        self.font_small = (self.font_family, 9)
        self.font_tiny = (self.font_family, 8)
        self.font_bold = (self.font_family, 10, 'bold')
        self.display_font = self.find_display_font()

        self.build()
        self.apply_theme()
        self.connect_mpd()
        self.idle.start()
        self._status_poll_inflight = False
        self.after(250, self.clock_tick)
        self.after(300, self.initial_refresh)

    def find_icon_font(self):
        families=set(tkfont.families(self))
        for name in ('Font Awesome 6 Free', 'Font Awesome 5 Free', 'Font Awesome 6 Free Solid', 'Font Awesome 5 Free Solid'):
            if name in families: return name
        return None

    def find_nerd_font(self):
        families = set(tkfont.families(self))
        for name in ('JetBrainsMono Nerd Font Propo', 'JetBrainsMono Nerd Font', 'JetBrains Mono'):
            if name in families:
                return name
        return 'TkFixedFont'

    def find_display_font(self):
        families = set(tkfont.families(self))
        for name in ('Noto Sans Black', 'Noto Sans', 'DejaVu Sans'):
            if name in families:
                return name
        return 'TkDefaultFont'

    def build(self):
        self.main = tk.Frame(self, bd=0)
        self.main.pack(fill='both', expand=True)

        self.top = tk.Frame(self.main, bd=0)
        self.top.pack(fill='x', padx=12, pady=(12, 5))

        # Compact Winamp-inspired display. No image assets: just text + time.
        self.display = tk.Frame(self.top, width=110, height=64, bd=1, relief='flat')
        self.display.pack(side='left', fill='y')
        self.display.pack_propagate(False)
        self.logo_btn = tk.Button(self.display, text='MPD⚡AMP', command=self.show_info,
                                  relief='flat', bd=0, padx=0, pady=0,
                                  font=(self.display_font, 14, 'bold'))
        self.logo_btn.pack(anchor='center', pady=(3,1))
        # Compact time display: labels use the same size as the album text.
        self.elapsed_label = tk.Label(self.display, text='elapsed', font=self.font_small,
                                      justify='center', anchor='center')
        self.elapsed_label.pack(fill='x')
        self.time_label = tk.Label(self.display, text='00:00', font=(self.font_family, 16, 'bold'),
                                   cursor='hand2', justify='center', anchor='center')
        self.time_label.pack(fill='x')
        self.time_label.bind('<Button-1>', lambda e: self.toggle_time_mode())
        self.total_name_label = tk.Label(self.display, text='total', font=self.font_small,
                                         justify='center', anchor='center')
        self.total_name_label.pack(fill='x')
        self.total_label = tk.Label(self.display, text='--:--', font=(self.font_family, 16, 'bold'),
                                    justify='center', anchor='center')
        self.total_label.pack(fill='x')

        self.info = tk.Frame(self.top, bd=0)
        self.info.pack(side='left', fill='both', expand=True, padx=(10,0))
        self.song_label = tk.Label(self.info, text='mpdamp', anchor='w', font=(self.font_family, 15, 'bold'))
        self.song_label.pack(fill='x')
        self.artist_label = tk.Label(self.info, text='MPD disconnected', anchor='w', font=self.font_normal)
        self.artist_label.pack(fill='x', pady=(1,0))
        self.album_label = tk.Label(self.info, text='', anchor='w', font=self.font_small)
        self.album_label.pack(fill='x')
        self.format_label = tk.Label(self.info, text='', anchor='w', font=self.font_tiny)
        self.format_label.pack(fill='x', pady=(3,3))
        self.seekbar = Bar(self.info, height=10, command=self.seek_bar_command)
        self.seekbar.pack(fill='x', pady=(4,7))

        self.controls = tk.Frame(self.info, bd=0)
        self.controls.pack(fill='x')
        self.buttons = {}
        # Keep transport glyphs intentionally boring and portable. The Nerd Font is used
        # elsewhere, but these controls should render consistently on any Tk installation.
        if self.icon_family:
            specs = [
                ('prev','\uf048',self.prev), ('playpause','\uf04b',self.playpause), ('stop','\uf04d',self.stop),
                ('next','\uf051',self.next), ('random','\uf074',self.toggle_random), ('repeat','\uf01e',self.toggle_repeat),
                ('single','1',self.toggle_single), ('consume','\uf1b8',self.toggle_consume)
            ]
            transport_font=(self.icon_family,10,'normal')
        else:
            specs = [
                ('prev','⏮',self.prev), ('playpause','▶',self.playpause), ('stop','■',self.stop),
                ('next','⏭',self.next), ('random','🔀',self.toggle_random), ('repeat','🔁',self.toggle_repeat),
                ('single','1',self.toggle_single), ('consume','♻',self.toggle_consume)
            ]
            transport_font=('DejaVu Sans',10,'bold')
        transport_font = ('DejaVu Sans', 10, 'bold')
        for key, text, cmd in specs:
            b = tk.Button(self.controls, text=text, command=cmd, relief='flat', bd=0,
                          font=transport_font, width=3 if key in ('prev','playpause','stop','next') else 4,
                          padx=4, pady=4)
            b.pack(side='left', padx=(0,3))
            self.buttons[key] = b
        self.mute_btn = tk.Button(self.controls, text='VOL', command=self.toggle_mute, relief='flat', bd=0,
                                  font=(self.font_family, 9, 'bold'), padx=5, pady=3)
        self.mute_btn.pack(side='left', padx=(10,4))
        self.volbar = Bar(self.controls, height=8, command=self.volume_bar_command)
        self.volbar.pack(side='left', fill='x', expand=True, padx=(0,6))
        self.volbar.bind('<MouseWheel>', self.volume_wheel)
        self.volbar.bind('<Button-4>', self.volume_wheel)
        self.volbar.bind('<Button-5>', self.volume_wheel)

        self.tabbar = tk.Frame(self.main, bd=0)
        self.tabbar.pack(fill='x', padx=12, pady=(5,0))
        self.tabs = {}
        tab_icons = {'PLAYING / QUEUE':'\uf001','DATABASE':'\uf1c0','BROWSE: /':'\uf120','SEARCH':'\uf002','PLAYLISTS':'\uf03a'}
        for name in ('PLAYING / QUEUE','DATABASE','BROWSE: /','SEARCH','PLAYLISTS'):
            label = (tab_icons[name] + ' ' + name) if self.icon_family else name
            b = tk.Button(self.tabbar, text=label, command=lambda n=name:self.show_tab(n), relief='flat', bd=0,
                          font=(self.font_family, 9, 'bold'), padx=11, pady=5)
            b.pack(side='left', padx=(0,2))
            self.tabs[name] = b

        self.content = tk.Frame(self.main, bd=0)
        self.content.pack(fill='both', expand=True, padx=12, pady=(0,7))
        self.build_queue()
        self.build_database()
        self.build_browse()
        self.build_search()
        self.build_playlists()

        self.status = tk.Frame(self.main, bd=0)
        self.status.pack(fill='x', padx=12, pady=(0,7))
        self.status_song = tk.Label(self.status, text='MPD', anchor='w', font=self.font_tiny)
        self.status_song.pack(side='left', fill='x', expand=True)
        self.status_pos = tk.Label(self.status, text='#--/--', anchor='w', font=self.font_tiny)
        self.status_pos.pack(side='left', padx=10)
        self.status_total = tk.Label(self.status, text='0:00:00', anchor='w', font=self.font_tiny)
        self.status_total.pack(side='left', padx=(0,10))
        self.clear_queue_btn = tk.Button(self.status, text=('\uf1f8 CLEAR QUEUE' if self.icon_family else 'CLEAR QUEUE'), command=self.clear_queue, relief='flat', bd=0, font=self.font_tiny, padx=5)
        self.clear_queue_btn.pack(side='left', padx=(0,10))
        self.status_msg = tk.Label(self.status, text='', anchor='e', font=self.font_tiny)
        self.status_msg.pack(side='left', fill='x', expand=True)
        self.theme_btn = tk.Button(self.status, text='☾', command=self.toggle_theme, relief='flat', bd=0, font=self.font_tiny, padx=5)
        self.theme_btn.pack(side='right')

        self.show_tab(self.current_tab)

    def build_queue(self):
        self.queue_frame = tk.Frame(self.content, bd=0)
        self.queue_filter = tk.Entry(self.queue_frame, font=self.font_small, bd=0)
        self.queue_filter.pack(fill='x', pady=(0,5))
        self.queue_filter.insert(0, '')
        self.queue_filter.bind('<KeyRelease>', lambda e:self.render_queue())
        holder = tk.Frame(self.queue_frame, bd=0)
        holder.pack(fill='both', expand=True)
        cols = ('#','artist','album','song')
        self.queue_tree = ttk.Treeview(holder, columns=cols, show='headings', selectmode='extended')
        headings = {'#':'#','artist':'ARTIST','album':'ALBUM','song':'SONG'}
        for c in cols:
            self.queue_tree.heading(c, text=headings[c])
        self.queue_tree.column('#', width=55, anchor='e', stretch=False)
        self.queue_tree.column('artist', width=180, anchor='w')
        self.queue_tree.column('album', width=180, anchor='w')
        self.queue_tree.column('song', width=300, anchor='w')
        sy = ttk.Scrollbar(holder, orient='vertical', command=self.queue_tree.yview)
        sx = ttk.Scrollbar(holder, orient='horizontal', command=self.queue_tree.xview)
        self.queue_tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.queue_tree.grid(row=0,column=0,sticky='nsew'); sy.grid(row=0,column=1,sticky='ns'); sx.grid(row=1,column=0,sticky='ew')
        holder.rowconfigure(0,weight=1); holder.columnconfigure(0,weight=1)
        self.queue_tree.bind('<Double-1>', self.queue_double)
        self.queue_tree.bind('<Delete>', self.queue_delete)
        self.queue_tree.bind('<Home>', lambda e: self.queue_tree.yview_moveto(0))
        self.queue_tree.bind('<End>', lambda e: self.queue_tree.yview_moveto(1))

    def build_database(self):
        self.db_frame = tk.Frame(self.content, bd=0)
        top = tk.Frame(self.db_frame, bd=0); top.pack(fill='x', pady=(0,5))
        self.db_path_label = tk.Label(top, text='Browse database: /', anchor='w', font=self.font_small)
        self.db_path_label.pack(side='left', fill='x', expand=True)
        tk.Button(top,text=('\uf019 UPDATE DATABASE' if self.icon_family else 'UPDATE DATABASE'),command=self.update_database,relief='flat',bd=0,font=self.font_tiny).pack(side='right')
        self.db_holder = tk.Frame(self.db_frame, bd=0); self.db_holder.pack(fill='both',expand=True)
        cols=('name','type','artist','album','song')
        self.db_tree=ttk.Treeview(self.db_holder,columns=cols,show='headings',selectmode='extended')
        for c,h in zip(cols,('NAME','TYPE','ARTIST','ALBUM','SONG')): self.db_tree.heading(c,text=h)
        self.db_tree.column('name',width=260); self.db_tree.column('type',width=90,stretch=False); self.db_tree.column('artist',width=180); self.db_tree.column('album',width=180); self.db_tree.column('song',width=240)
        sy=ttk.Scrollbar(self.db_holder,orient='vertical',command=self.db_tree.yview); sx=ttk.Scrollbar(self.db_holder,orient='horizontal',command=self.db_tree.xview)
        self.db_tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        self.db_tree.grid(row=0,column=0,sticky='nsew'); sy.grid(row=0,column=1,sticky='ns'); sx.grid(row=1,column=0,sticky='ew')
        self.db_holder.rowconfigure(0,weight=1); self.db_holder.columnconfigure(0,weight=1)
        self.db_tree.bind('<Double-1>',self.db_double)
        self.db_actions=tk.Frame(self.db_frame,bd=0); self.db_actions.pack(fill='x',pady=(5,0))
        tk.Button(self.db_actions,text=('\uf060 BACK' if self.icon_family else 'BACK'),command=self.db_back,relief='flat',bd=0,font=self.font_tiny).pack(side='left')
        tk.Button(self.db_actions,text=('\uf03a ADD SELECTED' if self.icon_family else 'ADD SELECTED'),command=self.db_add_selected,relief='flat',bd=0,font=self.font_tiny).pack(side='right',padx=(4,0))
        tk.Button(self.db_actions,text=('\uf03a ADD ALL SHOWN' if self.icon_family else 'ADD ALL SHOWN'),command=self.db_add_all,relief='flat',bd=0,font=self.font_tiny).pack(side='right')

    def build_browse(self):
        self.browse_frame=tk.Frame(self.content,bd=0)
        top=tk.Frame(self.browse_frame,bd=0); top.pack(fill='x',pady=(0,5))
        self.browse_path=tk.Label(top,text='Browse: /',anchor='w',font=self.font_small); self.browse_path.pack(side='left',fill='x',expand=True)
        self.browse_tree=tk.Listbox(self.browse_frame,selectmode='extended',bd=0,highlightthickness=0,font=self.font_normal)
        self.browse_tree.pack(fill='both',expand=True)
        self.browse_tree.bind('<Double-1>',self.browse_double)
        bottom=tk.Frame(self.browse_frame,bd=0); bottom.pack(fill='x',pady=(5,0))
        tk.Button(bottom,text=('\uf060 BACK' if self.icon_family else 'BACK'),command=self.browse_back,relief='flat',bd=0,font=self.font_tiny).pack(side='left')
        tk.Button(bottom,text=('\uf03a ADD SELECTED' if self.icon_family else 'ADD SELECTED'),command=self.browse_add_selected,relief='flat',bd=0,font=self.font_tiny).pack(side='right')

    def build_search(self):
        self.search_frame=tk.Frame(self.content,bd=0)
        top=tk.Frame(self.search_frame,bd=0); top.pack(fill='x',pady=(0,5))
        self.search_entry=tk.Entry(top,font=self.font_small,bd=0); self.search_entry.pack(side='left',fill='x',expand=True)
        self.search_entry.bind('<Return>',lambda e:self.do_search())
        tk.Button(top,text='SEARCH',command=self.do_search,relief='flat',bd=0,font=self.font_tiny).pack(side='right',padx=(5,0))
        holder=tk.Frame(self.search_frame,bd=0); holder.pack(fill='both',expand=True)
        cols=('artist','album','song')
        self.search_tree=ttk.Treeview(holder,columns=cols,show='headings',selectmode='extended')
        for c,h in zip(cols,('ARTIST','ALBUM','SONG')): self.search_tree.heading(c,text=h)
        self.search_tree.column('artist',width=210); self.search_tree.column('album',width=210); self.search_tree.column('song',width=320)
        sy=ttk.Scrollbar(holder,orient='vertical',command=self.search_tree.yview); sx=ttk.Scrollbar(holder,orient='horizontal',command=self.search_tree.xview)
        self.search_tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        self.search_tree.grid(row=0,column=0,sticky='nsew'); sy.grid(row=0,column=1,sticky='ns'); sx.grid(row=1,column=0,sticky='ew')
        holder.rowconfigure(0,weight=1); holder.columnconfigure(0,weight=1)
        self.search_tree.bind('<Double-1>',self.search_double)
        bottom=tk.Frame(self.search_frame,bd=0); bottom.pack(fill='x',pady=(5,0))
        tk.Button(bottom,text=('\uf03a ADD SELECTED' if self.icon_family else 'ADD SELECTED'),command=self.search_add_selected,relief='flat',bd=0,font=self.font_tiny).pack(side='right',padx=(4,0))
        tk.Button(bottom,text=('\uf03a ADD ALL SHOWN' if self.icon_family else 'ADD ALL SHOWN'),command=self.search_add_all,relief='flat',bd=0,font=self.font_tiny).pack(side='right')

    def style_ttk(self):
        style=ttk.Style(self)
        try: style.theme_use('clam')
        except Exception: pass
        style.configure('Treeview',background=self.t['list'],fieldbackground=self.t['list'],foreground=self.t['text'],rowheight=23,borderwidth=0,font=self.font_small)
        style.map('Treeview',background=[('selected',self.t['select'])],foreground=[('selected',self.t['select_text'])])
        style.configure('Treeview.Heading',background=self.t['panel2'],foreground=self.t['text'],relief='flat',font=self.font_tiny)
        style.map('Treeview.Heading',background=[('active',self.t['button_active'])])
        style.configure('Horizontal.TScrollbar',background=self.t['panel2'],troughcolor=self.t['panel'],arrowcolor=self.t['text'])
        style.configure('Vertical.TScrollbar',background=self.t['panel2'],troughcolor=self.t['panel'],arrowcolor=self.t['text'])

    def apply_theme(self):
        self.t=THEMES[self.theme_name]; self.configure(bg=self.t['bg']); self.style_ttk()
        def walk(w):
            for child in w.winfo_children():
                cls=child.winfo_class()
                try:
                    if cls=='Frame': child.configure(bg=self.t['panel'] if child in (self.top,self.tabbar,self.status,self.controls,self.info,self.db_actions,self.playlist_actions) else self.t['bg'])
                    elif cls=='Label': child.configure(bg=self.t['panel'],fg=self.t['text'])
                    elif cls=='Button': child.configure(bg=self.t['button'],fg=self.t['text'],activebackground=self.t['button_active'],activeforeground=self.t['text'])
                    elif cls=='Entry': child.configure(bg=self.t['list'],fg=self.t['text'],insertbackground=self.t['text'])
                except Exception: pass
                walk(child)
        self.main.configure(bg=self.t['bg']); self.display.configure(bg=self.t['display']); self.logo_btn.configure(bg=self.t['display'],fg=self.t['display_text'],activebackground=self.t['display'])
        self.elapsed_label.configure(bg=self.t['display'],fg=self.t['display_text']); self.time_label.configure(bg=self.t['display'],fg=self.t['display_text'])
        self.total_name_label.configure(bg=self.t['display'],fg=self.t['display_text']); self.total_label.configure(bg=self.t['display'],fg=self.t['display_text'])
        walk(self.main)
        for b in self.tabs.values(): b.configure(bg=self.t['button'],fg=self.t['text'],activebackground=self.t['button_active'],activeforeground=self.t['text'])
        self.seekbar.configure(bg=self.t['panel']); self.seekbar.set_colors(self.t['progress_fill'],self.t['progress_rest'])
        self.volbar.configure(bg=self.t['panel']); self.volbar.set_colors(self.t['volume_fill'],self.t['volume_rest'])
        self.theme_btn.configure(text=(('\uf186' if self.theme_name == 'dark' else '\uf185') if self.icon_family else ('☾' if self.theme_name == 'dark' else '☀')))
        self.update_button_states()
        if hasattr(self, 'queue_tree'): self.queue_tree.tag_configure('current', background=self.t['panel2'], foreground=self.t['accent2'])
        self.status_msg.configure(fg=self.t['status']); self.status_pos.configure(fg=self.t['text']); self.status_song.configure(fg=self.t['status'])

    def clear_queue(self):
        if messagebox.askyesno('Clear queue', 'Remove all tracks from the current MPD queue?'):
            self.executor.submit('clear', tag='command')

    def toggle_theme(self):
        self.theme_name='light' if self.theme_name=='dark' else 'dark'; self.apply_theme()

    def connect_mpd(self):
        self.executor.submit('ping',tag='connect')

    def initial_refresh(self):
        self.executor.submit('status',tag='status')
        self.executor.submit('currentsong',tag='current')
        self.executor.submit('playlistinfo',tag='queue')

    def on_mpd_change(self, changed):
        if 'player' in changed or 'options' in changed:
            self.executor.submit('status',tag='status')
            self.executor.submit('currentsong',tag='current')
        if 'playlist' in changed:
            self.executor.submit('status',tag='status')
            self.executor.submit('playlistinfo',tag='queue')
        if 'database' in changed and self.current_tab in ('DATABASE','BROWSE: /'):
            self.after(0,self.reload_current_browse)

    def on_result_thread(self, tag, result):
        self.after(0,lambda t=tag,r=result:self.on_result(t,r))

    def on_result(self, tag, result):
        if tag == 'status_poll':
            self._status_poll_inflight = False
            tag = 'status'
        if isinstance(tag, tuple) and tag and tag[0] == 'volume':
            desired = int(tag[1])
            if self.pending_volume == desired:
                self.last_status['volume'] = str(desired)
                self.volbar.set(desired / 100)
                self.pending_volume = None
            return
        if isinstance(tag, tuple) and tag and tag[0] == 'seek':
            desired = float(tag[1])
            if self.pending_seek is not None and abs(self.pending_seek - desired) < 0.001:
                self.last_status['elapsed'] = str(desired)
                self.pending_seek = None
                self.update_player()
            return
        if isinstance(tag, tuple) and tag and tag[0] == 'db_album':
            self.db_rows = [{'name': x.get('album',''), 'type':'ALBUM',
                             'artist': tag[1], 'album': x.get('album','')} for x in (result or [])]
            self.render_db(); return
        if tag == 'db_album':
            self.db_rows = [{'name': x.get('album',''), 'type':'ALBUM'} for x in (result or [])]
            self.render_db(); return
        if tag == 'db_tracks':
            self.db_rows = [{'name': x.get('title') or os.path.basename(x.get('file','')),
                             'type':'TRACK', 'artist':x.get('artist',''),
                             'album':x.get('album',''), 'file':x.get('file','')}
                            for x in (result or [])]
            self.render_db(); return
        if tag == 'db':
            self.on_db_result(result); return
        if tag == 'browse':
            self.on_browse_result(result); return
        if tag == 'search':
            self.on_search_result(result); return
        if tag == 'playlists':
            self.on_playlists_result(result); return
        if tag == 'playlist_saved':
            self.status_msg.configure(text='Playlist saved'); self.after(2500,lambda:self.status_msg.configure(text=''))
            self.load_playlists(); return
        if tag == 'playlist_deleted':
            self.status_msg.configure(text='Playlist deleted'); self.after(2500,lambda:self.status_msg.configure(text=''))
            self.load_playlists(); return
        if isinstance(tag, tuple) and tag and tag[0] == 'playlist_load':
            self.status_msg.configure(text='Playlist loaded' if tag[1] else 'Playlist added to queue')
            self.after(2000,lambda:self.status_msg.configure(text=''))
            self.executor.submit('status',tag='status'); self.executor.submit('playlistinfo',tag='queue'); return
        if tag == 'update':
            self.status_msg.configure(text=f'Database update started (job {result})')
            self.after(5000, lambda: self.status_msg.configure(text=''))
            return
        if tag == 'status':
            self.last_status = result or {}
            actual_vol = self.last_status.get('volume')
            if actual_vol is not None:
                try:
                    actual = max(0, min(100, int(actual_vol)))
                    self.muted = actual == 0
                    if actual > 0:
                        self.saved_volume = actual
                    # V4 behavior: authoritative MPD status always wins.
                    self.volbar.set(actual / 100)
                    self.pending_volume = None
                except Exception: pass
            self.update_player(); self.update_button_states(); self.update_current_highlight(); return
        if tag == 'current':
            self.current = result or {}
            self.update_player(); self.update_current_highlight(); return
        if tag == 'queue':
            self.queue = result or []
            self.render_queue(); return
        if tag == 'connect':
            self.status_msg.configure(text='MPD socket connected')
            return

    def on_error_thread(self, tag, exc):
        self.after(0,lambda t=tag,e=exc:self.on_error(t,e))

    def on_error(self, tag, exc):
        if tag == 'status_poll':
            self._status_poll_inflight = False
            return
        if isinstance(tag, tuple) and tag and tag[0] in ('volume','seek'):
            self.status_msg.configure(text=f'MPD error: {exc}',fg=self.t['error'])
            if tag[0] == 'volume': self.pending_volume = None
            else: self.pending_seek = None
        elif tag in ('status','current','queue','connect'):
            self.status_msg.configure(text=f'MPD error: {exc}',fg=self.t['error'])

    def mpd_version_hint(self):
        return 'MPD'

    def update_player(self):
        s,c=self.last_status,self.current
        state=s.get('state','stop')
        elapsed=float(s.get('elapsed','0') or 0); duration=float(s.get('duration','0') or c.get('duration','0') or 0)
        self.elapsed_label.configure(text='remaining' if self.time_remaining else 'elapsed')
        self.time_label.configure(text=(f'-{fmt_time(max(0,duration-elapsed))}' if self.time_remaining and duration else fmt_time(elapsed)))
        self.total_name_label.configure(text='total')
        self.total_label.configure(text=fmt_time(duration) if duration else '--:--')
        title=c.get('title') or os.path.basename(c.get('file','')) or 'mpdamp'
        artist=c.get('artist',''); album=c.get('album','')
        self.song_label.configure(text=title)
        self.artist_label.configure(text=artist or state.upper())
        self.album_label.configure(text=album)
        fmt=c.get('format',''); rate='--'; bits='--'; chans='--'
        if fmt:
            p=fmt.split(':')
            if len(p)>0:
                try: rate=f'{int(p[0])/1000:g} kHz'
                except Exception: rate='--'
            if len(p)>1: bits=f'{p[1]} bit'
            if len(p)>2: chans=f'{p[2]} ch'
        bitrate=c.get('bitrate') or s.get('bitrate') or ''
        try:
            b=int(float(bitrate))
            if b <= 0: bitrate=''
        except Exception: bitrate=''
        if not bitrate:
            try:
                rel=c.get('file',''); path=os.path.join(MUSIC_ROOT, rel)
                size=os.path.getsize(path); bitrate=str(int(round(size*8/duration/1000))) if duration > 0 else ''
            except Exception: bitrate=''
        bitrate = bitrate or '--'
        codec=codec_from_song(c)
        self.format_label.configure(text=f'{codec}  •  {bitrate} kbps  •  {rate}  •  {bits}  •  {chans}')
        frac=max(0,min(1,elapsed/duration if duration else 0))
        if self.pending_seek is None and not self.seekbar.dragging: self.seekbar.set(frac)
        if not self.volbar.dragging:
            vol=int(s.get('volume',0) or 0); self.volbar.set(max(0,min(100,vol))/100)
        pos=s.get('song',''); total=s.get('playlistlength','--')
        pos_text=f'#{int(pos)+1}/{total}' if str(pos).isdigit() else f'#--/{total}'
        self.status_pos.configure(text=pos_text)
        self.status_song.configure(text=f'{state.upper()} • {artist} — {title}')
        self.status_total.configure(text=self.queue_total_time_text())

    def queue_total_time_text(self):
        total=0.0
        for song in self.queue:
            try: total += float(song.get('duration',0) or 0)
            except Exception: pass
        if total <= 0: return '0:00:00'
        sec=int(total); return f'{sec//3600}:{(sec%3600)//60:02d}:{sec%60:02d}'

    def toggle_time_mode(self):
        self.time_remaining = not self.time_remaining
        self.update_player()
        return 'break'

    def clock_tick(self):
        if self.last_status.get('state')=='play' and not self.seekbar.dragging:
            try:
                elapsed=float(self.last_status.get('elapsed','0') or 0)+0.25
                duration=float(self.last_status.get('duration','0') or 0)
                if duration: elapsed=min(elapsed,duration)
                self.last_status['elapsed']=str(elapsed)
                self.update_player()
            except Exception: pass
        # V4 behavior: continuously sample MPD status. This makes external
        # volume changes visible even while paused, without relying on idle events.
        if not self._status_poll_inflight and not self.executor.closed:
            self._status_poll_inflight = True
            self.executor.submit('status',tag='status_poll')
        self.after(250,self.clock_tick)

    def update_button_states(self):
        state=self.last_status.get('state','stop')
        # Fixed-size ASCII glyphs avoid the oversized pause glyph problem.
        self.buttons['playpause'].configure(text=('\uf04c' if self.icon_family else '⏸') if state=='play' else ('\uf04b' if self.icon_family else '▶'))
        for key,field in [('random','random'),('repeat','repeat'),('single','single'),('consume','consume')]:
            val=self.last_status.get(field,'0')
            on=str(val) in ('1','True','true','yes','on')
            self.buttons[key].configure(bg=self.t['select'] if on else self.t['button'],
                                        fg=self.t['select_text'] if on else self.t['text'],
                                        activebackground=self.t['select'])
        self.mute_btn.configure(text='MUTE' if self.muted else 'VOL',
                                 bg=self.t['select'] if self.muted else self.t['button'],
                                 fg=self.t['select_text'] if self.muted else self.t['text'],
                                 activebackground=self.t['select'])

    def seek_bar_command(self,f,dragging):
        duration=float(self.last_status.get('duration','0') or 0)
        if not duration: return
        if dragging:
            self.pending_seek=duration*f
            self.last_status['elapsed']=str(self.pending_seek)
            return
        self.pending_seek=duration*f
        self.last_status['elapsed']=str(self.pending_seek)
        self.update_player()
        self.executor.submit('seekcur',self.pending_seek,tag=('seek',self.pending_seek))

    def volume_bar_command(self,f,dragging):
        vol=int(round(max(0,min(1,f))*100))
        self.volbar.set(vol/100)
        self.muted = (vol == 0)
        if vol > 0:
            self.saved_volume = vol
        self.last_status['volume']=str(vol)
        if not dragging:
            self.executor.submit('setvol',vol,tag=('volume',vol))

    def volume_wheel(self,e):
        current=int(round(self.volbar.value*100))
        delta=1 if getattr(e,'delta',0)>0 or getattr(e,'num',0)==4 else -1
        new=max(0,min(100,current+delta*2))
        self.volbar.set(new/100)
        self.muted = (new == 0)
        if new > 0:
            self.saved_volume = new
        self.last_status['volume']=str(new)
        self.executor.submit('setvol',new,tag=('volume',new))
        return 'break'

    def toggle_mute(self):
        current=int(self.last_status.get('volume',0) or 0)
        if not self.muted:
            self.saved_volume=max(1,current)
            self.muted=True
            self.last_status['volume']='0'
            self.volbar.set(0)
            self.executor.submit('setvol',0,tag=('volume',0))
        else:
            new=max(1,min(100,self.saved_volume))
            self.muted=False
            self.last_status['volume']=str(new)
            self.volbar.set(new/100)
            self.executor.submit('setvol',new,tag=('volume',new))
        self.update_button_states()

    def prev(self): self.executor.submit('previous',tag='command')
    def playpause(self):
        if self.last_status.get('state')=='play': self.executor.submit('pause',1,tag='command')
        else: self.executor.submit('play',tag='command')
    def stop(self): self.executor.submit('stop',tag='command')
    def next(self): self.executor.submit('next',tag='command')
    def toggle_random(self): self.executor.submit('random',0 if self.last_status.get('random') in ('1','True','true') else 1,tag='command')
    def toggle_repeat(self): self.executor.submit('repeat',0 if self.last_status.get('repeat') in ('1','True','true') else 1,tag='command')
    def toggle_single(self): self.executor.submit('single',0 if self.last_status.get('single') in ('1','True','true') else 1,tag='command')
    def toggle_consume(self): self.executor.submit('consume',0 if self.last_status.get('consume') in ('1','True','true') else 1,tag='command')

    def render_queue(self):
        if not hasattr(self,'queue_tree'): return
        filter_text=self.queue_filter.get().strip().lower()
        old_selected=set(self.queue_tree.selection())
        for iid in self.queue_tree.get_children(): self.queue_tree.delete(iid)
        current_id=str(self.current.get('id') or self.last_status.get('songid',''))
        new_selected=[]
        for i,s in enumerate(self.queue):
            values=(i+1,s.get('artist',''),s.get('album',''),s.get('title') or os.path.basename(s.get('file','')))
            hay=' '.join(map(str,values)).lower()
            if filter_text and filter_text not in hay: continue
            iid=f'q{i}'
            tags=('current',) if str(s.get('id',''))==current_id else ()
            self.queue_tree.insert('', 'end', iid=iid, values=values, tags=tags)
            if iid in old_selected: new_selected.append(iid)
        if new_selected:
            self.queue_tree.selection_set(new_selected)
        self.queue_tree.tag_configure('current',background=self.t['panel2'],foreground=self.t['accent2'])
        self.status_total.configure(text=self.queue_total_time_text())

    def update_current_highlight(self):
        if not hasattr(self, 'queue_tree'): return
        current_id=str(self.current.get('id') or self.last_status.get('songid',''))
        for iid in self.queue_tree.get_children():
            try:
                idx=int(iid[1:]); song=self.queue[idx]
                self.queue_tree.item(iid, tags=('current',) if str(song.get('id',''))==current_id else ())
            except Exception: pass

    def queue_double(self,e=None):
        sel=self.queue_tree.selection()
        if not sel:return
        iid=sel[0]
        try:
            idx=int(iid[1:]); self.executor.submit('play',idx,tag='command')
        except Exception: pass

    def queue_delete(self,e=None):
        sel=self.queue_tree.selection()
        indexes=[]
        for iid in sel:
            try:indexes.append(int(iid[1:]))
            except:pass
        if not indexes: return 'break'
        first=min(indexes)
        for idx in sorted(indexes,reverse=True): self.executor.submit('delete',idx,tag='command')
        self.after(120, lambda: self._restore_queue_focus(first))
        return 'break'

    def _restore_queue_focus(self, index):
        if not self.queue_tree.winfo_exists(): return
        children=self.queue_tree.get_children()
        if not children: return
        idx=min(index, len(children)-1)
        self.queue_tree.focus(children[idx]); self.queue_tree.selection_set(children[idx]); self.queue_tree.see(children[idx])
        self.queue_tree.focus_set()

    def show_tab(self,name):
        self.current_tab=name
        for f in (self.queue_frame,self.db_frame,self.browse_frame,self.search_frame,self.playlists_frame): f.pack_forget()
        frame={'PLAYING / QUEUE':self.queue_frame,'DATABASE':self.db_frame,'BROWSE: /':self.browse_frame,'SEARCH':self.search_frame,'PLAYLISTS':self.playlists_frame}[name]
        frame.pack(fill='both',expand=True)
        for n,b in self.tabs.items(): b.configure(bg=self.t['select'] if n==name else self.t['button'],fg=self.t['select_text'] if n==name else self.t['text'], activebackground=self.t['select'] if n==name else self.t['button_active'])
        if name=='PLAYING / QUEUE': self.render_queue()
        elif name=='DATABASE': self.db_load_root()
        elif name=='BROWSE: /': self.browse_load('/')
        elif name=='PLAYLISTS': self.load_playlists()

    def db_load_root(self):
        self.db_path='/'; self.db_mode='artists'; self.db_path_label.configure(text='Database: Artists'); self.executor.submit('list','artist',tag='db')

    def on_db_result(self,result):
        self.db_rows=[]
        for x in result or []:
            name=x.get('artist') or x.get('name','')
            if name: self.db_rows.append({'name':name,'type':'ARTIST','artist':name})
        self.render_db()

    def render_db(self):
        for iid in self.db_tree.get_children(): self.db_tree.delete(iid)
        for i,r in enumerate(self.db_rows):
            self.db_tree.insert('', 'end', iid=f'd{i}', values=(r.get('name',''), r.get('type',''), r.get('artist',''), r.get('album',''), r.get('title') or r.get('name','')))

    def db_double(self,e=None):
        sel=self.db_tree.selection()
        if not sel:return
        try: r=self.db_rows[int(sel[0][1:])]
        except Exception:return
        if self.db_mode=='artists':
            artist=r.get('artist') or r.get('name','')
            self.db_mode='albums'; self.db_path=artist; self.db_path_label.configure(text=f'Database: {artist} / Albums')
            self.executor.submit('list','album','artist',artist,tag=('db_album',artist))
        elif self.db_mode=='albums':
            album=r.get('album') or r.get('name',''); artist=r.get('artist') or self.db_path
            self.db_mode='tracks'; self.db_path=f'{artist} / {album}'; self.db_path_label.configure(text=f'Database: {artist} / {album}')
            self.executor.submit('search','album',album,'artist',artist,tag='db_tracks')
        else:
            self.db_add_selected()

    def db_back(self):
        if self.db_mode=='tracks':
            parts=self.db_path.split(' / ',1); artist=parts[0]
            self.db_mode='albums'; self.db_path=artist; self.db_path_label.configure(text=f'Database: {artist} / Albums')
            self.executor.submit('list','album','artist',artist,tag=('db_album',artist)); return
        if self.db_mode=='albums': self.db_load_root(); return
        self.db_load_root()

    def db_add_selected(self):
        for iid in self.db_tree.selection():
            try:r=self.db_rows[int(iid[1:])]
            except:continue
            self.db_add_row(r)

    def db_add_all(self):
        if self.db_mode == 'artists' and len(self.db_rows) > 100:
            if not messagebox.askyesno('Add all shown', f'Add all {len(self.db_rows)} artists to the queue?\n\nThis can add a very large number of tracks.'):
                return
        for r in self.db_rows:self.db_add_row(r)

    def db_add_row(self,r):
        if r.get('type')=='TRACK': self.executor.submit('add',r.get('file'),tag='add'); return
        if r.get('type')=='ARTIST': self.executor.submit('findadd','file',r['name'],tag='add'); return
        if r.get('type')=='ALBUM': self.executor.submit('searchadd','album',r['album'], 'artist', r.get('artist',''), tag='add')

    def update_database(self): self.executor.submit('update',tag='update')

    def browse_load(self,path):
        self.db_path=path or '/'; self.browse_path.configure(text=f'Browse: {self.db_path}'); self.executor.submit('lsinfo',self.db_path,tag='browse')

    def on_browse_result(self,result):
        self.browse_tree.delete(0,'end')
        self.browse_rows=[]
        for x in result or []:
            if 'directory' in x:self.browse_rows.append(('dir',x['directory']))
            elif 'file' in x:self.browse_rows.append(('file',x['file']))
        self.browse_rows.sort(key=lambda x:(x[0]!='dir',x[1].lower()))
        for typ,path in self.browse_rows:self.browse_tree.insert('end',('📁 ' if typ=='dir' else '🎵 ')+os.path.basename(path.rstrip('/')))

    def browse_double(self,e=None):
        sel=self.browse_tree.curselection()
        if not sel:return
        typ,path=self.browse_rows[sel[0]]
        if typ=='dir':self.browse_load(path)
        else:self.executor.submit('add',path,tag='add')

    def browse_back(self):
        p=self.db_path.rstrip('/')
        if not p:return
        parent=os.path.dirname(p) or '/'; self.browse_load(parent)

    def browse_add_selected(self):
        for i in self.browse_tree.curselection():
            typ,path=self.browse_rows[i]
            # MPD accepts both file and directory URIs for add(). A directory
            # adds its contents recursively according to MPD's database.
            self.executor.submit('add',path,tag='add')

    def reload_current_browse(self):
        if self.current_tab=='BROWSE: /': self.browse_load(self.db_path)
        elif self.current_tab=='DATABASE': self.db_load_root()

    def do_search(self):
        q=self.search_entry.get().strip()
        if q:self.executor.submit('search','any',q,tag='search')

    def on_search_result(self,result):
        self.search_results_data=result or []; self.search_tree.delete(*self.search_tree.get_children())
        for i,s in enumerate(self.search_results_data):
            self.search_tree.insert('', 'end', iid=f's{i}', values=(s.get('artist',''),s.get('album',''),s.get('title') or os.path.basename(s.get('file',''))))

    def search_add_selected(self):
        for iid in self.search_tree.selection():
            try:s=self.search_results_data[int(iid[1:])]
            except:continue
            self.executor.submit('add',s.get('file'),tag='add')

    def search_add_all(self):
        for s in self.search_results_data:self.executor.submit('add',s.get('file'),tag='add')

    def search_double(self,e=None):self.search_add_selected()

    def build_playlists(self):
        self.playlists_frame=tk.Frame(self.content,bd=0)
        top=tk.Frame(self.playlists_frame,bd=0); top.pack(fill='x',pady=(0,5))
        self.playlist_name=tk.Entry(top,font=self.font_small,bd=0)
        self.playlist_name.pack(side='left',fill='x',expand=True)
        self.playlist_name.insert(0,'new_playlist')
        tk.Button(top,text='SAVE PLAYLIST',command=self.save_playlist,relief='flat',bd=0,font=self.font_tiny).pack(side='right',padx=(5,0))
        holder=tk.Frame(self.playlists_frame,bd=0); holder.pack(fill='both',expand=True)
        self.playlist_tree=ttk.Treeview(holder,columns=('playlist',),show='headings',selectmode='extended')
        self.playlist_tree.heading('playlist',text='PLAYLIST')
        self.playlist_tree.column('playlist',anchor='w',width=500)
        sy=ttk.Scrollbar(holder,orient='vertical',command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=sy.set)
        self.playlist_tree.grid(row=0,column=0,sticky='nsew'); sy.grid(row=0,column=1,sticky='ns')
        holder.rowconfigure(0,weight=1); holder.columnconfigure(0,weight=1)
        self.playlist_tree.bind('<Double-1>',lambda e:self.load_selected_playlist(replace=True))
        bottom=tk.Frame(self.playlists_frame,bd=0); bottom.pack(fill='x',pady=(5,0))
        self.playlist_actions=bottom
        tk.Button(bottom,text='DELETE PLAYLIST',command=self.delete_playlist,relief='flat',bd=0,font=self.font_tiny).pack(side='left')
        tk.Label(bottom,text='double click to replace playlist',font=self.font_tiny).pack(side='left',padx=(10,0))
        tk.Button(bottom,text='ADD TO QUEUE',command=lambda:self.load_selected_playlist(replace=False),relief='flat',bd=0,font=self.font_tiny).pack(side='right',padx=(4,0))
        tk.Button(bottom,text='RELOAD',command=self.load_playlists,relief='flat',bd=0,font=self.font_tiny).pack(side='right')

    def load_playlists(self):
        self.executor.submit('listplaylists',tag='playlists')

    def on_playlists_result(self,result):
        self.playlist_rows=[]
        for x in result or []:
            name=x.get('playlist') or x.get('name')
            if name: self.playlist_rows.append(name)
        self.playlist_rows.sort(key=str.lower)
        self.playlist_tree.delete(*self.playlist_tree.get_children())
        for i,name in enumerate(self.playlist_rows):
            self.playlist_tree.insert('', 'end', iid=f'p{i}', values=(name,))

    def normalized_playlist_name(self):
        name=self.playlist_name.get().strip()
        if name.lower().endswith('.m3u'): name=name[:-4]
        return name

    def save_playlist(self):
        name=self.normalized_playlist_name()
        if not name: return
        self.executor.submit('save',name,tag='playlist_saved')

    def selected_playlist_name(self):
        sel=self.playlist_tree.selection()
        if not sel: return None
        try: return self.playlist_rows[int(sel[0][1:])]
        except Exception: return None

    def load_selected_playlist(self,replace=True):
        name=self.selected_playlist_name()
        if not name: return
        # MPD load() replaces nothing: it appends. For the requested replace
        # behavior, clear and load are kept in one worker transaction.
        self.executor.submit('__load_playlist_replace' if replace else 'load',name,tag=('playlist_load',replace))

    def delete_playlist(self):
        name=self.selected_playlist_name()
        if not name: return
        if messagebox.askyesno('Delete playlist',f'Delete playlist "{name}"?'):
            self.executor.submit('rm',name,tag='playlist_deleted')

    def show_info(self):
        c=MPDClient(); c.timeout=2
        mpdver='unknown'
        try:c.connect(SOCKET); mpdver=c.mpd_version
        except Exception:pass
        finally:
            try:c.close();c.disconnect()
            except:pass
        messagebox.showinfo('mpdamp',f'{APP_VERSION}\n\nPython: {sys.version.split()[0]}\nTk: {tk.TkVersion}\npython-mpd: Debian package 3.1.2 (expected)\nMPD: {mpdver}\nSocket: {SOCKET}\nTheme: {self.theme_name}')

    def on_close(self):
        self.idle.stop(); self.executor.close(); self.destroy()


if __name__=='__main__':
    MPDAmp().mainloop()

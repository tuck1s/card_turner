#!/usr/bin/env python3
# Simple card turning app
import argparse, configparser, random, time
from tkinter import *
from datetime import datetime

# Dump out a configparser section as a pure dict, removing the self-named default section
def dump_section(s):
    d = dict(s.items())
    dsect = s.name
    del(d[dsect])
    return d

class Deck():
    """A deck comprises cards that can be shuffled, drawn, undrawn. Drawn cards go onto the discard pile"""

    def __init__(self, name, color='white', textcolor='black'):
        self.name = name
        self.cards = []
        self.discards = []
        self.table = None
        self.color = color
        self.textcolor = textcolor
        return

    def add(self, c):
        """Add a single card, or a list of cards"""
        if iter(c) and not isinstance(c, str):
            self.cards.extend(c)
        else:
            self.cards.append(c)

    def shuffle(self):
        """Randomise the order of the cards and the discards"""
        random.shuffle(self.cards)
        random.shuffle(self.discards)
        return

    def draw(self):
        """Move a card from the front of the deck to the table. If exhausted, returns None """
        try:
            self.discard() # ensure the table is empty
            self.table = self.cards.pop()
        finally:
            return self.label(self.table)

    def discard(self):
        """Move card from table to discard. If None, does nothing """
        if self.table:
            self.discards.append(self.table)
            self.table = None
            return self.label(self.table)

    def undiscard(self):
        """ Get a card back from the discards to the table. If exhausted, returns None """
        try:
            self.undraw() # ensure the table is empty
            self.table = self.discards.pop()
        finally:
            return self.label(self.table)


    def undraw(self):
        """ Get a card back from the discards to the table. If exhausted, returns empty """
        if self.table:
            self.cards.append(self.table)
            self.table = None
        return self.label(self.table)

    def label(self, c):
        if c == None:
            return ''
        else:
            return c


def get_decks(config):
    decks = []
    for i in config.sections():
        if i != 'main':
            color = config[i].get('color', None)
            textcolor = config[i].get('textcolor', None)
            d = Deck(i, color, textcolor)
            cards = config[i].get('cards', None)
            if cards:
                d.add(cards.lstrip('"').rstrip('"').split(',')) # remove quotation marks if any
            d.shuffle()
            decks.append(d)
    return decks


class App():
    def handle_draw(self, event):
        num = event.widget.extra[0]
        lbl = event.widget.extra[1]
        c = self.decks[num].draw()
        lbl['text'] = c
        self.reset_clock()


    def handle_undraw(self, event):
        num = event.widget.extra[0]
        lbl = event.widget.extra[1]
        c = self.decks[num].undraw()
        lbl['text'] = c
        self.reset_clock()


    def handle_discard(self, event):
        num = event.widget.extra[0]
        lbl = event.widget.extra[1]
        c = self.decks[num].discard()
        lbl['text'] = c
        self.reset_clock()


    def handle_undiscard(self, event):
        num = event.widget.extra[0]
        lbl = event.widget.extra[1]
        c = self.decks[num].undiscard()
        lbl['text'] = c
        self.reset_clock()


    def reset_clock(self):
        self.time_started = datetime.now()
        self.timer_label['text'] = '00:00'
        self.window.after(1000, self.update_clock)

    def update_clock(self):
        spent = datetime.now() - self.time_started
        minutes, seconds = divmod(spent.seconds, 60)
        self.timer_label['text'] = '{:02}:{:02}'.format(int(minutes), int(seconds))
        self.window.after(1000, self.update_clock)

    def __init__(self, decks, w):
        self.window = Tk()
        self.window.attributes('-topmost', 1) # bring window in front of others
        self.window.title(w.get('title'))
        self.decks = decks
        bg=w.get('color')

        f_width = 100
        frm = Frame(master=self.window, width=f_width, bg=bg)
        self.timer_label = Label(master=frm)
        self.reset_clock()

        self.timer_label.pack()

        for i, d in enumerate(decks):
            frm.grid(row=i, column=1, padx=5, pady=5)

            # f1: Deck names
            f1 = Frame(master=frm, width=f_width, relief=GROOVE, borderwidth=5, bg=bg)
            lbl1 = Label(master=f1, text=d.name, bg=d.color, fg=d.textcolor, width=30, wraplength=f_width)
            lbl1.pack(fill=X)

            # f2: Draw / undraw buttons
            f2 = Frame(master=frm, width=f_width, bg=bg)
            btn1 = Button(master=f2, text='⬇︎', highlightbackground=bg)
            btn1.bind('<Button-1>', self.handle_draw)
            btn1.pack(side=LEFT)

            btn2 = Button(master=f2, text='⬆︎', highlightbackground=bg)
            btn2.bind('<Button-1>', self.handle_undraw)
            btn2.pack(side=RIGHT)

            # f3: Table, has one card face-up
            f3 = Frame(master=frm, width=f_width, bg=bg)
            lbl2 = Label(master=f3, text=None, bg=d.color, fg=d.textcolor, wraplength=200)
            lbl2.pack()

            # f4: Discard / undiscard buttons
            f4 = Frame(master=frm, width=f_width, bg=bg)
            btn3 = Button(master=f4, text='⬇︎', highlightbackground=bg)
            btn3.bind('<Button-1>', self.handle_discard)
            btn3.pack(side=LEFT)

            btn4 = Button(master=f4, text='⬆︎', bg='gray', highlightbackground=bg)
            btn4.bind('<Button-1>', self.handle_undiscard)
            btn4.pack(side=RIGHT)

            f1.pack(side='top', fill='both', expand=True)
            f2.pack(fill='both', expand=True)
            f3.pack(fill='both', expand=True)
            f4.pack(fill='both', expand=True)

            # Provide hooks to deck number and label
            btn1.extra = (i, lbl2)
            btn2.extra = (i, lbl2)
            btn3.extra = (i, lbl2)
            btn4.extra = (i, lbl2)
        self.window.mainloop()

# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Simple card turning game app')
parser.add_argument('inifile', metavar='file.ini', type=argparse.FileType('r'),
                    help='Configuration file')
args = parser.parse_args()
config = configparser.ConfigParser(defaults= {
    'main': {
        'width': 400,
        'height': 400,
        'color': 'black',
        'title': 'Card turner'
    }
})
config.read_file(args.inifile)
decks = get_decks(config)
print('{} card decks read'.format(len(decks)))
App(decks, config['main'])

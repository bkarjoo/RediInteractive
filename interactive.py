from Queue import Queue
import time
from Tkinter import *
from ScrolledText import ScrolledText
from threading import Thread
import datetime
from redi_order_factory import RediOrderFactory

import google_sheet_dtp as gs


class Interactive(object):

    def __init__(self):
        self.printQueue = Queue()
        # Tkinter components:
        self.root = Tk() # the is the GUI
        self.root.title = "PGF API App"
        self.text_box = ScrolledText(self.root)
        self.runPrintQueue = True
        self.is_running = False
        self.prompt_var = StringVar()
        self.user_input = StringVar()
        # redi object
        self.of = RediOrderFactory()
        self.google_sheet = None
        self.confirm_mode = ''

    def gui_start(self):
        printer_thread = Thread(target=self.queue_printer)
        printer_thread.daemon = True
        printer_thread.start()
        # start printer_thread

        self.text_box.pack()
        self.text_box.config(state=DISABLED)

        user_prompt_entry = Entry(self.root, textvariable=self.prompt_var)
        user_prompt_entry.pack(fill=BOTH)

        entry_var = StringVar()
        entry_box = Entry(self.root, textvariable=entry_var)

        def enter_pressed(event):
            print event
            self.user_input = entry_box.get()

            self.print_user_input(self.user_input)
            request_thread = Thread(target=self.process_user_input, args=[entry_box.get()])
            # self.process_user_input(entry_box.get())
            request_thread.start()
            entry_box.delete(0, 'end')

        entry_box.bind("<Return>", enter_pressed)
        entry_box.pack(fill=BOTH)
        entry_box.focus_set()

        self.user_input.set('')

        mainloop()
        self.runPrintQueue = False

    def queue_printer(self):
        while True:
            item = self.printQueue.get()

            self.text_box.config(state=NORMAL)
            self.text_box.insert(END, item)
            if isinstance(item, basestring):
                self.text_box.insert(END, '\n')
            if isinstance(item, ListType):
                self.text_box.insert(END, '\n')
            self.text_box.config(state=DISABLED)
            self.text_box.see('end')
            if not self.runPrintQueue:
                break
            time.sleep(.1)
            self.printQueue.task_done()

    def print_user_input(self, item):
        self.text_box.config(state=NORMAL)
        self.text_box.tag_config("b", foreground="blue")
        self.text_box.insert(END, item, "b")
        self.text_box.insert(END, '\n')
        self.text_box.config(state=DISABLED)
        self.text_box.see('end')

    def print2(self, txt):
        print txt
        self.printQueue.put(txt)

    def process_user_input(self, ui):
        # build this one function at a time
        if ui[:4].upper() == 'ECHO':
            self.print2(ui[4:])
            self.prompt_var.set(ui[4:])
        elif ui.upper() == 'QUIT' or ui.upper() == 'Q':
            self.print2('Breaking out of interactive.')
            sys.stdout.flush()
            self.root.quit()
            return -1
        elif ui.upper() == 'LOAD SHEET':
            self.print2('Called Load Sheet')
            try:
                self.google_sheet = gs.GoogleSheetDailyTradingProcedure()

                self.print2('wait a moment . . . ')
                sys.stdout.flush()
                self.google_sheet.load_sheet()
                self.print2('sheet loaded')

            except E:
                self.print2('problem loading sheet' + E)

        elif ui.upper() == 'PRINT SHEET':
            if self.google_sheet:
                for row in self.google_sheet.sheet:
                    self.print2(row)

            else:
                self.print2('Load sheet first. (cmd = load sheet)')

        elif ui.upper()[:10] == 'SUBMIT ROW':
            row = int(ui.split(' ')[2]) - 1

            self.submit_row(row)
            # submit_row_thread = Thread(target=self.submit_row,args=[row])
            # submit_row_thread.start()
        elif ui.upper()[:10] == 'SUBMIT ALL':
            if self.google_sheet.sheet:
                i = -1
                toks = ui.split(' ')
                # if user added a starting row
                if len(toks) > 2:
                    row = int(ui.split(' ')[2]) - 1
                else:
                    row = 2
                for _ in self.google_sheet.sheet:
                    i += 1
                    if i < (row):
                        continue
                    a = self.submit_row(i)
                    if a == 'b':
                        break
            else:
                pass
        elif ui.upper() == 'LOAD ADRS':
            self.google_sheet = gs.GoogleSheetDailyTradingProcedure()
            sheet_id = '1Z3POIK8N5Vi_CsF_MDLszrJeNviBwrU9BuVFC8h-xgQ'
            worksheet_range = 'ADRs Test!A1:F'
            self.print2('wait a moment')
            sys.stdout.flush()
            self.google_sheet.load_sheet(sheet_id, worksheet_range)
            self.print2('adrs loaded')
        elif ui.upper()[:14] == 'SUBMIT ADR ROW':
            r = int(ui.split(' ')[3])
            self.submit_our_adr_row(r)
            self.print2('submit adr row')
        elif ui.upper() == 'SUBMIT ALL ADRS':
            if self.google_sheet.sheet:
                i = -1
                for _ in self.google_sheet.sheet:
                    i += 1
                    if i < 2:
                        continue
                    a = self.submit_our_adr_row(i)

                    if a == 'b':
                        break
            else:
                pass
            self.print2('submit adrs')
        elif ui.upper() == 'SUBMIT ALL MOCS':
            if self.google_sheet.sheet:
                i = -1
                for _ in self.google_sheet.sheet:
                    i += 1
                    if i < 2:
                        continue
                    a = self.submit_our_moc_row(i)
                    if a == 'b':
                        break
            else:
                pass
        elif ui.upper()[:14] == 'SUBMIT MOC ROW':
            r = int(ui.split(' ')[3])
            self.submit_our_moc_row(r)
            self.print2('submit adr row')
        elif ui.upper()[:8] == 'STOP ROW':
            stop_tokens = ui.split(' ')
            row_num = int(stop_tokens[2]) - 1
            row = self.google_sheet.sheet[row_num]
            if len(stop_tokens) == 4:
                quantity = int(stop_tokens[3])
            else:
                quantity = int(row[4])
            side = 'sell' if (
                    row[3].upper() == 'LONG'
                    or row[3].upper() == 'BUY'
                    or row[3].upper() == 'B') else 'buy'
            if side == 'sell':
                quantity *= -1
            symbol = row[2].split()[0].upper()
            stop_price = 0
            if len(row) >= 13:
                stop_price = round(float(row[12]), 2)
            account = row[1].upper()
            if side == 'sell':
                stop_limit = round(stop_price * .99, 2)
            else:
                stop_limit = round(stop_price * 1.01, 2)
            self.of.generate_stop_limit_order(quantity, symbol, stop_price, stop_limit, account)
        elif ui.upper()[:9] == 'PRINT ROW':
            if self.google_sheet:
                tokens = ui.split(' ')
                self.print2(self.google_sheet.sheet[int(tokens[2]) - 1])
            else:
                self.print2('Load sheet first. (cmd = load sheet)')
        else:
            if ui != 'y' and ui != 'n' and ui != 'b':
                self.print2('Command not understood.')

    def submit_row(self, r, confirm=True):

        try:
            if self.google_sheet:
                row = self.google_sheet.sheet[r]
                self.print2(row)
                sys.stdout.flush()

                account = row[1].upper()
                symbol = row[2].split()[0].upper()
                if symbol == '':
                    return
                if row[4] == '':
                    self.print2("Row doesn't have quantity. Enter quantity and reload sheet.")
                    sys.stdout.flush()
                    return
                quantity = int(row[4])
                side = 'buy' if (
                        row[3].upper() == 'LONG'
                        or row[3].upper() == 'BUY'
                        or row[3].upper() == 'B'
                ) else 'sell'


                if side == 'sell':
                    quantity *= -1

                o_type = None

                if len(row) >= 7:
                    o_type = row[6].upper()
                price = 0
                if len(row) >= 8:
                    if row[7] == '':
                        price = 0
                    else:
                        price = float(row[7][1:]) if row[7][0] == '$' else float(row[7])
                trade_date = None
                if len(row) >= 9:
                    trade_date = row[8]

                if str(datetime.datetime.now())[:10] != trade_date:
                    self.print2('Date is not today')
                    sys.stdout.flush()
                    return

                order_string = '{} {} {} {} {} in {}'.format(
                        side, abs(quantity), symbol, price, o_type, account)

                if self.confirm_mode == 'c': confirm = False
                if confirm:

                    confirm_msg = '{}? (y/n/b/c)'.format(order_string)

                    self.user_input = ''
                    self.prompt_var.set(confirm_msg)
                    while self.user_input == '':
                        time.sleep(.1)
                    inp = self.user_input
                    self.confirm_mode = inp
                    if inp == 'c': inp = 'y'
                    self.prompt_var.set('')
                else:
                    inp = 'y'

                if inp == 'y':
                    o = False
                    if o_type == 'MOO':
                        o = self.of.generate_opg_market_order(quantity, symbol, account)
                    elif o_type == 'LOO':
                        o = self.of.generate_opg_limit_order(quantity, symbol, price, account)
                    elif o_type == 'LOC':
                        o = self.of.generate_loc_order(quantity, symbol, price, account)
                    elif o_type == 'MOC':
                        o = self.of.generate_moc_order(quantity, symbol, account)
                    elif o_type == 'LIMIT' or o_type == 'LMT':
                        o = self.of.generate_limit_order(quantity, symbol, price, account)
                    time.sleep(.05)
                    if o:
                        return '1'
                    else:
                        return '0'
                elif inp == 'b':
                    return 'b'  # user requested break
                else:
                    return inp
            else:
                self.print2('Load sheet first. (cmd = load sheet)')
                sys.stdout.flush()
                return 'b'
        except Exception as e:
            self.print2('row {} failed to submit: {}'.format(r + 1, e))
            sys.stdout.flush()

    def submit_our_adr_row(self, r, confirm=False):

        try:
            if self.google_sheet:
                row = self.google_sheet.sheet[r - 1]
                self.print2(row)
                sys.stdout.flush()

                symbol = row[1].split()[0].upper()
                if symbol == '':
                    return
                if row[3] == '':
                    self.print2("Row doesn't have quantity. Enter quantity and reload sheet.")
                    sys.stdout.flush()
                    return
                quantity = int(row[3])
                if row[2] == '':
                    return
                side = 'buy' if (
                        row[2].upper() == 'LONG'
                        or row[2].upper() == 'BUY'
                        or row[2].upper() == 'B'
                ) else 'sell'
                if side == 'sell':
                    quantity *= -1
                order_type = None
                if len(row) >= 6:
                    order_type = row[5].upper()
                price = 0
                if len(row) >= 5:
                    if row[4] == '':
                        price = 0
                    else:
                        price = float(row[4][1:]) if row[4][0] == '$' else float(row[4])
                trade_date = None
                if len(row) >= 1:
                    trade_date = row[0]

                if str(datetime.datetime.now())[:10] != trade_date:
                    self.print2('Date is not today')
                    sys.stdout.flush()
                    return

                order_string = '{} {} {} {} {}'.format(
                    side, abs(quantity), symbol, price, order_type)
                if confirm:
                    sys.stdout.write('{} {} {} {} {}? (y/n/b)'.format(side, abs(quantity), symbol, price, order_type))
                    sys.stdout.flush()
                    inp = raw_input()
                else:
                    inp = 'y'
                if inp == 'y':
                    o = 0
                    if order_type == 'MOO':
                        o = self.of.generate_opg_market_order(quantity, symbol)
                    elif order_type == 'LOO':
                        o = self.of.generate_opg_limit_order(quantity, symbol, price)
                    elif order_type == 'LOC':
                        o = self.of.generate_loc_order(quantity, symbol, price)
                    elif order_type == 'MOC':
                        o = self.of.generate_moc_order(quantity, symbol)
                    elif order_type == 'LIMIT' or order_type == 'LMT':
                        o = self.of.generate_limit_order(quantity, symbol, price)
                    if o:
                        return '1'
                    else:
                        return '0'
                if inp == 'b':
                    return 'b'
                else:
                    self.print2('order not submitted: {}'.format(order_string))
                    sys.stdout.flush()
                return ''
            else:
                self.print2('Load sheet first. (cmd = load sheet)')
                sys.stdout.flush()
                return 'b'
        except Exception as e:
            self.print2('row {} failed to submit: {}'.format(r + 1, e))
            sys.stdout.flush()

    def submit_our_moc_row(self, r, confirm=False):

        try:
            if self.google_sheet:
                row = self.google_sheet.sheet[r - 1]
                self.print2(row)
                sys.stdout.flush()

                symbol = row[1].split()[0].upper()
                if symbol == '':
                    return
                if row[3] == '':
                    self.print2("Row doesn't have quantity. Enter quantity and reload sheet.")
                    sys.stdout.flush()
                    return
                quantity = int(row[3])
                if row[2] == '':
                    return
                side = 'sell' if (
                        row[2].upper() == 'LONG'
                        or row[2].upper() == 'BUY'
                        or row[2].upper() == 'B'
                ) else 'buy'
                if side == 'sell':
                    quantity *= -1
                order_type = 'MOC'
                price = 0
                order_string = '{} {} {} {} {}'.format(
                    side, abs(quantity), symbol, price, order_type)
                if confirm:
                    sys.stdout.write('{} {} {} {} {}? (y/n/b)'.format(
                        side, abs(quantity), symbol, price, order_type))
                    sys.stdout.flush()
                    inp = raw_input()
                else:
                    inp = 'y'

                if inp == 'y':
                    o = 0
                    if order_type == 'MOC':
                        o = self.of.generate_moc_order(quantity, symbol)
                    time.sleep(.05)
                    if o:
                        return '1'
                    else:
                        return '0'
                if inp == 'b':
                    return 'b'
                else:
                    self.print2('order not submitted: {}'.format(order_string))
                    sys.stdout.flush()
                return ''
            else:
                self.print2('Load sheet first. (cmd = load sheet)')
                sys.stdout.flush()
                return 'b'
        except Exception as e:
            self.print2('row {} failed to submit: {}'.format(r + 1, e))
            sys.stdout.flush()

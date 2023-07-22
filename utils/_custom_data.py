import backtrader as bt
from datetime import datetime

class MyCustomData(bt.feed.DataBase):
    params = (
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('tick_volume', 5),
        ('spread', 6),
        ('real_volume', 7),
    )

    def start(self):
        super().start()

    def _loadline(self, linetokens):
        # Convert the date and time string to a datetime object
        dt = datetime.strptime(linetokens[self.p.datetime], '%Y-%m-%d %H:%M:%S')
        self.lines.datetime[0] = bt.date2num(dt)
        self.lines.open[0] = float(linetokens[self.p.open])
        self.lines.high[0] = float(linetokens[self.p.high])
        self.lines.low[0] = float(linetokens[self.p.low])
        self.lines.close[0] = float(linetokens[self.p.close])
        self.lines.tick_volume[0] = int(linetokens[self.p.tick_volume])
        self.lines.spread[0] = float(linetokens[self.p.spread])
        self.lines.real_volume[0] = int(linetokens[self.p.real_volume])
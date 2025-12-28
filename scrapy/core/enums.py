from enum import Enum, auto

class MarketRegime(Enum):
    TREND_UP = auto()
    TREND_DOWN = auto()
    RANGE = auto()
    PANIC = auto()
    NO_TRADE = auto()

class TakeStop(Enum):
    TakeProfit = auto()
    StopLoss = auto()
    Hold = auto()

class LongShort(Enum):
    EnterLong = auto()
    EnterShort = auto()
    NoTrade = auto()

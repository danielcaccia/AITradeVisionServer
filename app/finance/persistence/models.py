from peewee import Model, CharField, DateField, FloatField, IntegerField, TimestampField, DateTimeField

from .database import db

class BaseModel(Model):
    class Meta:
        database = db


class Dividend(BaseModel):
    symbol = CharField()
    name = CharField()
    ex_dividend_date = DateField()
    dividend_per_share = FloatField(null=True)
    payment_date = DateField(null=True)
    record_date = DateField(null=True)
    declaration_date = DateField(null=True)
    created_at = TimestampField()


class Ipo(BaseModel):
    symbol = CharField()
    name = CharField()
    exchange = CharField()
    ipo_date = DateField()
    price_range = FloatField(null=True)
    created_at = DateTimeField()


class TechnicalSignal(BaseModel):
    symbol = CharField()
    name = CharField(null=True)
    last_price = FloatField()
    rsi = FloatField(null=True)
    macd_cross = CharField(null=True)  # 'bullish', 'bearish', or None
    signal_summary = CharField()
    created_at = TimestampField()


class MarketMovers(BaseModel):
    symbol = CharField()
    name = CharField()
    price = FloatField()
    variation = FloatField()
    volume_spike = FloatField()
    current_volume = IntegerField()
    avg_volume = FloatField()
    snapshot_type = CharField()  # 'gainer', 'loser', 'trending'
    created_at = TimestampField()

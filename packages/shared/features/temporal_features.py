from pandas.tseries.holiday import HolidayCalendar
from feature_engine.creation import CyclicalFeatures

def create_calendar_features(df):
    cal = HolidayCalendar()
    holidays = cal.holidays(start=df.index.min(), end=df.index.max())
    df['is_holiday'] = df.index.isin(holidays).astype(int)

    cyclical = CyclicalFeatures(
        variables=["hour", "day_of_week", "month"],
        drop_original=True
    )
    return cyclical.fit_transform(df)

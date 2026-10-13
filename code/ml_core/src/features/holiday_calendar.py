import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from ..config import get_holiday_country
from ..exceptions import ConfigurationError

NO_HOLIDAYS = "NONE"


def resolve_country(country: str | None = None) -> str:
    """Normalise a country code, falling back to the ``HOLIDAY_COUNTRY`` setting."""
    value = (country if country is not None else get_holiday_country()).strip().upper()
    return value or NO_HOLIDAYS


def _holiday_dates(dates: pd.DatetimeIndex, country: str) -> set[pd.Timestamp]:
    if country == "US":
        us_calendar = USFederalHolidayCalendar()
        return set(us_calendar.holidays(start=dates.min(), end=dates.max()))

    try:
        import holidays as holidays_lib
    except ImportError as exc:
        raise ConfigurationError(
            f"HOLIDAY_COUNTRY={country!r} needs the optional 'holidays' package "
            "(pip install holidays), or set HOLIDAY_COUNTRY to US or NONE."
        ) from exc

    years = range(int(dates.min().year), int(dates.max().year) + 1)
    try:
        calendar = holidays_lib.country_holidays(country, years=years)
    except NotImplementedError as exc:
        raise ConfigurationError(
            f"No holiday calendar is available for country {country!r}."
        ) from exc
    return {pd.Timestamp(day) for day in calendar}


def holiday_flags(
    index: pd.Index | pd.Series, country: str | None = None
) -> np.ndarray:
    """Return a 0/1 integer array marking timestamps that fall on a public holiday.

    Timestamps are matched on their calendar date as given (the package works in
    naive UTC), so holidays are not shifted into a local timezone.
    """
    country = resolve_country(country)
    stamps = pd.DatetimeIndex(pd.to_datetime(index))
    if country == NO_HOLIDAYS or len(stamps) == 0:
        return np.zeros(len(stamps), dtype=np.int64)

    days = stamps.normalize()
    unique_days = pd.DatetimeIndex(days.unique())
    holiday_set = _holiday_dates(unique_days, country)
    return np.asarray(days.isin(list(holiday_set)).astype(np.int64))

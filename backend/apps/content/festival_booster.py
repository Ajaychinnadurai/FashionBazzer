"""
Festival & Sale Event Auto-Boost for FashionBazzer.

Detects upcoming Indian shopping festivals, sales, and seasonal events,
then adjusts posting frequency, keywords, and caption themes automatically.

Commission spikes per plan.md: Diwali/Navratri/EOSS can give 5–10x spikes.
"""
import logging
import random
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Event Severity Levels ──
BOOST_NONE = 0       # No event
BOOST_LOW = 1        # Minor event → 1.2x posting
BOOST_MEDIUM = 2     # Medium event → 1.5x posting, extra keywords
BOOST_HIGH = 3       # Major event → 2x posting, heavy keywords, more scraping
BOOST_PEAK = 4       # Peak event → 3x posting (e.g. Diwali week, BBD, Prime Day)

# ── Indian Shopping Events Calendar ──
# Each event has:
#   month, day, duration_days: approximate date window
#   level: boost severity
#   theme: caption theme prefix
#   keywords: extra product keywords to scrape during this event
#   platforms: which platforms get the boost (None = all)
EVENTS = [
    # ── January ──
    {
        'name': 'New Year Sale 🎉',
        'month': 1, 'day': 1, 'duration_days': 7,
        'level': BOOST_HIGH,
        'theme': 'New Year, New Wardrobe ✨',
        'keywords': ['party dress 2025', 'new year outfit', 'sequin dress', 'party wear'],
    },
    {
        'name': 'Pongal / Sankranti 🌾',
        'month': 1, 'day': 14, 'duration_days': 4,
        'level': BOOST_LOW,
        'theme': 'Festival Special 🌾',
        'keywords': ['ethnic dress', 'traditional wear women'],
    },
    {
        'name': 'Republic Day Sale 🇮🇳',
        'month': 1, 'day': 24, 'duration_days': 4,
        'level': BOOST_MEDIUM,
        'theme': 'Republic Day Offers 🇮🇳',
        'keywords': ['sale dress', 'discount dress', 'clearance'],
    },
    {
        'name': 'EOSS (January) 📉',
        'month': 1, 'day': 20, 'duration_days': 14,
        'level': BOOST_HIGH,
        'theme': 'End of Season Sale 📉',
        'keywords': ['clearance dress', '70% off dress', 'stock clearance'],
    },

    # ── February ──
    {
        'name': 'Valentine\'s Week 💕',
        'month': 2, 'day': 7, 'duration_days': 10,
        'level': BOOST_MEDIUM,
        'theme': 'Valentine\'s Special 💕',
        'keywords': ['date night dress', 'valentine dress', 'romantic dress', 'gift for her'],
    },
    {
        'name': 'Valentine\'s Day ❤️',
        'month': 2, 'day': 14, 'duration_days': 3,
        'level': BOOST_HIGH,
        'theme': 'Valentine\'s Day ❤️',
        'keywords': ['red dress', 'rose dress', 'couple outfit'],
    },

    # ── March ──
    {
        'name': 'Women\'s Day 👩',
        'month': 3, 'day': 6, 'duration_days': 4,
        'level': BOOST_MEDIUM,
        'theme': 'Women\'s Day Special 👩',
        'keywords': ['power dress', 'women dress', 'shein style dress'],
    },
    {
        'name': 'Holi 🌈',
        'month': 3, 'day': 13, 'duration_days': 5,
        'level': BOOST_MEDIUM,
        'theme': 'Holi Special 🌈',
        'keywords': ['white dress', 'colorful dress', 'holi outfit'],
    },
    {
        'name': 'Gudi Padwa / Ugadi 🌸',
        'month': 3, 'day': 28, 'duration_days': 4,
        'level': BOOST_LOW,
        'theme': 'New Beginnings 🌸',
        'keywords': ['ethnic wear', 'traditional dress'],
    },

    # ── April ──
    {
        'name': 'Eid ul-Fitr 🌙',
        'month': 4, 'day': 10, 'duration_days': 5,
        'level': BOOST_HIGH,
        'theme': 'Eid Special 🌙',
        'keywords': ['eid dress', 'festival wear', 'designer dress', 'anarkali'],
    },
    {
        'name': 'Summer Sale ☀️',
        'month': 4, 'day': 15, 'duration_days': 10,
        'level': BOOST_MEDIUM,
        'theme': 'Summer Sale ☀️',
        'keywords': ['summer dress', 'cotton dress', 'flowy dress', 'sun dress'],
    },

    # ── May ──
    {
        'name': 'Summer Vacation 🌴',
        'month': 5, 'day': 1, 'duration_days': 15,
        'level': BOOST_LOW,
        'theme': 'Vacation Mode 🌴',
        'keywords': ['vacation dress', 'beach dress', 'travel outfit'],
    },
    {
        'name': 'Mothers\'s Day 💐',
        'month': 5, 'day': 11, 'duration_days': 3,
        'level': BOOST_LOW,
        'theme': 'Gift for Mom 💐',
        'keywords': ['mom dress', 'ethnic wear', 'comfort dress'],
    },

    # ── June ──
    {
        'name': 'Back to College 🎓',
        'month': 6, 'day': 10, 'duration_days': 15,
        'level': BOOST_MEDIUM,
        'theme': 'College Fashion 🎓',
        'keywords': ['college dress', 'casual dress', 'student budget', 't-shirt dress'],
    },
    {
        'name': 'Amazon Prime Day 🛒',
        'month': 6, 'day': 20, 'duration_days': 3,
        'level': BOOST_PEAK,
        'theme': 'Prime Day Deals 🛒',
        'keywords': ['prime day deal', 'amazon fashion', 'best seller dress'],
    },

    # ── July ──
    {
        'name': 'EOSS (July) 📉',
        'month': 7, 'day': 1, 'duration_days': 20,
        'level': BOOST_HIGH,
        'theme': 'Mid-Year Sale 📉',
        'keywords': ['clearance sale', 'summer clearance', '75% off dress', 'budget dress'],
    },
    {
        'name': 'Raksha Bandhan 🪡',
        'month': 7, 'day': 25, 'duration_days': 5,
        'level': BOOST_LOW,
        'theme': 'Rakhi Special 🪡',
        'keywords': ['ethnic set', 'traditional dress', 'sibling outfit'],
    },

    # ── August ──
    {
        'name': 'Independence Day Sale 🇮🇳',
        'month': 8, 'day': 10, 'duration_days': 6,
        'level': BOOST_MEDIUM,
        'theme': 'Freedom Sale 🇮🇳',
        'keywords': ['tricolor dress', 'patriotic outfit', 'freedom sale'],
    },
    {
        'name': 'Janmashtami 🎵',
        'month': 8, 'day': 24, 'duration_days': 2,
        'level': BOOST_LOW,
        'theme': 'Festive Vibes 🎵',
        'keywords': ['ethnic wear dress', 'traditional outfit'],
    },
    {
        'name': 'Ganesh Chaturthi 🐘',
        'month': 8, 'day': 27, 'duration_days': 5,
        'level': BOOST_LOW,
        'theme': 'Festival Season 🐘',
        'keywords': ['festive dress', 'indian traditional'],
    },

    # ── September ──
    {
        'name': 'Navratri Begins 🪔',
        'month': 9, 'day': 22, 'duration_days': 9,
        'level': BOOST_HIGH,
        'theme': 'Navratri Special 🪔',
        'keywords': ['garba dress', 'chaniya choli', 'navratri outfit', 'ethnic lehenga'],
    },
    {
        'name': 'Durga Puja 🎭',
        'month': 9, 'day': 28, 'duration_days': 6,
        'level': BOOST_HIGH,
        'theme': 'Durga Puja Special 🎭',
        'keywords': ['puja outfit', 'bengali saree', 'festival dress'],
    },

    # ── October ──
    {
        'name': 'Flipkart Big Billion Days 💥',
        'month': 10, 'day': 5, 'duration_days': 7,
        'level': BOOST_PEAK,
        'theme': 'Billion Days Sale 💥',
        'keywords': ['big billion deal', 'festival offer', 'bestseller dress'],
    },
    {
        'name': 'Amazon Great Indian Festival 🎊',
        'month': 10, 'day': 12, 'duration_days': 10,
        'level': BOOST_PEAK,
        'theme': 'Great Indian Festival 🎊',
        'keywords': ['festival deal', 'amazon top rated', 'festival collection'],
    },
    {
        'name': 'Diwali Prep 🪔',
        'month': 10, 'day': 20, 'duration_days': 7,
        'level': BOOST_HIGH,
        'theme': 'Diwali Shopping 🪔',
        'keywords': ['diwali dress', 'festival wear', 'ethnic dress', 'party wear diwali'],
    },

    # ── November ──
    {
        'name': 'Diwali Week 🪔✨',
        'month': 11, 'day': 1, 'duration_days': 7,
        'level': BOOST_PEAK,
        'theme': 'Happy Diwali 🪔✨',
        'keywords': ['diwali special', 'festival collection', 'luxury dress', 'diwali outfit'],
    },
    {
        'name': 'Bhhai Dooj 👫',
        'month': 11, 'day': 10, 'duration_days': 2,
        'level': BOOST_LOW,
        'theme': 'Festival Love 👫',
        'keywords': ['family outfit', 'matching dress'],
    },
    {
        'name': 'Black Friday 🖤',
        'month': 11, 'day': 25, 'duration_days': 4,
        'level': BOOST_HIGH,
        'theme': 'Black Friday Sale 🖤',
        'keywords': ['black friday deal', 'flash sale dress', 'steal deal'],
    },
    {
        'name': 'Cyber Monday 💻',
        'month': 11, 'day': 29, 'duration_days': 3,
        'level': BOOST_MEDIUM,
        'theme': 'Cyber Monday Deals 💻',
        'keywords': ['online deal', 'cyber sale dress', 'digital offer'],
    },

    # ── December ──
    {
        'name': 'Christmas Sale 🎄',
        'month': 12, 'day': 20, 'duration_days': 7,
        'level': BOOST_HIGH,
        'theme': 'Christmas Special 🎄',
        'keywords': ['christmas dress', 'party dress', 'red dress', 'winter outfit'],
    },
    {
        'name': 'New Year Countdown 🥂',
        'month': 12, 'day': 28, 'duration_days': 5,
        'level': BOOST_HIGH,
        'theme': 'New Year Party 🥂',
        'keywords': ['new year party dress', 'sequin dress', 'midnight outfit'],
    },

    # ── Wedding Season (Nov-Feb, always ongoing) ──
    {
        'name': 'Wedding Season 💍',
        'month': 11, 'day': 15, 'duration_days': 100,  # Nov 15 → Feb 23
        'level': BOOST_MEDIUM,
        'theme': 'Wedding Guest Special 💍',
        'keywords': ['wedding guest dress', 'reception dress', 'mehendi outfit', 'sangeet dress'],
    },
]


class FestivalBooster:
    """
    Detects active and upcoming Indian shopping events and provides
    boost multipliers, themed caption hints, and extra keywords.
    """

    def __init__(self):
        self._cache: Optional[Dict] = None
        self._cache_date: Optional[date] = None

    def _get_active_events(self, check_date: Optional[date] = None) -> List[Dict]:
        """
        Return all events that are active on `check_date` (defaults to today).
        An event is active if `check_date` falls within its date window.
        Also checks the previous year for year-boundary events
        (e.g. Wedding Season Nov 15 → Feb 23 should be active in January).
        """
        if check_date is None:
            check_date = date.today()

        active = []
        for event in EVENTS:
            try:
                # Check current year version of the event
                event_start = date(check_date.year, event['month'], event['day'])
                event_end = event_start + timedelta(days=event['duration_days'])

                if event_start <= check_date <= event_end:
                    active.append(event)
                    continue

                # Check previous year for events that span into the new year
                # Only needed Jan-Mar when year-boundary events (Nov start, 100d+)
                # could still be active from the prior year.
                prev_start = date(check_date.year - 1, event['month'], event['day'])
                prev_end = prev_start + timedelta(days=event['duration_days'])
                if prev_start <= check_date <= prev_end:
                    active.append(event)
            except ValueError:
                logger.warning(f"Skipping invalid event date: {event.get('name')}")
                continue

        return active

    def _get_upcoming_events(self, days_ahead: int = 7, check_date: Optional[date] = None) -> List[Dict]:
        """
        Return events starting within the next `days_ahead` days.
        Useful for pre-heating scraping keywords.
        """
        if check_date is None:
            check_date = date.today()

        upcoming = []
        for i in range(1, days_ahead + 1):
            future_date = check_date + timedelta(days=i)
            for event in EVENTS:
                try:
                    event_start = date(future_date.year, event['month'], event['day'])
                    if event_start == future_date:
                        upcoming.append(event)
                except ValueError:
                    continue

        return upcoming

    def get_boost_info(self, check_date: Optional[date] = None) -> Dict:
        """
        Get the current boost information.

        Returns a dict with:
          - level: 0–4 boost level
          - multiplier: posting frequency multiplier (1.0 normal, 2.0 for peak)
          - events: list of active event names
          - theme: caption theme for the top active event (or None)
          - extra_keywords: combined keywords from active events
          - next_event: name + days until next upcoming event
        """
        if check_date is None:
            check_date = date.today()

        # Use cache if called multiple times in the same day
        if self._cache is not None and self._cache_date == check_date:
            return self._cache

        active_events = self._get_active_events(check_date)
        upcoming_events = self._get_upcoming_events(days_ahead=7, check_date=check_date)

        # Determine boost level (use highest level among active events)
        level = BOOST_NONE
        if active_events:
            level = max(e['level'] for e in active_events)

        # Calculate multiplier from level
        multiplier_map = {
            BOOST_NONE: 1.0,
            BOOST_LOW: 1.2,
            BOOST_MEDIUM: 1.5,
            BOOST_HIGH: 2.0,
            BOOST_PEAK: 3.0,
        }
        multiplier = multiplier_map.get(level, 1.0)

        # Combine keywords and themes
        all_keywords = set()
        themes = []
        for event in active_events:
            all_keywords.update(event.get('keywords', []))
            if event.get('theme'):
                themes.append(event['theme'])

        # If no active events, suggest prep keywords for upcoming
        if not active_events and upcoming_events:
            for event in upcoming_events:
                all_keywords.update(event.get('keywords', []))

        # Next event info
        next_event_info = None
        for i in range(1, 31):
            future_date = check_date + timedelta(days=i)
            upcoming_on_date = []
            for event in EVENTS:
                try:
                    event_start = date(future_date.year, event['month'], event['day'])
                    if event_start == future_date:
                        upcoming_on_date.append(event)
                except ValueError:
                    continue
            if upcoming_on_date:
                next_event_info = {
                    'name': upcoming_on_date[0]['name'],
                    'days_until': i,
                    'level': upcoming_on_date[0]['level'],
                }
                break

        result = {
            'level': level,
            'multiplier': multiplier,
            'events': [e['name'] for e in active_events],
            'theme': themes[0] if themes else None,
            'all_themes': themes,
            'extra_keywords': list(all_keywords),
            'has_active_boost': level > BOOST_NONE,
            'is_peak': level >= BOOST_PEAK,
            'next_event': next_event_info,
            'active_event_count': len(active_events),
        }

        # Cache for the day
        self._cache = result
        self._cache_date = check_date

        return result

    def get_caption_theme(self, check_date: Optional[date] = None) -> Optional[str]:
        """Get the current event-based caption theme, or None if no event."""
        info = self.get_boost_info(check_date)
        return info.get('theme')

    def get_caption_themed_season(self, check_date: Optional[date] = None) -> str:
        """Return a season label for caption templates during events."""
        info = self.get_boost_info(check_date)
        if info['theme']:
            return info['theme']
        # Fall back to default seasons based on month
        month = (check_date or date.today()).month
        season_map = {
            3: 'Spring Vibes 🌸', 4: 'Summer Chic ☀️', 5: 'Summer Chic ☀️',
            6: 'Monsoon Magic 🌧️', 7: 'Monsoon Magic 🌧️', 8: 'Monsoon Magic 🌧️',
            9: 'Festival Season 🪔', 10: 'Festival Season 🪔', 11: 'Festival Season 🪔',
            12: 'Winter Glam ❄️', 1: 'Winter Glam ❄️', 2: 'Spring Vibes 🌸',
        }
        return season_map.get(month, 'Seasonal Style ✨')

    def get_extra_scraping_keywords(self, check_date: Optional[date] = None) -> List[str]:
        """Get extra product keywords to scrape during active events."""
        info = self.get_boost_info(check_date)
        return info.get('extra_keywords', [])

    def get_boosted_post_limit(self, base_limit: int, check_date: Optional[date] = None) -> int:
        """
        Calculate how many posts to fetch based on the current boost level.
        E.g. base_limit=5 with 2x multiplier → returns 10.
        """
        info = self.get_boost_info(check_date)
        return max(base_limit, int(base_limit * info['multiplier']))

    def get_boosted_queue_threshold(self, check_date: Optional[date] = None) -> int:
        """
        Return the "low queue" threshold for auto-triggering content generation.
        Lower during events to keep the pipeline fuller.
        """
        info = self.get_boost_info(check_date)
        # Normal threshold = 15, during peak = 30
        base = 15
        if info['is_peak']:
            return 30
        elif info['level'] >= BOOST_HIGH:
            return 25
        elif info['level'] >= BOOST_MEDIUM:
            return 20
        return base

    def get_event_log_line(self, check_date: Optional[date] = None) -> str:
        """Get a one-line log message describing the current event status."""
        info = self.get_boost_info(check_date)
        if info['has_active_boost']:
            events_str = ', '.join(info['events'])
            return f"🎉 ACTIVE BOOST: {'{:.1f}x'.format(info['multiplier'])} | Events: {events_str}"
        elif info['next_event']:
            next_ = info['next_event']
            return f"📅 Next event: {next_['name']} in {next_['days_until']}d"
        return "No events active"

    def get_seasonal_hashtags(self, check_date: Optional[date] = None) -> List[str]:
        """Get event-specific hashtags for social media posts."""
        info = self.get_boost_info(check_date)
        event_hashtags = {
            'Diwali': ['#DiwaliFashion', '#FestivalSale', '#DiwaliOutfit'],
            'Navratri': ['#NavratriFashion', '#GarbaOutfit', '#FestivalWear'],
            'Christmas': ['#ChristmasFashion', '#PartyDress', '#WinterOutfit'],
            'New Year': ['#NewYearDress', '#Party2025', '#NewYearOutfit'],
            'Eid': ['#EidFashion', '#EidOutfit', '#FestivalWear'],
            'Valentine': ['#ValentinesDay', '#DateNightOutfit', '#LoveFashion'],
            'Holi': ['#HoliSpecial', '#ColorfulOutfit', '#FestivalVibes'],
            'EOSS': ['#EOSSale', '#ClearanceSale', '#BudgetFashion'],
            'Sale': ['#SaleAlert', '#DiscountFashion', '#DealDress'],
            'Wedding': ['#WeddingGuest', '#WeddingOutfit', '#ReceptionLook'],
            'College': ['#CollegeFashion', '#BackToCollege', '#StudentStyle'],
            'Prime Day': ['#PrimeDay', '#AmazonFashion', '#DealFinder'],
            'Billion Days': ['#BigBillionDays', '#FlipkartSale', '#FestivalDeals'],
            'Black Friday': ['#BlackFridayDeals', '#FashionSteals', '#CyberSale'],
        }
        hashtags = []
        for event in info['events']:
            for key, tags in event_hashtags.items():
                if key.lower() in event.lower():
                    hashtags.extend(tags)
        return list(set(hashtags)) or ['#FashionBazzer', '#TrendingFashion']


# ── Module-level singleton ──
_booster: Optional[FestivalBooster] = None


def get_booster() -> FestivalBooster:
    """Get the global FestivalBooster singleton."""
    global _booster
    if _booster is None:
        _booster = FestivalBooster()
    return _booster


# ── Quick-access helpers ──

def get_current_multiplier() -> float:
    """Get the current posting frequency multiplier."""
    return get_booster().get_boost_info()['multiplier']


def should_boost() -> bool:
    """Check if any event boost is currently active."""
    return get_booster().get_boost_info()['has_active_boost']


def get_current_theme() -> Optional[str]:
    """Get current event caption theme."""
    return get_booster().get_caption_theme()


def get_boosted_limit(base_limit: int) -> int:
    """Get the boosted post limit for the current event."""
    return get_booster().get_boosted_post_limit(base_limit)

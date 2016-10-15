import bisect

# TODO, lookup method that returns channel info on band letter/number lookup
# eg. get_channel('E5')

class Channel:
    """Hold information about a channel"""

    def __init__(self, number, frequency, band):
        self.band = band
        self.number = number
        self.frequency = frequency

    def __str__(self):
        return "{}{} ({}Mhz)".format(
            self.band.band_char.upper(), self.number, self.frequency)

    def __repr__(self):
        return str(self)

    # methods for comparing channels and seeing if they are higher/lower than
    # others and if they're close

    def __eq__(self, other):
        return self.frequency == other.frequency

    def __ne__(self, other):
        return self.frequency != other.frequency

    def __lt__(self, other):
        return self.frequency < other.frequency

    def __gt__(self, other):
        return self.frequency > other.frequency

    def __le__(self, other):
        return self.frequency <= other.frequency

    def __ge__(self, other):
        return self.frequency >= other.frequency

    def is_channel_close(self, other):
        other_freq = other.frequency
        separation = 80
        return (other_freq - separation) <= self.frequency <= (other_freq + separation)

    def seperation_power(self, other):
        diff = abs(other.frequency - self.frequency)
        return abs(1 - min(1, (diff / 200)))


class ChannelRegistry:
    def __init__(self):
        self.channels = []

    def add_channel(self, channel):
        # ascending list of channels by frequency
        bisect.insort_left(self.channels, channel)

    def farthest_from(self, channel):
        pass
        # TODO: may be helpful?


class Band:
    """All frequencies are in Mhz"""

    def __init__(
            self, band_char, start, end, *args, long_name=None, registry=None,
            channel_count=8, **kwargs):
        assert isinstance(start, int), 'start frequency must be an integer'
        assert isinstance(end, int), 'end frequency must be an integer'
        self.channel_count = channel_count
        self.registry = registry
        self.band_char = band_char
        self.start = start
        self.end = end
        self.long_name = long_name
        self.ascending = (end > start)
        self.separation = int(abs((self.start - self.end) / (self.channel_count - 1)))
        self.channels = []
        self.build_channels()

    def build_channels(self):
        for channel in range(self.channel_count):
            frequency_offset = (self.separation * channel)
            if self.ascending:
                frequency = self.start + frequency_offset
            else:
                frequency = self.start - frequency_offset
            channel = Channel(channel+1, frequency, self)
            if self.registry:
                self.registry.add_channel(channel)
            # Locally store this band's channels in the order they're made
            self.channels.append(channel)

    def __str__(self):
        return "{} {}".format(self.band_char, self.long_name)


# DBM to mW conversion

from bands import ChannelRegistry, Band


channel_registry = ChannelRegistry()


# Build our bands and channels
band_a = Band('a', 5865, 5725, registry=channel_registry)
band_b = Band('b', 5733, 5866, registry=channel_registry)
band_c = Band('c', 5705, 5945, registry=channel_registry)
band_f = Band('f', 5740, 5880, long_name='Fatshark', registry=channel_registry)
band_e = Band('e', 5658, 5917, long_name='Raceband', registry=channel_registry)


all_channels = channel_registry.channels

# test seperation of power calculation
for channel in all_channels:
    for in_channel in all_channels:
        print(channel, in_channel)
        print(channel.seperation_power(in_channel))
        print(channel.is_channel_close(in_channel))

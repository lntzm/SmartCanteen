import statistics as stat
import time
import RPi.GPIO as GPIO


class HX711:
    def __init__(self, dout_pin: int, pd_sck_pin: int,
                 offset: float = 0.0, ratio: float = 1.0):
        """
        Args:
            dout_pin(int): Raspberry Pi pin number where the Data pin of HX711 is connected.
            pd_sck_pin(int): Raspberry Pi pin number where the Clock pin of HX711 is connected.
        """
        self._pd_sck = pd_sck_pin
        self._dout = dout_pin
        self._offset = offset       # offset
        self._scale_ratio = ratio   # scale ratio
        self._last_raw_data = 0
        self._data_filter = outliers_filter  # default it is used outliers_filter

        GPIO.setup(self._pd_sck, GPIO.OUT)  # pin _pd_sck is output only
        GPIO.setup(self._dout, GPIO.IN)  # pin _dout is input only

        # after changing channel or gain it has to wait 500 ms to allow adjustment.
        # the data before is garbage and cannot be used.
        self._read()
        time.sleep(0.5)

    def correct_offset_ratio(self, times:int=10):
        input("第一次，放置好去皮的物品（空盘子），回车:")
        result = self.get_raw_data_mean(times)
        if result != False:
            self._offset = result
        else:
            raise ValueError('get_raw_data_mean(times) returned False.')
        known_weight = input("第二次，去皮的基础上放置好已知重量的物品，输入该物品重量(g)并回车:")
        known_weight = float(known_weight)
        reading = self.get_raw_data_mean(times)
        if result != False:
            self._scale_ratio = (reading - self._offset) / known_weight
        else:
            raise ValueError('get_raw_data_mean(times) returned False.')
        print("set offset: {}, scale ratio: {}".format(self._offset, self._scale_ratio))

    def set_offset(self, offset: float):
        self._offset = offset

    def set_scale_ratio(self, scale_ratio):
        self._scale_ratio = scale_ratio

    def set_data_filter(self, data_filter):
        """
        set_data_filter method sets data filter that is passed as an argument.

        Args:
            data_filter(data_filter): Data filter that takes list of int numbers and
                returns a list of filtered int numbers.

        Raises:
            TypeError: if filter is not a function.
        """
        if callable(data_filter):
            self._data_filter = data_filter
        else:
            raise TypeError('Parameter "data_filter" must be a function. '
                            'Received: {}'.format(data_filter))

    def _save_last_raw_data(self, data):
        """
        _save_last_raw_data saves the last raw data for specific channel and gain.
        """
        self._last_raw_data = data

    def _ready(self):
        """
        _ready method check if data is prepared for reading from HX711

        Returns: bool True if ready else False when not ready        
        """
        # if DOUT pin is low data is ready for reading
        return True if GPIO.input(self._dout) == 0 else False

    def _set_channel_gain(self):
        """
        _set_channel_gain is called only from _read method.
        It finishes the data transmission for HX711 which sets
        the next required gain and channel.

        Returns: bool True if HX711 is ready for the next reading
            False if HX711 is not ready for the next reading
        """
        start_counter = time.perf_counter()
        GPIO.output(self._pd_sck, True)
        GPIO.output(self._pd_sck, False)
        end_counter = time.perf_counter()
        # check if hx 711 did not turn off...
        if end_counter - start_counter >= 0.00006:
            # if pd_sck pin is HIGH for 60 us and more than the HX 711 enters power down mode.
            print('Not enough fast while setting gain and channel')
            print('Time elapsed: {}'.format(end_counter - start_counter))
            # hx711 has turned off. First few times are inaccurate.
            # Despite it, this reading was ok and data can be used.
            result = self.get_raw_data_mean(6)  # set for the next reading.
            if result == False:
                return False
        return True

    def _read(self):
        """
        _read method reads bits from hx711, converts to INT
        and validate the data.

        Returns: (bool || int) if it returns False then it is false reading.
            if it returns int then the reading was correct
        """
        GPIO.output(self._pd_sck, False)  # start by setting the pd_sck to 0
        ready_counter = 0
        while (not self._ready() and ready_counter <= 40):
            time.sleep(0.01)  # sleep for 10 ms because data is not ready
            ready_counter += 1
            if ready_counter == 50:  # if counter reached max value then return False
                print('self._read() not ready after 40 trials\n')
                return False

        # read first 24 bits of data
        data_in = 0  # 2's complement data from hx 711
        for _ in range(24):
            start_counter = time.perf_counter()
            # request next bit from hx 711
            GPIO.output(self._pd_sck, True)
            GPIO.output(self._pd_sck, False)
            end_counter = time.perf_counter()
            # check if the hx 711 did not turn off...
            if end_counter - start_counter >= 0.00006:
                # if pd_sck pin is HIGH for 60 us and more than the HX 711 enters power down mode.
                print('Not enough fast while reading data')
                print('Time elapsed: {}'.format(end_counter - start_counter))
                return False
            # Shift the bits as they come to data_in variable.
            # Left shift by one bit then bitwise OR with the new bit.
            data_in = (data_in << 1) | GPIO.input(self._dout)

        if not self._set_channel_gain():  # send only one bit which is 1
            return False  # return False because channel was not set properly

        # print('Binary value as received: {}\n'.format(bin(data_in)))

        # check if data is valid
        if (data_in == 0x7fffff
                or  # 0x7fffff is the highest possible value from hx711
                data_in == 0x800000
            ):  # 0x800000 is the lowest possible value from hx711
            # print('Invalid data detected: {}\n'.format(data_in))
            return False  # return false because the data is invalid

        # calculate int from 2's complement
        signed_data = 0
        # 0b1000 0000 0000 0000 0000 0000 check if the sign bit is 1. Negative number.
        if (data_in & 0x800000):
            signed_data = -(
                (data_in ^ 0xffffff) + 1)  # convert from 2's complement to int
        else:  # else do not do anything the value is positive number
            signed_data = data_in

        # print('Converted 2\'s complement value: {}\n'.format(signed_data))

        return signed_data

    def get_raw_data_mean(self, times=10):
        """
        get_raw_data_mean returns mean value of times.

        Args:
            times(int): Number of times for mean.

        Returns: (bool || int) if False then reading is invalid.
            if it returns int then reading is valid
        """
        data_list = []
        # do required number of times
        for _ in range(times):
            data_list.append(self._read())
        data_mean = False
        if times > 2 and self._data_filter:
            filtered_data = self._data_filter(data_list)
            # print('data_list: {}'.format(data_list))
            # print('filtered_data list: {}'.format(filtered_data))
            # print('data_mean:', stat.mean(filtered_data))
            data_mean = stat.mean(filtered_data)
        else:
            data_mean = stat.mean(data_list)
        self._save_last_raw_data(data_mean)
        return int(data_mean)

    # def get_data_mean(self, times=10):
    #     """
    #     get_data_mean returns average value of times minus
    #     offset for the channel which was read.

    #     Args:
    #         times(int): Number of times for mean

    #     Returns: (bool || int) False if reading was not ok.
    #         If it returns int then reading was ok
    #     """
    #     result = self.get_raw_data_mean(times)
    #     if result != False:
    #         return result - self._offset
    #     else:
    #         return False

    def get_weight_mean(self, times=10):
        """
        get_weight_mean returns average value of times minus
        offset divided by scale ratio for a specific channel
        and gain.

        Args:
            times(int): Number of times for mean

        Returns: (bool || float) False if reading was not ok.
            If it returns float then reading was ok
        """
        result = self.get_raw_data_mean(times)
        if result != False:
            return int((result - self._offset) / self._scale_ratio)
        else:
            return False

    def get_last_raw_data(self):
        return self._last_raw_data

    def get_current_offset(self, channel='', gain_A=0):
        return self._offset

    def get_current_scale_ratio(self, channel='', gain_A=0):
        return self._scale_ratio

    def power_down(self):
        """
        power down method turns off the hx711.
        """
        GPIO.output(self._pd_sck, False)
        GPIO.output(self._pd_sck, True)
        time.sleep(0.01)

    def power_up(self):
        """
        power up function turns on the hx711.
        """
        GPIO.output(self._pd_sck, False)
        time.sleep(0.01)

    def reset(self):
        """
        reset method resets the hx711 and prepare it for the next reading.

        Returns: True if error encountered
        """
        self.power_down()
        self.power_up()
        result = self.get_raw_data_mean(6)
        if result:
            return False
        else:
            return True


def outliers_filter(data_list):
    """
    It filters out outliers from the provided list of int.
    Median is used as an estimator of outliers.

    Args:
        data_list([int]): List of int. It can contain Bool False that is removed.

    Returns: list of filtered data. Excluding outliers.
    """
    data = []
    for num in data_list:
        if num:
            data.append(num)
    # set 'm' to lower value to remove more outliers
    # set 'm' to higher value to keep more data samples (also some outliers)
    m = 2.0
    # It calculates the absolute distance to the median.
    # Then it scales the distances by their median value (again)
    # so they are on a relative scale to 'm'.
    data_median = stat.median(data)
    abs_distance = []
    for num in data:
        abs_distance.append(abs(num - data_median))
    mdev = stat.median(abs_distance)
    s = []
    if mdev:
        for num in abs_distance:
            s.append(num / mdev)
    else:
        # mdev is 0. Therefore all data samples in the list data have the same value.
        return data
    filtered_data = []
    for i in range(len(data)):
        if s[i] < m:
            filtered_data.append(data[i])
    return filtered_data

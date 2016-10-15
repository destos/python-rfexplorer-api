import logging
import serial
import time

from exceptions import (
    RFEAlreadyConnected,
    RFEAlreadyDisconnected,
    RFERestartException
)
import commands


logger = logging.getLogger(__name__)


class RFExplorer(object):
    baudrate = 500000
    connection_timeout = 2

    def __init__(self, port, **kwargs):
        self.serial_port = serial.Serial(
            port, self.baudrate, timeout=self.connection_timeout)
        logger.info('opening connection to {!s}'.format(self.serial_port))

    def reset_state(self):
        pass

    @property
    def connected(self):
        return self.serial_port.is_open

    def connect(self):
        # if self.connected:
        #     raise RFEAlreadyConnected('already connected to RFExplorer')
        self.stop()
        logger.info('sending GO command')
        self.send_command(commands.GO)

    def get_config(self):
        try:
            # skipps non config lines. Is there a way to do this more pythonically?
            while not self.serial_port.readline().startswith(b'$S'):
                return self.parse_line(self.serial_port.readline())
        except ValueError:
            # TOOD catch things
            print('wat')

    def disconnect(self):
        """
        just a clean disconnect
        """
        if not self.connected:
            raise RFEAlreadyDisconnected('already disconnected from RFExplorer')
        self.stop()
        self.serial_port.close()

    def stop(self):
        if self.connected:
            logger.info('sending stop command')
            self.send_command(commands.STOP)
            time.sleep(0.25)
            self.serial_port.flushOutput()
            self.serial_port.flushInput()
            self.serial_port.readline()
            return True
        return False

    def parse_line(self, line):
        """
        given the line, determine what to do with it.
        A #C2-M is just an initializer so do nothing
        A #C2-F is what needs to be parsed into a 112 step frequency list
        A $S is valid data
        """
        # TODO: maybe handle parsing differently as it returns many different types of objects

        # first figure out what we are dealing with
        if line.startswith(b'#C2-M'):
            # TODO: what type of line is this?
            line = self.ser.readline()

        if line.startswith(b'#C2-F'):
            freq_list = self.parse_C2F(line)
            return freq_list
        elif line.startswith(b'$S'):
            return self.parse_valid_data(line)
        elif line.startswith(b'Restart'):
            # TODO do some logging?
            # self.errorLog.append(line)
            # return 'Restart'
            raise RestartException()
        else:
            raise ValueError('Not a valid response, ({:s})'.format(line))

    def parse_C2F(self, line):
        """
        creates the 112 frequency list
        if you select a 100-112Mhz span in your example the sweep scan step is:
            (112-100)/112 = 12/112 = 0.107Mhz = 107Khz.
            For that each scan point will be 100.0, 100.107, 100.214, etc.
        Example:
            '#C2-F:0507000,0017857,-010,-100,0112,1,000,0015000,2700000,0100000,00018,-001\r\n'
            #C2-F:<Start_Freq>,
                <Freq_Step>,
                <Amp_Top>,
                <Amp_Bottom>,
                <Sweep_Steps>,
                <ExpModuleActive>,
                <CurrentMode>,
                <Min_Freq>,
                <Max_Freq>,
                <Max_Span>,
                <RBW>,
                <AmpOffset>,
                <CalculatorMode>
                <EOL>
            '#C2-F:0507000,0017857,-010,-100,0112,1,000,0015000,2700000,0100000,00018,-001\r\n'

            #C2-F:0691200,0050000,-036,-101,0112,0,000,0240000,0960000,0600000,00048,-001,000\r\n'
        """
        config = self.parse_config(line)

        make_hz = lambda freq: freq * 1000
        round_freq = lambda freq: round(make_hz(freq / 1000))

        start_freq_hz = make_hz(config['start_freq'])
        sweep_steps = config['sweep_steps']
        freq_step = config['freq_step']

        span = make_hz((freq_step * sweep_steps) / 1000)
        end_freq = span + start_freq_hz
        center_freq = start_freq_hz + (span / 2)

        freq_list = [start_freq_hz + round_freq(step_num * freq_step) for step_num in range(sweep_steps)]

        return freq_list

    def parse_config(self, config):

        request_config = config.split(b':')

        key_parts = (
            'start_freq',
            'freq_step',
            'amp_top',
            'amp_bottom',
            'sweep_steps',
            'exp_module_active',
            'current_mode',
            'min_freq',
            'max_freq',
            'max_span',
            'rbw',
            'amp_offset',
            'calculator_mode'
            'eol'
        )

        if request_config[0] != b'#C2-F':  # Current_Config key
            raise NameError("C2F value is not present in the serial port's queue")

        # split values
        values = request_config[1].split(b',')

        return {key_parts[i]: int(value) for i, value in enumerate(values)}

    def parse_valid_data(self, line):
        """
        returns a list of values that correspond with self.freq_list

        Line must start with '$S'
        """
        # if self.freq_list == None:
        #     raise ValueError('Restart collection, there is no corresponding freq_list')

        results = line.split(b'$Sp')[1]
        itemCount = 0

        separated = []

        # Take off the carriage and newline at the end
        results = results[:-2]

        if len(results) != 112:
            # TODO: exception?
            return 'NOT 112'

        final_results = []

        for result in results:
            result = result / -2.0  # convert to dBm
            final_results.append(result)

        return final_results

    def send_command(self, command):
        command = bytes(command, 'utf-8')
        self.serial_port.write(command)

    # Sweep commands

    def send_sweep_params(self, start_freq, end_freq, amp_top, amp_bottom):
        """
        Args:
            self
            start_freq: max 7 digit value in kHz. Can be between 0240000 and 0959888
            end_freq: 7 digit value in kHz. Can be between 0241112 and 0960000
            amp_top: 4 digit value in dBm include the +/- sign. Between -110 and +005
            amp_bottom: 4 digit value in dBm include the +/- sign. Between -120 and -005
        Returns:
            boolean: True designates a successful change of parameters
        Raises:
            ValueError: Incorrect Value submitted
            ValueError: Length of Value is not correct
            ValueError: Write to RFE Failed

        """
        assert isinstance(start_freq, int)
        assert isinstance(end_freq, int)
        assert isinstance(amp_top, int)
        assert isinstance(amp_bottom, int)

        if start_freq < 240000 or start_freq > 959888:
            raise ValueError("start_freq not in bounds")
        if end_freq < 241112 or end_freq > 960000:
            raise ValueError("end_freq not in bounds")
        if amp_top < -110 or amp_top > 5:
            raise ValueError("amp_top not in bounds")
        if amp_bottom < -120 or amp_bottom > -5:
            raise ValueError("amp_bottom not in bounds")

        # start_freq = str(start_freq)
        # end_freq = str(end_freq)
        # amp_top = str(amp_top)
        # amp_bottom = str(amp_bottom)
        # Use format fill here

        # if len(start_freq) < 7:
        #     sf_0 = 7-len(start_freq)
        #     start_freq = ('0'*sf_0) + start_freq
        # if len(end_freq) < 7:
        #     ef_0 = 7-len(end_freq)
        #     end_freq = ('0'*sf_0) + end_freq
        # if len(amp_top) != 4:
        #     raise ValueError("length of amp_top is not 4")

        params = "#{}C2-F:{:0=#7},{:0=#7},{:0=+#4},{:0=+#4}".format(
            chr(0x20), start_freq, end_freq, amp_top, amp_bottom)
        print(params)
        # sweep_params = '#'+chr(0x20)+'C2-F:'+start_freq+','+end_freq+','+amp_top+','+amp_bottom
        try:
            self.send_command(params)
            # TODO: there should be a check here that self.C2F gets set and freqlist gets set
            while not self.serial_port.readline().startswith(b'$'):
                print(self.parse_line(self.serial_port.readline()))
            return True
        except Exception as e:
            raise e
            raise ValueError("write to RFExplorer failed")

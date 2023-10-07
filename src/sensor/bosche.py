import smbus2 as smbus

# I2C address of BME280 sensor
I2C_ADDR = 0x76

# Register addresses for BME280 sensor
BME280_REGISTER_DIG_T1 = 0x88
BME280_REGISTER_PRESSURE_DATA = 0xF7
BME280_REGISTER_HUMIDITY_DATA = 0xFD

DIG_T, DIG_P, DIG_H = [], [], []

class BME280:
    """
    BME280 sensor class for reading temperature, pressure and humidity data.

    The BME280 sensor communicates with the Raspberry Pi over the I2C protocol 
    by using the smbus library. 
    """


    def __init__(self, address=I2C_ADDR):
        self.i2c = smbus.SMBus(1)
        
        self.address = address
        self.calib = []
        self.osrs_t = 1		# Temperature oversampling x 1
        self.osrs_p = 1		# Pressure oversampling x 1
        self.osrs_h = 1		# Humidity oversampling x 1
        self.mode   = 3		# Normal self.mode
        self.t_sb   = 5		# Tstandby 1000ms
        self.filter = 0		# self.filter off
        self.spi3w_en = 0   # 3-wire SPI Disable
        self.t_fine = 0.0

        ctrl_meas_reg = (self.osrs_t << 5) | (self.osrs_p << 2) | self.mode
        config_reg    = (self.t_sb << 5) | (self.filter << 2) | self.spi3w_en
        ctrl_hum_reg  = self.osrs_h

        self.write_register(0xF2, ctrl_hum_reg)
        self.write_register(0xF4, ctrl_meas_reg)
        self.write_register(0xF5, config_reg)
        
        self.get_calib_param()

    def write_register(self, reg_address, data):
        """
        Writes data to the specified register address.
        """
        self.i2c.write_byte_data(self.address, reg_address, data)
    

    def get_calib_param(self):
        """
        Read calibration parameters from the BME280 registers and store in
        corresponding 'DIG_T', 'DIG_P' and 'DIG_H' lists.

        Each compensation word is a 16-bit signed or unsigned integer value 
        stored in two's complement. As the memory is organized into 8-bit words, 
        two words must always be combined in order to represent the compensation 
        word.

        The 8-bit registers are named calib00…calib41 and are stored at memory 
        addresses 0x88…0xA1 and 0xE1…0xE7. The corresponding compensation words 
        are named dig_T# for temperature compensation related values, dig_P# 
        for pressure related values and dig_H# for humidity related values.
        """
        for i in range (0x88, 0xA1):
            self.calib.append(self.i2c.read_byte_data(self.address, i))

        for i in range (0xE1, 0xE8):
            self.calib.append(self.i2c.read_byte_data(self.address, i))

        ## Construct the calibration words ##

        # temperature
        DIG_T.append((self.calib[1] << 8) | self.calib[0])
        DIG_T.append((self.calib[3] << 8) | self.calib[2])
        DIG_T.append((self.calib[5] << 8) | self.calib[4])

        # pressure
        DIG_P.append((self.calib[7] << 8) | self.calib[6])
        DIG_P.append((self.calib[9] << 8) | self.calib[8])
        DIG_P.append((self.calib[11]<< 8) | self.calib[10])
        DIG_P.append((self.calib[13]<< 8) | self.calib[12])
        DIG_P.append((self.calib[15]<< 8) | self.calib[14])
        DIG_P.append((self.calib[17]<< 8) | self.calib[16])
        DIG_P.append((self.calib[19]<< 8) | self.calib[18])
        DIG_P.append((self.calib[21]<< 8) | self.calib[20])
        DIG_P.append((self.calib[23]<< 8) | self.calib[22])

        # humidity
        DIG_H.append(self.calib[24])
        DIG_H.append((self.calib[26]<< 8) | self.calib[25])
        DIG_H.append(self.calib[27])
        DIG_H.append((self.calib[28]<< 4) | (0x0F & self.calib[29]))
        DIG_H.append((self.calib[30]<< 4) | ((self.calib[29] >> 4) & 0x0F))
        DIG_H.append(self.calib[31])
        
        # convert signed numbers to unsigned numbers 
        for i in range(1, 2):
            if DIG_T[i] & 0x8000:
                DIG_T[i] = (-DIG_T[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if DIG_P[i] & 0x8000:
                DIG_P[i] = (-DIG_P[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if DIG_H[i] & 0x8000:
                DIG_H[i] = (-DIG_H[i] ^ 0xFFFF) + 1  


    def read_data(self):
        """
        Reads raw sensor data for pressure, temperature, and humidity from I2C 
        registers. It then calls 'compensate_P', 'compensate_T', and 'compensate_H' 
        functions to get compensated sensor readings.
        """
    
        data = [self.i2c.read_byte_data(self.address, i) for i in range(0xF7, 0xFF)]

        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw  = (data[6] << 8)  |  data[7]
        
        pressure = self.compensate_P(pres_raw)
        temperature = self.compensate_T(temp_raw)
        humidity = self.compensate_H(hum_raw)

        return pressure, temperature, humidity


    def compensate_P(self, adc_P):
        """
        Reads raw pressure reading 'adc_P' as input and returns the compensated 
        pressure reading by using the calibration data 'DIG_P' and a series of 
        calculations.
        """

        pressure = 0.0        
        v1 = (self.t_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * DIG_P[5]
        v2 = v2 + ((v1 * DIG_P[4]) * 2.0)
        v2 = (v2 / 4.0) + (DIG_P[3] * 65536.0)
        v1 = ((((DIG_P[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + 
               ((DIG_P[1] * v1) / 2.0)) / 262144
               )
        v1 = ((32768 + v1) * DIG_P[0]) / 32768
        
        if v1 == 0:
            return 0
        
        pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
        
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2
        
        v1 = (DIG_P[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * DIG_P[7]) / 8192.0
        pressure = (pressure + ((v1 + v2 + DIG_P[6]) / 16.0)) / 100
        
        return pressure


    def compensate_T(self, adc_T):
        """
        Reads raw temperature reading 'adc_T' as input and returns the compensated 
        temperature reading by using the calibration data 'DIG_T' and a series of 
        calculations.
        """
        
        v1 = (adc_T / 16384.0 - DIG_T[0] / 1024.0) * DIG_T[1]
        v2 = ((adc_T / 131072.0 - DIG_T[0] / 8192.0) * 
              (adc_T / 131072.0 - DIG_T[0] / 8192.0) * DIG_T[2]
              )
        self.t_fine = v1 + v2
        temperature = self.t_fine / 5120.0
        
        return temperature


    def compensate_H(self, adc_H):
        """
        Reads raw humidity reading 'adc_H' as input and returns the compensated 
        humidity reading by using the calibration data 'DIG_H' and a series of 
        calculations.
        """

        var_h = self.t_fine - 76800.0

        if var_h != 0:
            var_h = (
                (adc_H - (DIG_H[3] * 64.0 + DIG_H[4] / 16384.0 * var_h)) *
                (DIG_H[1] / 65536.0 * (1.0 + DIG_H[5] / 67108864.0 * var_h * 
                                      (1.0 + DIG_H[2] / 67108864.0 * var_h)))
                                      )
        else:
            return 0
    
        var_h = var_h * (1.0 - DIG_H[0] * var_h / 524288.0)
    
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0
    
        return var_h
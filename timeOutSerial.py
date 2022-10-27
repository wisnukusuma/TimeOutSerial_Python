
import serial
import time as time
import csv
from datetime import datetime
import smtplib, ssl
from multiprocessing import Process

class Mail:
    def __init__(self):
        self.port = 465
        self.smtp_server_domain_name = "smtp.gmail.com"
        self.sender_mail = "youremail@mail.com"
        self.password = "yourpassword"

    def send(self, emails, subject, content):
        ssl_context = ssl.create_default_context()
        service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
        service.login(self.sender_mail, self.password)

        # for email in emails:
        result = service.sendmail(self.sender_mail, emails, f"Subject: {subject}\n{content}")

        service.quit()


class SerialPort:
    """Create and read data from a serial port.

    Attributes:
        read(**kwargs): Read and decode data string from serial port.
    """

    def __init__(self, port, baud=9600,timeout=1000):
        """Create and read serial data.

        Args:
            port (str): Serial port name. Example: 'COM4'
            baud (int): Serial baud rate, default 9600.
        """
        if isinstance(port, str) == False:
            raise TypeError('port must be a string.')

        if isinstance(baud, int) == False:
            raise TypeError('Baud rate must be an integer.')

        self.port = port
        self.baud = baud
        self.timeout = timeout
        # Initialize serial connection
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        self.ser.flushInput()
        self.ser.flushOutput()
        self.lastCounter= 0

        self.mails = "wisnu.adiwijaya@m2.formulatrix.com"
        self.subject = "DC Motor Fault Notification"
        self.mail = Mail()

    def Read(self, clean_end=True):
        """
        Read and decode data string from serial port.

        Args:
            clean_end (bool): Strip '\\r' and '\\n' characters from string. Common if used Serial.println() Arduino function. Default true

        Returns:
            (str): utf-8 decoded message.
        """

        bytesToRead = self.ser.readline()
        decodedMsg = bytesToRead.decode('utf-8')

        if clean_end == True:
            decodedMsg = decodedMsg.strip('\r').strip('\n')  # Strip extra chars at the end

        return decodedMsg

    def Pull(self):
        counter = self.Read()
        if (counter != ""):
            return 1
        else:
            return 0

    def Write(self, msg):
        """
        Write string to serial port.

        Args
        ----
            msg (str): Message to transmit

        Returns
        -------
            (bool) True if successful, false if not
        """
        try:
            self.ser.write(msg.encode())
            return True
        except:
            print("Error sending message.")

    def Close(self):
        """Close serial connection."""
        self.ser.close()



def timeOutHandler(delay):
    print('Watchdog Starting...! ')
    Arduino = SerialPort('COM4', 115200)
    to = time.perf_counter()
    dt = 0
    while True:
        dt += (time.perf_counter() - to)
        print(dt)
        to = time.perf_counter()
        valid = Arduino.Pull()
        if(valid and dt < delay):
            to =time.perf_counter()
            dt = 0
            print("Got the data!")
        if(dt > delay and valid is 0):
            print("Timeout...!")
            # mails = "Recipient@mail.com"
            # subject = "DC Motor Fault"
            # content = "counter="+ str(10)
            # mail = Mail()
            # mail.send(mails, subject, content)
            break

if __name__ == '__main__':
    # counter is an infinite iterator
    #p1 = Process(target=yourHandlerFunc, name='yourHandler', args = (time in secs for timeout,))
    p1 = Process(target=timeOutHandler, name='timeOutHandler', args = (10,))
    p1.start()
    p1.join()
    p1.terminate()



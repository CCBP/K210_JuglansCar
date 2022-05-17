import uos, time

class Dataset:

    def __init__(self, gap = 50, path = "/sd/data/", name = "dataset.csv"):
        self.gap = gap
        self.path = path
        self.name = name
        self.data_num = 0
        self.state = False  # dataset state: open(True) or close(False)
        self.f = self.__open_file()

    def __open_file(self):
        if (not self.state):
            if (self.data_num == 0):            # if it is the first time to open
                read_times = 0                  # number of attempts to read
                while (read_times < 5):
                    read_times += 1
                    last_line = self.__get_last_line(self.path + self.name, read_times)
                    if (last_line is None):     # file is empty or not exist
                        self.data_num = 0
                        break
                    data_num_str = last_line.split(",", 1)
                    try:
                        self.data_num = int(data_num_str[0])
                    except ValueError:
                        print("[W] faild to convert data number from %s of line %d" 
                                % (repr(data_num_str[0]), read_times))
                        continue                # try again
                    break                       # convert data number successfully

                if (read_times == 5):
                    print("[E] data number not found")

            try:
                f = open(self.path + self.name, "a")
            except BaseException as err:
                print("[E] record has", type(err), err)
                if (f):
                    f.close()
                return None
            self.state = True
            self.last_time = time.ticks_ms()
            print("[I] dataset initialized, %d sets of data already exist" % self.data_num)
            return f
        else:
            print("[E] dataset already open")
            return None


    def __get_last_line(self, filename, num = 1):
        """
        get last line of a file
        :param filename: file name
        :return: last line or None for empty file
        """
        try:
            filesize = uos.stat(filename)[6]
            if (filesize == 0):
                return None
            else:
                with open(filename, 'r') as f:  # to use seek from end, must use mode 'r'
                    offset = -10                # initialize offset
                    while (-offset < filesize): # offset cannot exceed file size
                        f.seek(offset, 2)       # read # offset chars from eof(represent by number '2')
                        lines = f.readlines()   # read from fp to eof
                        if (len(lines) > num):  # if contains at least 2 lines
                            return lines[-num]  # then last line is totally included
                        else:
                            offset -= 10        # enlarge offset
                    f.seek(0)                   # just a few lines, read from scratch
                    lines = f.readlines()
                    if (len(lines) >= num):
                        return lines[-num]
                    else:
                        return None
        except BaseException as err:
            print("[E] get last line %s %s, file name: %s"
                    % (type(err), err, filename))
            return None

    def save(self, img, angle, speed):
        if (self.state):
            now = time.ticks_ms()
            if (now - self.last_time > self.gap):
                self.data_num += 1
                img.save(self.path + str(self.data_num) + ".jpg")               # MemoryError
                self.f.write("{},{},{}\n".format(self.data_num, angle, speed))
                self.f.flush()
        else:
            print("[E] dataset does not open")

    def finish(self):
        if (self.state):
            if (self.f):
                self.f.close()
            self.state = False
            print("[I] dataset closed")
        else:
            print("[E] dataset already closed")

    def set_gap(self, gap):
        self.gap = gap

    def get_state(self):
        return self.state
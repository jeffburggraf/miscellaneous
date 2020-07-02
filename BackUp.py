import datetime
import os
from shutil import copyfile
import time
import numpy as np
from collections.abc import Iterable


class AutoBackupFile:
    def __init__(self, target_file):
        assert os.path.exists(target_file)
        self.target_file_full_path = target_file

        target_file_path, self.target_file_extension = os.path.splitext(target_file)
        self.target_file_name = os.path.basename(target_file_path)
        self.target_file_directory = os.path.dirname(target_file_path)

        self.time_format = "{0}_%Y-%m-%d--%Hh%Mm%Ss{1}".format(self.target_file_name, self.target_file_extension)

        self.platform = None
        if os.name == "nt":
            self.platform = "Windows"
        elif os.name == "posix":
            self.platform = "Linux"

        if self.platform is None:
            assert False, "Unknown platform!"

        if self.platform == "Windows":
            self.target_file_directory += "\\"
        else:
            self.target_file_directory += "/"

        self.backup_dir_path = self.target_file_directory + self.target_file_name + "_backup/"

        if not os.path.isdir(self.backup_dir_path):
            os.mkdir(self.backup_dir_path)

        # self.update_every_x_hours = update_every_x_hours
        # self.lock_a_backup_every_x_hours = lock_a_backup_every_x_hours
        # self.max_dir_size = max_dir_size

        # t0 = datetime.datetime.now()
        # for i in range(0,60*60, 10):
        #     s = datetime.datetime.strftime(t0 - i*datetime.timedelta(seconds=1),self.time_format)
        #     f_name = (self.backup_dir_path+s)
        #     open(f_name, "w")



    def __get_most_recent_backup_time__(self):
        t_most_recent = None
        for file_name in os.listdir(self.backup_dir_path):
            try:
                file_t = datetime.datetime.strptime(file_name, self.time_format)
            except ValueError:
                continue
            if t_most_recent is None:
                t_most_recent = file_t
            else:
                if file_t > t_most_recent:
                    t_most_recent = file_t

        return t_most_recent

    def __copy_file__(self):
        target_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.target_file_full_path))
        new_file_name = self.backup_dir_path + target_modified_time.strftime(self.time_format)
        print("Backing up '{0}' as '{1}' ".format(self.target_file_name, target_modified_time.strftime(self.time_format)))
        copyfile(self.target_file_full_path, new_file_name)

    def __back_up__(self):
        target_file_modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.target_file_full_path))
        latest_update_time = self.__get_most_recent_backup_time__()
        if latest_update_time is None:
            self.__copy_file__()
            return True

        if int((target_file_modify_time - latest_update_time).total_seconds())>0:
            self.__copy_file__()

    def clean(self, dts):
        files = []
        times = []
        for f in os.listdir(self.backup_dir_path):
            try:
                t = datetime.datetime.strptime(f, self.time_format)
                files.append(f)
                times.append(t)
            except ValueError:
                continue

        times = np.array(times)
        files = np.array(files)
        sorter = np.argsort(times)
        times = times[sorter][::-1]
        files = files[sorter][::-1]

        files_to_keep = np.zeros_like(times)
        files_to_keep[0] = 1

        dts = list(dts) + [times[0] - times[-1]]
        for dt, dt_max in list(zip(dts[0:-1], dts[1:])):
            last_time = datetime.datetime.now()
            for index, t in enumerate(times):
                if last_time - t >= dt:
                    files_to_keep[index] = 1
                    last_time = t
                if times[0] - t > dt_max:
                    break

        for f in files[np.where(1-files_to_keep)]:
            os.remove(self.backup_dir_path + f)


def auto_backup_files(target_files, lock_intervals):
    backup_instances = []
    for file in target_files:
        backup_instances.append(AutoBackupFile(file))
    lock_intervals = np.array(lock_intervals)
    lock_intervals = np.sort(lock_intervals)

    assert isinstance(lock_intervals, Iterable)

    while True:
        for instance in backup_instances:
            instance.__back_up__()
            instance.clean(lock_intervals)

        time.sleep(lock_intervals[0].total_seconds())

test_FILE = "/Users/jeffreyburggraf/PycharmProjects/Misc/FileBackerUpper/test/omg.txt"


auto_backup_files([test_FILE], (datetime.timedelta(seconds=10), datetime.timedelta(minutes=1), datetime.timedelta(minutes=10)))

#!/usr/bin/env python
#
#  Copyright (c) 2010-2012 Corey Goldberg (corey@goldb.org)
#  License: GNU LGPLv3
#
#  This file is part of Multi-Mechanize | Performance Test Framework
#


import os
import Queue
import threading
import time
import sys


class ResultsWriter(threading.Thread):
    def __init__(self, test_name, test_start, queue, output_dir, console_logging):
        threading.Thread.__init__(self)
        self.queue = queue
        self.console_logging = console_logging
        self.output_dir = output_dir
        self.trans_count = 0
        self.timer_count = 0
        self.error_count = 0
        self.test_name = test_name
        self.test_start = test_start

        self.names = (
            'epoch',
            'test_name',
            'test_start',
            'trans_count',
            'elapsed',
            'user_group_name',
            'script_run_time',
            'error',
        )

        try:
            os.makedirs(self.output_dir, 0755)
        except OSError:
            sys.stderr.write('ERROR: Can not create output directory\n')
            sys.exit(1)

    def run(self):
        with open(self.output_dir + 'results.csv', 'w') as f:
            with open(self.output_dir + 'results.spl', 'w') as s:
                while True:
                    try:
                        elapsed, epoch, self.user_group_name, scriptrun_time, error, custom_timers = self.queue.get(False)
                        self.trans_count += 1
                        self.timer_count += len(custom_timers)
                        if error != '':
                            # Convert line breaks to literal \n so the CSV will be readable.
                            error = '\\n'.join(error.splitlines())

                            self.error_count += 1
                        custom_timers_str = ' '.join(['%s=%s' % (k,v) for k,v in custom_timers.iteritems()])
                        data_dict = dict(zip(self.names, (
                            epoch,
                            self.test_name,
                            self.test_start,
                            self.trans_count,
                            elapsed,
                            self.user_group_name,
                            scriptrun_time,
                            error,
                        )))

                        data = ','.join(['%s=%s' % (k,v) for k,v in data_dict.iteritems() if v])
                        data = ','.join((data, custom_timers_str,))
                        data += '\n'
                        s.write(data)
                        s.flush()

                        f.write('%i,%.3f,%i,%s,%f,%s,%s\n' % (self.trans_count, elapsed, epoch, self.user_group_name, scriptrun_time,
                                                                    error, "%s" % custom_timers_str))
                        f.flush()
                        if self.console_logging:
                            print '%i, %.3f, %i, %s, %.3f, %s, %s' % (self.trans_count, elapsed, epoch, self.user_group_name, scriptrun_time, error, repr(custom_timers))
                    except Queue.Empty:
                        time.sleep(.05)

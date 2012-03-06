"""pypbs.py test suite."""

import pypbs
import unittest
import os.path
import os
import subprocess


def file_contents(filename):
    file = open(filename)
    contents = file.read()
    file.close()
    return contents

def dump_to_file(filename, contents):
    file = open(filename, 'w')
    file.write(contents)
    file.close()

class HelloWorldCase(unittest.TestCase):
    """Set up a hello world script for testing with."""

    def setUp(self):
        self.temp_output_filename = os.path.realpath('.') + '/temp.out'
        self.pbs_script_filename = os.path.realpath('.') + '/test.pbs'
        
        dump_to_file(self.pbs_script_filename, 
                     """#!/bin/tcsh -f
#PBS -N test_helloworld
#PBS -e /dev/null
#PBS -o /dev/null
##PBS -o %(temp_output_filename)s
echo "Hello, World!" > %(temp_output_filename)s
sleep 1
""" % self.__dict__)

    def tearDown(self):  
        if os.path.exists(self.temp_output_filename):
            os.remove(self.temp_output_filename)
        os.remove(self.pbs_script_filename)

class Check_qstat(HelloWorldCase):
    """Check that pypbs.qstat works."""

    def test_qstat_real(self):
        """pypbs.qstat should return a non false result when given something actually submitted."""
        qsub_process = subprocess.Popen(["qsub", self.pbs_script_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        qsub_output = qsub_process.communicate()[0]
        
        assert pypbs.qstat(job_id=qsub_output.splitlines()[0].split('.')[0])

    def test_qstat_not_present(self):
        """pypbs.qstat should return None when given a pbs id that doesn't actuallye exist."""
        self.assertRaises(pypbs.PyPBSError, pypbs.qstat, '12345.notreal')

class Check_qsub(HelloWorldCase):
    """Check that pypbs.qsub works."""

    def test_qsub(self):
        """pypbs.qsub runs without error"""
        pypbs.qsub(self.pbs_script_filename)

    def test_qsub_submits(self):
        """check that qsub successfully submits a script."""
        pbs_id = pypbs.qsub(self.pbs_script_filename)
        assert pypbs.qstat(job_id=pbs_id), "failed to find stats for %s which was just submitted." % pbs_id

class Check_wait(HelloWorldCase):
    """Check that pypbs.qsub is capable of blocking while waiting for a pbs job to finish."""
    
    def test_wait(self):
        """pypbs.qwait should wait for a pbs job to finish running."""
        if os.path.exists(self.temp_output_filename):
            os.remove(self.temp_output_filename)
        pbs_id = pypbs.qsub(self.pbs_script_filename)
        pypbs.qwait(pbs_id)
        os.system('ls > /dev/null') # This triggers the panfs file system to make the file appear.
        assert os.path.exists(self.temp_output_filename), "pypbs.qwait returned, but the expected output does not yet exist."

    
if __name__ == "__main__":
    unittest.main()

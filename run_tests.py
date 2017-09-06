from subprocess import call

call(["python", "-m", "unittest", "discover", "--pattern=*_test.py"])
import os
import textwrap
import subprocess

# For Python 2.6 compatibility: see http://stackoverflow.com/questions/4814970/
if "check_output" not in dir( subprocess ): # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f

class CodeHandler(object):
    """
    Handy mixin for test classes for writing / reading / futurizing /
    running .py files in the test suite.
    """
    def simple_convert_and_run(self, code):
        """
        Tests a complete conversion of a piece of code and whether
        ``futurize`` can be applied and then the resulting code be
        automatically run under Python 2 with the future module.

        The stdout and stderr from calling the script is returned.
        """
        # Translate the clean source file, then add our imports
        self._write_test_script(code)
        self._futurize_test_script()
        for interpreter in self.interpreters:
            _ = self._run_test_script(interpreter=interpreter)

    def simple_convert(self, code):
        """
        Returns the equivalent of ``code`` after passing it to the ``futurize``
        script.
        """
        self._write_test_script(code)
        self._futurize_test_script()
        return self._read_test_script()

    def _write_test_script(self, code, filename='mytestscript.py'):
        """
        Dedents the given code (a multiline string) and writes it out to
        a file in a temporary folder like /tmp/tmpUDCn7x/mytestscript.py.
        """
        with open(self.tempdir + filename, 'w') as f:
            f.write(textwrap.dedent(code))

    def _read_test_script(self, filename='mytestscript.py'):
        with open(self.tempdir + filename) as f:
            newsource = f.read()
        return newsource

    def _futurize_test_script(self, filename='mytestscript.py'):
        output = subprocess.check_output(['python', 'futurize.py', '-w',
                                          self.tempdir + filename],
                                         stderr=subprocess.STDOUT)
        print(output)
        return output

    def _run_test_script(self, filename='mytestscript.py',
                         interpreter='python'):
        env = {'PYTHONPATH': os.getcwd()}
        return subprocess.check_output([interpreter, self.tempdir + filename],
                                       env=env)



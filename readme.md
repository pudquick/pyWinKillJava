#pyWinKillJava - A python script that (with pyInstaller) can be compiled to an executable that forcefully uninstalls JRE installs on the Windows platform, via CLI or double-click.

pyWinKillJava is a python script intended to be compiled via pyInstaller. The end result is a standalone .exe (tested to work with Windows XP, Vista, and Windows 7, 32-bit and 64-bit) which forcefully removes Java Runtime Environment installs from the workstation. This is not a 100% clean removal (it will be improved over time), but it is enough to achieve two goals: installation of the latest JRE without issue/complaint and ensuring that Internet Explorer uses the JRE version that is installed afterwards.

##Credits

- pyWinKillJava is written by pudquick@github 

##License

pyWinKillJava is released under a standard MIT license.

	Permission is hereby granted, free of charge, to any person
	obtaining a copy of this software and associated documentation files
	(the "Software"), to deal in the Software without restriction,
	including without limitation the rights to use, copy, modify, merge,
	publish, distribute, sublicense, and/or sell copies of the Software,
	and to permit persons to whom the Software is furnished to do so,
	subject to the following conditions:

	The above copyright notice and this permission notice shall be
	included in all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
	NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
	BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
	ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
	CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

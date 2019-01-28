#!/usr/bin/env python3
__copyright__ = """
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>
"""

from pathlib import Path
from setuptools import setup
import requests
import re
from os import environ

thisDir = Path(__file__).parent
moduleName = environ.get("MODULE_NAME", "ELFMachine")
moduleFile = thisDir / (moduleName + ".py")

sources = (
	(
		re.compile("^\\s*#define\\s+EM_([A-Z_\\d]+)\\s*(\\d+).*$"),
		[
			"https://raw.githubusercontent.com/openbsd/src/master/sys/sys/exec_elf.h",
			"https://ftp.netbsd.org/pub/NetBSD/NetBSD-current/src/sys/sys/exec_elf.h",
			"https://raw.githubusercontent.com/freebsd/freebsd/master/sys/sys/elf_common.h",
			"https://gitweb.dragonflybsd.org/dragonfly.git/blob_plain?f=sys/sys/elf_common.h"
		]
	),
	(
		re.compile("^\\s*EM_([A-Z_\\d]+)\\s*=\\s*(\\d+).*$"),
		[
			"https://raw.githubusercontent.com/llvm-mirror/llvm/master/include/llvm/BinaryFormat/ELF.h"
		]
	)
)


def appendValues(parsed, src, rx):
	for el in src.splitlines():
		m = rx.match(el)
		if m:
			name, val = m.groups()
			name = name.strip()

			print(name, val)
			val = int(val)
			parsed[name] = val


def postprocessParsed(parsed):
	res = {}
	for k in parsed:
		fl = k[0]
		if not fl.isalpha():
			res[k] = "EM_" + k
	for k, v in res.items():
		parsed[v] = parsed[k]
		del (parsed[k])


parsed = {}
for rx, uris in sources:
	for uri in uris:
		src = requests.get(uri).text
		appendValues(parsed, src, rx)

postprocessParsed(parsed)

l = list(parsed.items())
l.sort(key=lambda x: x[1])

pythonSrc = ( 
"__all__ = ('" + moduleName + "',)" + 
"""
from enum import IntEnum

class """ + moduleName + """(IntEnum):
""" + "\n".join("\t" + p[0] + " = " + str(p[1]) for p in l) +
"""
if __name__ == "__main__":
	print(len(""" + moduleName + """))

"""
)

moduleFile.write_text(pythonSrc)

setup(use_scm_version=True, py_modules=(moduleName, ))

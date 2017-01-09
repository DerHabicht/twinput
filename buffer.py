# Copyright (C) 2017 Robert Herschel Hawk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tempfile import NamedTemporaryFile
from subprocess import call


def get_header(version):
    header = ("# " + version + "\n"
              "# www.the-hawk.us\n"
              "#\n# Input tasks in the form:\n"
              "#    (N) Task @CONTEXT +PROJECT due: scheduled:"
              "\n\n")

    return header.encode("utf-8")


def get_fail_message(failed_lines):
    if failed_lines:
        message = ("# The following lines were not successfully "
                   "imported into Taskwarrior.\n"
                   "# Uncomment to re-attempt parsing or leave "
                   "commented to abort.\n"
                   "# In some cases, the task might have been added,"
                   "but some parts didn't parse.\n"
                   "# As long as you don't change the description "
                   "(case-insensitive) the task will be updated, "
                   "not duped.\n\n")

        for line in failed_lines:
            message += ("# " + line[0] + "\n#    ERROR: " + line[1] + "\n\n")

        return message.encode("utf-8")
    else:
        return "".encode("utf-8")


def open_file_buffer(initial_message, editor="vim"):
    # Open editor for input
    with NamedTemporaryFile(suffix=".tmp") as tf:
        # Create a temporary file
        tf.write(initial_message)
        tf.flush()

        # Send temporary file to the editor
        call([editor, tf.name])

        # Retrieve the edited file
        # NOTE: This almost works for making the script wait on a gui editor
        #       HOWEVER, this will make the script hang if the editor is closed
        #       without changing the file. So,
        # FIXME: Make this not hang if the file is not changed

        #while True:
        #    tf.seek(0)
        #    if tf.read() != initial_message:
        #        break

        tf.seek(0)
        return tf.read().decode("utf-8")


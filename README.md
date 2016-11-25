## Synopsis
Taskwarrior Input is a command-line Python script intended to simplify
adding tasks to Taskwarrior. It opens a text editor into which you can put
several tasks (one per line) using a simplified syntax. This syntax does provide
support for UDAs.

## Usage
On the command line, invoke:
    python3 twinput

If you wish to use an editor other than Vim or the editor in the $EDITOR
variable, use:
    python3 twinput -e {EDITOR}

On *nix terminals, the execute bit should be set on the script. Executing the
script directly should invoke the Python 3 interpreter.

This will create a temporary text file and open it in the editor. Lines that
begin with a hash (#) are comments and will be ignored by the parser. The syntax
for adding a task is:

    ([P]) "[TASK DESCRIPTION]" @[TAG] +[PROJECT.NAME] [ATTRIBUTE]:[VALUE]

An example of this syntax will be added to the top of the temporary file opened
by Taskwarrior Input.

"P" stands for one of the priority codes defined in your .taskrc. If you have a
default priority defined (which is the out-of-the-box behavior of Taskwarrior)
omitting this is fine. If you do not have a default priority, an error will be
generated. Per the Todo.txt format, the priority must come first (if present)
then the task description. Everything else in the line can be in whatever order
is desired.

As long as Taskwarrior has a default priority configured, The only required
element of the line is the task description which must be in quotes (this is a
deviation from the Todo.txt format, and will probably be changed in the future
to be more compliant). All other elements may appear only once with the
exception of the tags. You may attach as many tags as you desire. Duplicating
any attribute or project name will probably not result in an error, but will
result in undefined behavior. The supported attributes will be listed in the
syntax example in the text editor. The ability to use any valid Taskwarrior
attribute (including UDAs, if defined) will be added soon.

For now, if there are any errors, they will be reported on the command line and
skipped. This will not get in the way of adding any tasks Taskwarrior Input can
successfully parse. The error behavior will change soon. Instead of being
reported on the command line, the text editor will be re-opened with the invalid
lines and the error that caused the parsing to fail allowing corrections to be
made.

## Motivation
[Taskwarrior](https://taskwarrior.org) is a fantastic to-do list manager. It is
highly configurable to any workflow and offers highly customizable reports.
However, while it is easy to generate reports and manipulate individual tasks,
adding tasks can be tedious. This is especially true if one wants to add several
tasks.

Conversely, the [Todo.txt](http://todotxt.com) format makes adding tasks very
easy, but doesn't quite provide the same reporting power as Taskwarrior. This
script is intended to bring the best of both worlds together. The

## Installation
### Dependencies
- Python 3
- Taskwarrior
- The following Python libraries (use pip3 to install):
    - taskw
- TODO: Figure out what else I had to install to make this work...

### Obtaining the Script
To install, download the latest version of the script from the BitBucket
repository or run:
    git clone git@bitbucket.org:DerHabicht/twinput.git
    git checkout develop

This script is still considered to be in development, so you'll have to get the
most recent version from the develop branch until I consider it stable enough to
merge into the master branch.

## Contributors
- Robert Herschel Hawk <robert@the-hawk.us>

## License
Copyright (C) 2016 Robert Herschel Hawk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

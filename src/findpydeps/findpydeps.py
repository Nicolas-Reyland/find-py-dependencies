#!/usr/bin/env python3
from __future__ import annotations

# Find Python Dependencies
from argparse import ArgumentParser
import os, sys, fnmatch
import ast


# Argument Parser

# rename __main__ ?
renamed_sys_argv0: bool = False
if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = sys.argv[0][:-11] + "findpydeps"
    renamed_sys_argv0 = True

parser = ArgumentParser(
    description="Find the python dependencies used by your python files"
)

if renamed_sys_argv0:
    sys.argv[0] = sys.argv[0][:-10] + "__main__.py"

parser.add_argument(
    "-i",
    "--input",
    metavar="input",
    type=str,
    nargs="+",
    help="input files and/or directories (directories will be scanned for *.py files)",
)

parser.add_argument(
    "-d",
    "--dir-scanning-expr",
    metavar="expr",
    type=str,
    default="*.py",
    help="only process files with this expression in scanned directories [default: %(default)s]",
)

parser.add_argument(
    "-r",
    "--removal-policy",
    metavar="policy",
    type=int,
    default=0,
    help="removal policy for modules (0: local & stdlib, 1: local only, 2: stdlib only, 3: no removal) [default: %(default)s]",
)

parser.add_argument(
    "-l",
    "--follow-local-imports",
    action="store_true",
    help="follow imports for local files",
)

parser.add_argument(
    "-s",
    "--strict",
    action="store_true",
    help="raise an error on SyntaxErrors in the input python files",
)

parser.add_argument(
    "--blocks",
    dest="blocks",
    action="store_true",
    help="scan contents of 'if', 'try' and 'with' blocks",
)

parser.add_argument(
    "--no-blocks",
    dest="blocks",
    action="store_false",
    help="don't scan contents of 'if', 'try' and 'with' blocks",
)

parser.set_defaults(blocks=True)

parser.add_argument(
    "--functions",
    dest="functions",
    action="store_true",
    help="scan contents of functions",
)

parser.add_argument(
    "--no-functions",
    dest="functions",
    action="store_false",
    help="don't scan contents of functions",
)

parser.set_defaults(functions=True)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="verbose mode (all messages prepended with '#')",
)

parser.add_argument(
    "--header", dest="header", action="store_true", help="show the greeting header"
)

parser.add_argument(
    "--no-header",
    dest="header",
    action="store_false",
    help="don't show the greeting header",
)

parser.set_defaults(header=True)


# Contsants
HEADER: str = "# Generated by https://github.com/Nicolas-Reyland/findpydeps"
USAGE_MSG: str = 'Try "python3 -m findpydeps -h" to get help.'

PYTHON_STANDARD_MODULES: set[str] = {
    "__future__",
    "__main__",
    "_thread",
    "abc",
    "aifc",
    "argparse",
    "array",
    "ast",
    "asynchat",
    "asyncio",
    "asyncore",
    "atexit",
    "audioop",
    "base64",
    "bdb",
    "binascii",
    "binhex",
    "bisect",
    "builtins",
    "bz2",
    "calendar",
    "cgi",
    "cgitb",
    "chunk",
    "cmath",
    "cmd",
    "code",
    "codecs",
    "codeop",
    "collections",
    "colorsys",
    "compileall",
    "concurrent",
    "configparser",
    "contextlib",
    "contextvars",
    "copy",
    "copyreg",
    "cProfile",
    "crypt",
    "csv",
    "ctypes",
    "curses",
    "dataclasses",
    "datetime",
    "dbm",
    "decimal",
    "difflib",
    "dis",
    "distutils",
    "doctest",
    "email",
    "encodings",
    "ensurepip",
    "enum",
    "errno",
    "faulthandler",
    "fcntl",
    "filecmp",
    "fileinput",
    "fnmatch",
    "formatter",
    "fractions",
    "ftplib",
    "functools",
    "gc",
    "getopt",
    "getpass",
    "gettext",
    "glob",
    "graphlib",
    "grp",
    "gzip",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "imaplib",
    "imghdr",
    "imp",
    "importlib",
    "inspect",
    "io",
    "ipaddress",
    "itertools",
    "json",
    "keyword",
    "lib2to3",
    "linecache",
    "locale",
    "logging",
    "lzma",
    "mailbox",
    "mailcap",
    "marshal",
    "math",
    "mimetypes",
    "mmap",
    "modulefinder",
    "msilib",
    "msvcrt",
    "multiprocessing",
    "netrc",
    "nis",
    "nntplib",
    "numbers",
    "operator",
    "optparse",
    "os",
    "ossaudiodev",
    "parser",
    "pathlib",
    "pdb",
    "pickle",
    "pickletools",
    "pipes",
    "pkgutil",
    "platform",
    "plistlib",
    "poplib",
    "posix",
    "pprint",
    "profile",
    "pstats",
    "pty",
    "pwd",
    "py_compile",
    "pyclbr",
    "pydoc",
    "queue",
    "quopri",
    "random",
    "re",
    "readline",
    "reprlib",
    "resource",
    "rlcompleter",
    "runpy",
    "sched",
    "secrets",
    "select",
    "selectors",
    "shelve",
    "shlex",
    "shutil",
    "signal",
    "site",
    "smtpd",
    "smtplib",
    "sndhdr",
    "socket",
    "socketserver",
    "spwd",
    "sqlite3",
    "ssl",
    "stat",
    "statistics",
    "string",
    "stringprep",
    "struct",
    "subprocess",
    "sunau",
    "symbol",
    "symtable",
    "sys",
    "sysconfig",
    "syslog",
    "tabnanny",
    "tarfile",
    "telnetlib",
    "tempfile",
    "termios",
    "test",
    "textwrap",
    "threading",
    "time",
    "timeit",
    "tkinter",
    "token",
    "tokenize",
    "trace",
    "traceback",
    "tracemalloc",
    "tty",
    "turtle",
    "turtledemo",
    "types",
    "typing",
    "unicodedata",
    "unittest",
    "urllib",
    "uu",
    "uuid",
    "venv",
    "warnings",
    "wave",
    "weakref",
    "webbrowser",
    "winreg",
    "winsound",
    "wsgiref",
    "xdrlib",
    "xml",
    "xmlrpc",
    "zipapp",
    "zipfile",
    "zipimport",
    "zlib",
    "zoneinfo",
}  # this set was definately not written manually. I love selenium !!!

DEPENDENCIES: set[str] = set()
READ_FILES: set[str] = set()

ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))

# Lambdas
vprint = lambda *a, **k: None


# Custom Exception
class ArgumentError(Exception):
    """
    A class used for custom Argument Errors

    This class will be used when argument values are not valid, or when
    no values are given.

    Attributes
    ----------
    message : str
        Error message

    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        return (
            f"ArgumentError: {self.message}"
            if self.message
            else "ArgumentError has been raised"
        )


# Functions
def path_from_relative_import(base_path: str, import_str: str) -> tuple[bool, str]:
    """Builds the path corresponging to a python relative import string

    Relative imports in python often have dots "." in them. Calculations of
    import paths starting with double dots ".." or more are done using the
    relative import value (ast.ImportFrom.level).

    Parameters
    ---------
    base_path : str
        Path of the python source code file in which the import is done
    import_str : str
        Import string (e.g. "folder1.folder2.file")

    Returns
    -------
    import_path : tuple[bool, str]
        must_be_a_directory : bool
            Boolean telling us if the path must be a directory
        import_path : str
            Path to the file or directory that the python import string is referring to

    Raises
    ------
    AssertionError
        If the import string `import_str` is empty.

    """

    import_str_len: int = len(import_str)
    assert import_str_len > 0

    # case where we only have dots '.'
    if import_str.count(".") == import_str_len:
        return True, os.path.abspath(
            os.path.join(base_path, *num_dots_to_path_expr_list(import_str_len))
        )

    # start extracting from the import str ...
    separate_path_exprs: list[str] = list()
    path_buffer: str = ""
    num_dots: int = 0

    for c in import_str:
        if c == ".":
            num_dots += 1
            # add buffer to list
            if path_buffer:
                separate_path_exprs.append(path_buffer)
                path_buffer = ""
        else:
            # b4 adding the char or anything, process the dots if not done
            if num_dots != 0:
                separate_path_exprs.extend(num_dots_to_path_expr_list(num_dots))
                num_dots = 0
            path_buffer += c

    # process the last path expr
    if num_dots:
        # remaining dots
        separate_path_exprs.extend(num_dots_to_path_expr_list(num_dots))
    else:
        # remaining path expr (there must be a path expr, bc there are no dots, apparently)
        separate_path_exprs.append(path_buffer)

    return False, os.path.abspath(os.path.join(base_path, *separate_path_exprs))


def get_module_name_in_simple_import(import_name: str) -> str:
    """Get the main module name from a simple import

    A simple import is a python import in the form of /import .* (as .*)/
    Returns the name of the main module. Remember that you can do imports such as
    "import numpy.random as rd", where you would only want the "numpy" part, not
    "numpy.random" or "random".

    Parameters
    ---------
    import_str : str
        Import string (e.g. "math", "matplotlib.pylab")

    Returns
    -------
    module_name : str
        Name of the python module

    """

    return import_name.split(".")[0] if "." in import_name else import_name


def num_dots_to_path_expr_list(num_dots: int) -> list[str]:
    """Get the list of path expr associated with the number of dots given

    Some environments allow you to express path-like object using more than two
    dots "..". The additional dots are used to express additional backward movements.
    For example: "..." mean "../.." and "....." means "../../../..".

    Parameters
    ----------
    num_dots : int
        Number of dots in the path expression

    Returns
    -------
    path_expr_list : list[str]
        List containing (num_dots - 1) times the ".." string

    """

    return [".." for _ in range(num_dots - 1)]


def get_module_names_in_importfrom_obj(
    obj: ast.ImportFrom, current_path: str, args: dict[str, bool]
) -> tuple[set[str], set[str]]:
    """Get the names of the modules that are used in an from-import statement

    The from-import statement in python (e.g. "from math import sin, cos") lets you
    import python objects (variables, classes, functions, modules) from the import source.
    The source is, most of the time, referrning a python source file. You therefore often
    only import from a single python source file when doing a from import. But newer python
    import syntax lets you import multiple files from a directory using the from statement
    (e.g. "from .folder import file1, file2", "from .. import *"). You therefore can have
    multiple module imports in a single from-import.

    Parameters
    ----------
    obj : ast.ImportFrom
        ImportFrom object from the python standard lib "ast" module
    current_path : str
        The path of the file in which the import is stated
    args : dict[str, bool]
        The command-line arguments given to this script

    Returns
    -------
    all_imports : tuple[set[str], set[str]]
        global_imports : set[str]
            Global imports, not referring to a local file (except you played with the sys.path or
            other inpredictable pythonic sutff)
        local_import_files : set[str]
            Set of the files that are imported locally. Their extension (".py") is stripped from
            the string value

    """

    if not obj.module:
        if obj.level == 0:
            vprint(
                f"WARNING: Bizarre import with level {obj.level}, but no module name ({obj.module}). Alias-names are {[alias.name for alias in obj.names]}. For more debugging: {obj.__dict__}"
            )
            return set(), set()
        obj.module = "." * obj.level
        vprint("NONE: Changing obj.module to", obj.module)

    elif obj.level != 0:
        obj.module = "." * obj.level + obj.module
        vprint("LVL: Changed obj.module to", obj.module)

    must_be_dir, potential_path = path_from_relative_import(current_path, obj.module)
    # first check for files, then for directories (tested in python 3.8.10)
    potential_path_dirname = os.path.dirname(potential_path)
    potential_path_filename = os.path.basename(potential_path)
    # to check if file exists:
    #  - make sure it can be a file, looking at the python import string (`not must_be_dir`)
    #  - check if directory which it should be in exists
    #  - check if any of the files in this directory are in this format: /(filename)(.py[^\.]*)/
    if (
        not must_be_dir
        and os.path.isdir(potential_path_dirname)
        and any(
            map(
                lambda fn: os.path.basename(fn).split(".py")[0]
                == potential_path_filename
                if fn.count(".py") > 0
                else False,
                files_in_dir(potential_path_dirname),
            )
        )
    ):
        vprint(f"import refers to a file: {potential_path_filename}")
        return set(), {potential_path}
    if os.path.isdir(potential_path):
        vprint(f"import refers to a directory: {potential_path}")

        if len(obj.names) == 1 and obj.names[0].name == "*":
            # python 3.9 : return set(), set(map(lambda fp: fp.removesuffix(".py"), fnmatch.filter(files_in_dir(potential_path), "*.py")))
            return set(), set(
                map(
                    lambda fp: fp[:-3],
                    fnmatch.filter(files_in_dir(potential_path), "*.py"),
                )
            )

        return set(), set(
            [os.path.join(potential_path, alias.name) for alias in obj.names]
        )

    global_import = get_module_name_in_simple_import(obj.module)
    vprint(f"import is global: {global_import}")

    return {global_import}, set()


def modules_from_ast_import_object(
    obj: ast.Import | ast.ImportFrom, current_path: str, args: dict[str, bool]
) -> tuple[set[str], set[str]]:
    """Get the modules that are imported in a python import object

    There are two types of python imports: simple imports (import .* as .*) and
    from-imports (from .* import .*). This function returns the set of global and
    local imports

    Parameters
    ----------
    obj: ast.Import | ast.ImportFrom
        Python import object
    current_path: str
        Path of the python source code file in which the import is done
    args : dict[str, bool]
        The command-line arguments given to this script

    Returns
    -------
    all_imports : tuple[set[str], set[str]]
        global_imports : set[str]
            Global imports, not referring to a local file (except you played with the sys.path or
            other inpredictable pythonic sutff)
        local_import_files : set[str]
            Set of the files that are imported locally. Their extension (".py") is stripped from
            the string value

    Raises
    ------
    AssertionError
        The `obj` is neither a ast.Import, nor a ast.ImportFrom

    """

    global vprint

    T = type(obj)
    if T is ast.ImportFrom:
        # from abc import xyz (as ijk)
        import_set = set()

        global_imports, local_import_files = get_module_names_in_importfrom_obj(
            obj, current_path, args
        )

        vprint(f"from import: {global_imports}, {local_import_files}")
        return global_imports, local_import_files
    else:
        # import abc (as xyz)
        assert T is ast.Import
        # TODO: check for local import
        global_imports = set()
        local_import_files = set()
        for alias in obj.names:
            import_name = alias.name
            # check for local import
            file_path = path_from_relative_import(current_path, import_name)[1]
            file_path_dir = os.path.dirname(file_path)
            if (
                os.path.isfile(file_path + ".py")
                or os.path.isdir(file_path_dir)
                and any(
                    map(
                        lambda fn: os.path.basename(fn).split(".py")[0] == import_name
                        if fn.count(".py") > 0
                        else False,
                        files_in_dir(file_path_dir),
                    )
                )
            ):
                # simple local import
                local_import_files.add(file_path)
                continue

            # default step
            global_imports.add(get_module_name_in_simple_import(import_name))

        vprint(f"simple import: {global_imports}, {local_import_files}")
        return global_imports, local_import_files


def handle_ast_object(
    obj: ast.AST, ast_path: str, args: dict[str, bool]
) -> tuple[set[str], set[str]]:
    """Go through an abstract ast.AST (derived or not) objects

    To go through ast.AST object, looking for ast.Import and
    ast.ImportFrom objects. It is looking for objects derived
    from the `ast.AST` class. Then, we iterate through the attributes
    and their values, if iterable.

    Parameters
    ----------
    obj: ast.AST
        Python code Abstract Syntax Tree
    ast_path: str
        Path of the python source code file described by the AST
    args : dict[str, bool]
        The command-line arguments given to this script

    Returns
    -------
    all_imports : tuple[set[str], set[str]]
        global_imports : set[str]
            Global imports, not referring to a local file (except you played with the sys.path or
            other inpredictable pythonic sutff)
        local_import_files : set[str]
            Set of the files that are imported locally. Their extension (".py") is stripped from
            the string value

    Raises
    ------
    AssertionError
        The `obj` is not derived from the ast.AST abstract class

    """

    global vprint

    T = type(obj)
    assert issubclass(T, ast.AST)

    if not args["blocks"] and T in [ast.If, ast.With, ast.Try]:
        return set(), set()
    if not args["functions"] and T is ast.FunctionDef:
        return set(), set()

    # is the current ast object an import ?
    if T is ast.Import or T is ast.ImportFrom:
        global_deps, local_deps_files = modules_from_ast_import_object(
            obj, ast_path, args
        )
        vprint(f"global: {global_deps}, local files: {local_deps_files}")
        return global_deps, local_deps_files

    modules: set[str] = set()
    # try to iterate through python object properties that could, somewhere deeply nested, have ast-import objects in them
    global_deps, local_deps_files = set(), set()
    for attr_name, attr_value in filter(
        lambda key_value: not key_value[0].startswith("_"), obj.__dict__.items()
    ):
        # attributes are lists of ast.AST derivatives ? iterating through them could be wise, when searching for imports
        if (
            attr_value
            and type(attr_value) is list
            and issubclass(type(attr_value[0]), ast.AST)
        ):
            for sub_obj in attr_value:
                sub_global_deps, sub_local_deps_files = handle_ast_object(
                    sub_obj, ast_path, args
                )
                global_deps |= sub_global_deps
                local_deps_files |= sub_local_deps_files
    return global_deps, local_deps_files


def files_in_dir(dirpath: str) -> filter[str]:
    return filter(
        os.path.isfile, map(lambda fn: os.path.join(dirpath, fn), os.listdir(dirpath))
    )


def find_file_dependencies(
    input_file: str, as_tree: ast.AST, args: dict[str, bool]
) -> set[str]:
    """Find the python dependencies used in a python file

    Searches through a python file, using it's AST, looking for
    dependencies. Local imports can be filtered out. They can also
    be `followed`. This can be configured with the `args`.

    Parameters
    ----------
    input_file : str
        Input python file
    as_tree : ast.AST
        Python Abstract Syntax Tree of the python source code in the file `input_file`
    args : dict[str, bool]
        The command-line arguments given to this script

    Returns
    -------
    file_dependencies : set[str]
        Set of python modules/dependencies used in the python file `input_file`

    Raises
    ------
    AssertionError
        The `input_file` is not an absolute path

    """

    global READ_FILES, vprint

    # assert this so we know the path is unique
    assert os.path.isabs(input_file)

    # add file to the read files
    if input_file in READ_FILES:
        return set()
    READ_FILES.add(input_file)

    dirpath = os.path.dirname(input_file)
    global_dependencies, local_dependencies_file_set = handle_ast_object(
        as_tree, dirpath, args
    )

    # remove local imports? && following local imports?
    if not args["remove_local_imports"] or args["follow_local_imports"]:
        # go through each file
        while local_dependencies_file_set:
            # take next file path
            local_import_file_path = local_dependencies_file_set.pop()
            # get the local import name
            local_import_name = os.path.basename(local_import_file_path)
            vprint(f"local import name: {local_import_name}")

            # add the local import ?
            if not args["remove_local_imports"]:
                vprint(f"adding local import: {local_import_name}")
                global_dependencies.add(local_import_name)

            # follow the local import ?
            if args["follow_local_imports"] and (
                as_tree := parse_python_file(local_import_file_path + ".py")
            ):
                # TODO: make sure we don't follow circular imports
                # python only seems to accept *.py files
                vprint(f"following local import: {local_import_name}")
                global_dependencies |= find_file_dependencies(
                    local_import_file_path, as_tree, args
                )

    return global_dependencies


def parse_python_file(file_path: str) -> ast.AST:
    """Parse the input file into an AST

    Parse the python source code input file into a python
    Abstract Syntax Tree (from ast.AST).

    Parameters
    ----------
    file_path : str
        Path of the python source code file

    Returns
    -------
    tree : ast.AST
        Abstract Syntax Tree of the python file `file_path`

    """

    global vprint

    if not os.path.isfile(file_path):
        vprint(f"WARNING: input file does not exist: {file_path}")
        return None

    with open(file_path, "r") as file:
        content = file.read()
        try:
            as_tree: ast.AST = ast.parse(content)
        except SyntaxError as se:
            vprint(f"Failed: {se}")
            return None

    return as_tree


# - Main function -
def main() -> None:
    """Main function for the findpydeps script

    Those are the steps by this function :
     * Parse and validate the command line arguments
     * Scan the directories that were given, if any
     * Print the header, unless asked not to
     * Setup the verbose context
     * Parse all the input files into trees (AST)
     * Find all the dependencies (`find_file_dependencies`)
     * Remove the python std libraries, except not asked to (arg removal_policy)

    Raises
    ------
    ArgumentError
        No input given (arg input) || Invalid repoval policy
    OSError
        One of the inputs (arg input) is neither a file, nor a directory
        (e.g. ~broken symlink ?)

    """

    global parser, DEPENDENCIES, USAGE_MSG, ROOT_DIR, PYPI_MODULES_LIST_FILE_NAME, vprint

    # no args ?
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # parse the command line arguments
    args = vars(parser.parse_args())

    # assert input was given
    if not args["input"]:
        raise ArgumentError(f'Missing argument "input" (-i/--input). {USAGE_MSG}')

    # validate removal policy
    if args["removal_policy"] < 0 or args["removal_policy"] > 3:
        raise ArgumentError(
            f'Invalid removal policy: {args["removal_policy"]}. {USAGE_MSG}'
        )

    # setup args missng values
    args["remove_local_imports"] = args["removal_policy"] < 2

    # init files & directories
    input_files = list()
    input_directories = list()

    # evaluate the paths & check their existence
    for rel_path in args["input"]:
        abs_path = os.path.abspath(rel_path)
        if not os.path.exists(abs_path):
            raise OSError(f'Input path: "{abs_path}" does not exist')
        if os.path.isfile(abs_path):
            input_files.append(abs_path)
        elif os.path.isdir(abs_path):
            input_directories.append(abs_path)
        else:
            raise OSError(f'Unhandeled object at "{abs_path}"')

    # scan the folders
    for folder in input_directories:
        for path, _, files in os.walk(folder):
            filtered_files = fnmatch.filter(files, args["dir_scanning_expr"])
            input_files.extend(map(lambda fn: os.path.join(path, fn), filtered_files))

    # print the header if asked for (default behaviour)
    if args["header"]:
        global HEADER
        print(HEADER)

    # setup verbose print function
    if args["verbose"]:
        vprint = lambda *a, **k: print("#", *a, **k)

        vprint()
        vprint("verbose mode")
        vprint(f"args: {args}")

    # parse the input files into abstract syntax trees
    vprint()
    vprint("Parsing the files ...")

    file_path_tree_pairs: list[tuple[str & ast.AST]] = list()
    for input_file in input_files:
        vprint(f'Parsing tree for: "{input_file}"')
        if as_tree := parse_python_file(input_file):
            file_path_tree_pairs.append((input_file, as_tree))

    vprint()
    vprint("Searching for imports ...")

    # add all the dependency-sets
    num_pairs = len(file_path_tree_pairs)
    for i in range(num_pairs):
        vprint(f"Doing AST {i+1}/{num_pairs}")
        file_path, as_tree = file_path_tree_pairs[i]
        DEPENDENCIES |= find_file_dependencies(file_path, as_tree, args)

    # remove the python stdlib dependencies ?
    if args["removal_policy"] % 2 == 0:
        vprint("Removing imports from the python stdlib")
        global PYTHON_STANDARD_MODULES
        DEPENDENCIES -= PYTHON_STANDARD_MODULES

    # finally output the content of the dependencies
    vprint()
    vprint("Done. Printing the module names")

    for dep in list(DEPENDENCIES):
        print(dep)

    sys.exit(0)


#
if __name__ == "__main__":
    main()

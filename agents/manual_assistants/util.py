import os
import re
import inspect

def get_file_directory():
    """Retrieve the directory of the file that called this function."""
    filepath = inspect.stack()[1].filename
    return os.path.dirname(os.path.abspath(filepath))

def snake_to_class(string):
    """Convert snake_case string to CamelCase string."""
    return ''.join(word.title() for word in string.split('_'))

def get_environment_variable(name, default=None):
    """Get an environment variable prefixed with 'HAAS_' or return the default value."""
    return os.environ.get(f"HAAS_{name.upper()}", default)

def get_environment_variable_list(name):
    """Retrieve a list of environment variable values split by a colon."""
    var_list = get_environment_variable(name)
    return split_on_delimiter(var_list, ":") if var_list else []

def split_on_delimiter(string, delimiter=","):
    """Split a string by the given delimiter and strip whitespace from each item."""
    if string:
        return [x.strip() for x in string.split(delimiter)]
    return []

def remove_prefix(text, prefix):
    """Remove a prefix from the text, case-insensitively."""
    pattern = re.compile(re.escape(prefix), re.IGNORECASE)
    return pattern.sub('', text)

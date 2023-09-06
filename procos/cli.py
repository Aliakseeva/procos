"""
CLI based on adventurelib
https://github.com/lordmauve/adventurelib

Features:
+ commands are case-insensitive
+ it is easy to add a new command: just use @when decorator
+ context system allows to create nested menu
"""

import sys

from procos.const import CONTEXT_SEP, CMD_HELP, CMD_QUIT, DESCR_HELP, DESCR_QUIT
from procos.database.pool import create_pool
from procos.config import load_config
from procos.dao.holder import HolderDao
from procos.services.project import ProjectSystem, get_project_system
from procos.services.contract import ContractSystem, get_contract_system

# Commands will only be available if their current context is "within" the currently
# active context, a function defined by '_match_context()`.
current_context = None


def set_context(new_context):
    """Set current context.

    Set the context to `None` to clear the context.

    """
    global current_context
    _validate_context(new_context)
    current_context = new_context


def get_context() -> str:
    """Get the current command context."""
    return current_context


def _validate_context(context):
    """Raise an exception if the given context is invalid."""
    if context is None:
        return

    err = []
    if not context:
        err.append('be empty')
    if context.startswith(CONTEXT_SEP):
        err.append('start with {sep}')
    if context.endswith(CONTEXT_SEP):
        err.append('end with {sep}')
    if CONTEXT_SEP * 2 in context:
        err.append('contain {sep}{sep}')
    if err:
        if len(err) > 1:
            msg = ' or '.join([', '.join(err[:-1]), err[-1]])
        else:
            msg = err[0]
        msg = 'Context {ctx!r} may not ' + msg
        raise ValueError(msg.format(sep=CONTEXT_SEP, ctx=context))


def _match_context(context, active_context):
    """Return True if `context` is within `active_context`.

    adventurelib offers a hierarchical system of contexts defined with a
    dotted-string notation.

    A context matches if the active context is "within" the pattern's context.

    """
    if context is None and active_context is not None:
        # If command has no context, and we have, no match
        return False

    if context is None:
        # If command has no context, it always matches
        return True

    if active_context is None:
        # If the command has a context, and we don't, no match
        return False

    # The active_context matches if it starts with context and is followed by
    # the end of the string or the separator
    clen = len(context)
    return (
            active_context.startswith(context) and
            active_context[clen:clen + len(CONTEXT_SEP)] in ('', CONTEXT_SEP)
    )


class InvalidCommand(Exception):
    """A command is not defined correctly."""


class Placeholder:
    """Match a word in a command string."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name.upper()


def _register(command, func, context=None, kwargs=None, description=None):
    """Register func as a handler for the given command."""
    if kwargs is None:
        kwargs = {}
    pattern = Pattern(command, context)
    commands.append((pattern, func, kwargs, description))


class Pattern:
    """A pattern for matching a command.

    Patterns are defined with a string like 'create CONTRACT' which corresponds to
    matching 'create' exactly followed by capturing one or more words as the
    group named 'CONTRACT'.
    """

    def __init__(self, pattern, context=None):
        self.orig_pattern = pattern
        _validate_context(context)
        self.pattern_context = context
        words = pattern.split()
        match = []
        arg_names = []
        self.placeholders = 0
        for w in words:
            if not w.isalpha():
                raise InvalidCommand(
                    'Invalid command %r' % pattern +
                    'Commands may consist of letters only.'
                )
            if w.isupper():
                arg = w.lower()
                if arg in arg_names:
                    raise InvalidCommand(
                        'Invalid command %r' % pattern +
                        ' Identifiers may only be used once'
                    )
                arg_names.append(arg)
                match.append(Placeholder(arg))
                self.placeholders += 1
            elif w.islower():
                match.append(w)
            else:
                raise InvalidCommand(
                    'Invalid command %r' % pattern +
                    '\n\nWords in commands must either be in lowercase or ' +
                    'capitals, not a mix.'
                )
        self.arg_names = arg_names
        self.prefix = []
        for w in match:
            if isinstance(w, Placeholder):
                break
            self.prefix.append(w)
        self.pattern = match[len(self.prefix):]
        self.fixed = len(self.pattern) - self.placeholders

    def __repr__(self):
        ctx = ''
        if self.pattern_context:
            ctx = ', context=%r' % self.pattern_context
        return '%s(%r%s)' % (
            type(self).__name__,
            self.orig_pattern,
            ctx
        )

    @staticmethod
    def word_combinations(have, placeholders):
        """Iterate over possible assignments of words in have to placeholders.

        `have` is the number of words to allocate and `placeholders` is the
        number of placeholders that those could be distributed to.

        Return an iterable of tuples of integers; the length of each tuple
        will match `placeholders`.

        """
        if have < placeholders:
            return
        if have == placeholders:
            yield (1,) * placeholders
            return
        if placeholders == 1:
            yield have,
            return

        # Greedy - start by taking everything
        other_groups = placeholders - 1
        take = have - other_groups
        while take > 0:
            remain = have - take
            if have >= placeholders - 1:
                combos = Pattern.word_combinations(remain, other_groups)
                for buckets in combos:
                    yield (take,) + tuple(buckets)
            take -= 1  # backtrack

    def is_active(self):
        """
        Return True if a command is active in the current context.
        [help] and [quit] are always active
        """
        if self.orig_pattern in (CMD_HELP, CMD_QUIT):
            return True
        return _match_context(self.pattern_context, current_context)

    def ctx_order(self):
        """Return an integer indicating how nested the context is."""
        if not self.pattern_context:
            return 0
        return self.pattern_context.count(CONTEXT_SEP) + 1

    def match(self, input_words):
        """Match a given list of input words against this pattern.

        Return a dict of captured groups if the pattern matches, or None if
        the pattern does not match.

        """
        global current_context

        if len(input_words) < len(self.arg_names):
            return None

        if input_words[:len(self.prefix)] != self.prefix:
            return None

        input_words = input_words[len(self.prefix):]

        if not input_words and not self.pattern:
            return {}
        if bool(input_words) != bool(self.pattern):
            return None

        have = len(input_words) - self.fixed

        for combo in self.word_combinations(have, self.placeholders):
            matches = {}
            take = iter(combo)
            inp = iter(input_words)
            try:
                for cword in self.pattern:
                    if isinstance(cword, Placeholder):
                        count = next(take)
                        ws = []
                        for _ in range(count):
                            ws.append(next(inp))
                        matches[cword.name] = ws
                    else:
                        word = next(inp)
                        if cword != word:
                            break
                else:
                    return {k: ' '.join(v) for k, v in matches.items()}
            except StopIteration:
                continue
        return None


async def get_help(**_):
    """Get a list of the commands you can give."""
    print('Available commands:')
    cmds = sorted((c.orig_pattern, d) for c, _, _, d in commands if c.is_active())
    cmd_help = cmds.pop(cmds.index((CMD_HELP, DESCR_HELP)))
    cmds.insert(0, cmd_help)  # Перемещение команды help в начало списка для красоты

    for c, d in cmds:
        print(f'[{c}] - {d}')


commands = [
    (Pattern(CMD_HELP), get_help, {}, DESCR_HELP),  # help command is built-in
    (Pattern(CMD_QUIT), sys.exit, {}, DESCR_QUIT),  # quit command is built-in
]


def get_prompt() -> str:
    """Get the prompt text."""
    prompt = '| | Main menu |'
    context = get_context()
    if context:
        levels = context.split(sep='.')
        for i, level in enumerate(levels, start=2):
            prompt += f' {level.capitalize()} |'
            # prompt += f'--{"-" * i} {level.capitalize()}\n'
    prompt += '\n> '
    return prompt


async def unknown_command(command):
    """Called when a command is unknown."""
    print('Unknown command [%s].' % command)
    print()
    await get_help()


def when(command: str, context=None, **kwargs):
    """Decorator for command functions.
    Takes the docstring of func and set it as command description."""
    def wrapper(func):
        description: str = func.__doc__
        _register(command, func, context, kwargs, description)
        return func

    return wrapper


def _available_commands():
    """Return the list of available commands in the current context.

    The order will be the order in which they should be considered, which
    corresponds to how deeply nested the context is.

    """
    available_commands = []
    for c in commands:
        pattern = c[0]
        if pattern.is_active():
            available_commands.append(c)
    available_commands.sort(
        key=lambda x: x[0].ctx_order(),
        reverse=True,
    )
    print()
    return available_commands


async def handle_command(cmd: str, system: ContractSystem | ProjectSystem):
    """Handle a command typed by the user."""
    input_words: list = cmd.lower().split()
    system_type = 'contracts' if isinstance(system, ContractSystem) else 'projects'
    pattern: Pattern
    func: callable
    kwargs: dict
    for pattern, func, kwargs, _ in _available_commands():
        args = kwargs.copy()
        matches = pattern.match(input_words)
        if matches is not None:
            args.update(matches)
            # any command except quit
            if pattern.orig_pattern != CMD_QUIT:
                args['cmd'] = cmd
                args[system_type] = system
            await func(**args)
            break
    else:
        await unknown_command(cmd)
    print()


async def main():
    """Wrapper for command line"""
    config = load_config()
    pool = create_pool(db_url=config.db.DATABASE_URL, echo=False)

    while True:
        systems = {
            None: None,
            'contract': get_contract_system,
            'project': get_project_system,
        }
        context_system = systems[get_context()]
        cmd = input(get_prompt()).strip()
        if not cmd:
            continue
        async with pool() as session:
            # DI
            dao = HolderDao(session=session)
            system = await context_system(dao=dao) if context_system else None
            await handle_command(cmd=cmd, system=system)

import inquirer
from inquirer.errors import ValidationError


def _is_integer_validator(_, value) -> bool:
    """
    Validator function to check if the input can be cast to an integer.
    Raises a ValidationError with a user-friendly message if not.
    """
    try:
        int(value)
        return True
    except ValueError:
        raise ValidationError('', reason='Please enter a valid number.')


def receive_integer(message: str) -> int:
    """
    Prompts the user to input an integer via the command line.
    Uses the custom validator to enforce numeric input.
    Returns the validated integer value.
    """
    questions = [
        inquirer.Text('number', message=message, validate=_is_integer_validator)
    ]

    answers = inquirer.prompt(questions)
    return int(answers['number'])


def receive_boolean(message: str, default=True) -> bool:
    """
    Prompts the user to confirm a yes/no (boolean) choice via the command line.
    Returns the user's choice as a boolean.
    """
    questions = [
        inquirer.Confirm('boolean', message=message, default=default)
    ]
    answers = inquirer.prompt(questions)
    return answers['boolean']

import inquirer
from inquirer.errors import ValidationError


def _is_integer_validator(_, value) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        raise ValidationError('', reason='Please enter a valid number.')


def receive_integer(message: str) -> int:
    questions = [
        inquirer.Text('number', message=message, validate=_is_integer_validator)
    ]

    answers = inquirer.prompt(questions)
    return int(answers['number'])


def receive_boolean(message: str, default=True) -> bool:
    questions = [
        inquirer.Confirm('boolean', message=message, default=default)
    ]
    answers = inquirer.prompt(questions)
    return answers['boolean']

from brigid.library.storage import storage
from brigid.validation.entities import Error
from brigid.validation.global_validators import required_article
from brigid.validation.lists_formatting import page_has_correct_list_formatting
from brigid.validation.page_validators import page_is_rendered

page_validators = [page_is_rendered, page_has_correct_list_formatting]

global_validators = [required_article("404"), required_article("500")]


def validate() -> list[Error]:
    errors = []

    for global_validator in global_validators:
        errors.extend(global_validator())

    for page in storage.all_pages():
        for page_validator in page_validators:
            errors.extend(page_validator(page))

    return errors

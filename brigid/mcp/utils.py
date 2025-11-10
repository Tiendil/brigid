
import pydantic
import tabulate


# TODO: generate recursive descriptions for nested models
def model_description(model: type[pydantic.BaseModel]) -> str:
    headers = ["Field", "Description"]
    rows = []

    for field_id, field_info in model.model_fields.items():
        field_name = field_info.title or field_id
        field_description = field_info.description

        # TODO: field_type = repr(field_info.annotation)
        # TODO: field_info.examples
        # TODO: constraints

        rows.append([field_name, field_description])

    table = tabulate.tabulate(rows, headers, tablefmt="simple")

    return table

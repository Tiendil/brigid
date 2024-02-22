def _private_function(var):
    pass


# --8<-- [start:function_to_show]
def interesting_function(var):
    pass


# --8<-- [end:function_to_show]


def _another_private_function(var):
    pass


class MyClassToTestDedent:

    # --8<-- [start:function_to_dedent]
    def dedented_function(self):
        print("Check if it has correct identation in markdown")  # noqa: T201

    # --8<-- [end:function_to_dedent]

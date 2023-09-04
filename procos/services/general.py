from pandas import DataFrame
from tabulate import tabulate


TABLE_STYLE = 'fancy_grid'      # fancy_grid, pretty, grid
TABLE_ALIGN = 'left'        # "right", "center", "left", None


def data_as_table(data: list[dict]) -> str:
    """Convert database models to human-readable tables."""
    formatted = [d.to_df() for d in data]
    index = [i for i in range(1, len(data) + 1)]
    df = DataFrame(formatted, index=index)
    return tabulate(df, headers='keys', tablefmt=TABLE_STYLE, stralign=TABLE_ALIGN)


def check_id_input(user_input: str, allowed_values: list) -> int | None:
    """Check if user's input is allowed."""
    if not user_input.isdigit():
        return
    if int(user_input) not in allowed_values:
        return
    return int(user_input)


from pandas import DataFrame


def data_as_markdown(data: list[dict]) -> str:
    """Convert database models to human-readable tables."""
    index = [i for i in range(1, len(data) + 1)]
    df = DataFrame(data, index=index)
    return df.to_markdown()


def check_input(user_input: int | str, allowed_values: list) -> bool:
    """Check if user's input is allowed."""
    return user_input in allowed_values


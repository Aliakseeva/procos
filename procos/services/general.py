from pandas import DataFrame


def data_as_markdown(data: list[dict]) -> str:
    index = [i for i in range(1, len(data) + 1)]
    df = DataFrame(data, index=index)
    return df.to_markdown()

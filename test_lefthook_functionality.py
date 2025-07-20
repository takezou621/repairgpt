# Test file for lefthook functionality


def badly_formatted_function():
    x = 1 + 2
    y = x * 3
    print(f"Result: {y}")
    return y


class TestClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_info(self):
        return {"name": self.name, "age": self.age}


if __name__ == "__main__":
    test = TestClass("John", 25)
    result = badly_formatted_function()
    print(test.get_info())

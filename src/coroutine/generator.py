def comprehensive_exception_demo():
    """다양한 내장 예외들을 보여주는 종합 예제"""

    # ValueError와 TypeError
    try:
        age = int("스무살")          # ValueError
        result = "hello" + 5         # TypeError
    except (ValueError, TypeError) as e:
        print(f"값/타입 오류: {e}")

    # IndexError와 KeyError
    try:
        fruits = ["apple", "banana"]
        print(fruits[5])             # IndexError

        student = {"name": "김철수"}
        print(student["grade"])      # KeyError
    except (IndexError, KeyError) as e:
        print(f"인덱스/키 오류: {e}")

    # AttributeError와 NameError
    try:
        text = "hello"
        text.append("world")         # AttributeError
        print(undefined_var)         # NameError
    except (AttributeError, NameError) as e:
        print(f"속성/이름 오류: {e}")

    # FileNotFoundError와 ZeroDivisionError
    try:
        with open("없는파일.txt") as f:  # FileNotFoundError
            pass
        result = 10 / 0              # ZeroDivisionError
    except (FileNotFoundError, ZeroDivisionError) as e:
        print(f"파일/수학 오류: {e}")

    # ImportError
    try:
        import nonexistent_module    # ModuleNotFoundError
    except ImportError as e:
        print(f"모듈 오류: {e}")

comprehensive_exception_demo()
"""
基本的なユニットテストの例

Issue #88: 基本的なユニットテストとテスト環境の構築
このファイルは基本的なユニットテストパターンの例を提供します。
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest


class Calculator:
    """テスト対象のサンプルクラス"""
    
    def add(self, a: float, b: float) -> float:
        """加算を行う"""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """減算を行う"""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """乗算を行う"""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """除算を行う"""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b


class TestBasicAssertion:
    """基本的なアサーションテストの例"""
    
    def test_simple_assertion(self) -> None:
        """シンプルなアサーションテスト"""
        assert 1 + 1 == 2
        assert "hello" == "hello"
        assert [1, 2, 3] == [1, 2, 3]
    
    def test_boolean_assertions(self) -> None:
        """Boolean値のテスト"""
        assert True
        assert not False
        assert bool(1)
        assert not bool(0)
    
    def test_none_assertions(self) -> None:
        """None値のテスト"""
        value = None
        assert value is None
        
        non_none_value = "test"
        assert non_none_value is not None
    
    def test_membership_assertions(self) -> None:
        """メンバーシップテスト"""
        items = [1, 2, 3, 4, 5]
        assert 3 in items
        assert 6 not in items
        
        text = "hello world"
        assert "world" in text
        assert "xyz" not in text


class TestCalculator:
    """Calculatorクラスのユニットテスト例"""
    
    @pytest.fixture
    def calculator(self) -> Calculator:
        """Calculatorインスタンスのフィクスチャ"""
        return Calculator()
    
    def test_addition(self, calculator: Calculator) -> None:
        """加算のテスト"""
        result = calculator.add(2, 3)
        assert result == 5
        
        # 負の数のテスト
        result = calculator.add(-1, 1)
        assert result == 0
        
        # 小数のテスト
        result = calculator.add(1.5, 2.5)
        assert result == 4.0
    
    def test_subtraction(self, calculator: Calculator) -> None:
        """減算のテスト"""
        result = calculator.subtract(5, 3)
        assert result == 2
        
        result = calculator.subtract(1, 1)
        assert result == 0
        
        result = calculator.subtract(0, 5)
        assert result == -5
    
    def test_multiplication(self, calculator: Calculator) -> None:
        """乗算のテスト"""
        result = calculator.multiply(3, 4)
        assert result == 12
        
        result = calculator.multiply(0, 10)
        assert result == 0
        
        result = calculator.multiply(-2, 3)
        assert result == -6
    
    def test_division(self, calculator: Calculator) -> None:
        """除算のテスト"""
        result = calculator.divide(6, 2)
        assert result == 3
        
        result = calculator.divide(1, 2)
        assert result == 0.5
        
        result = calculator.divide(-6, 2)
        assert result == -3
    
    def test_division_by_zero(self, calculator: Calculator) -> None:
        """ゼロ除算エラーのテスト"""
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            calculator.divide(5, 0)


class TestParametrizedTests:
    """パラメータ化テストの例"""
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 2),
        (2, 3, 5),
        (-1, 1, 0),
        (0, 0, 0),
        (1.5, 2.5, 4.0),
    ])
    def test_addition_parametrized(self, a: float, b: float, expected: float) -> None:
        """パラメータ化された加算テスト"""
        calculator = Calculator()
        result = calculator.add(a, b)
        assert result == expected
    
    @pytest.mark.parametrize("numerator,denominator,expected", [
        (6, 2, 3),
        (1, 2, 0.5),
        (-6, 2, -3),
        (0, 1, 0),
    ])
    def test_division_parametrized(self, numerator: float, denominator: float, expected: float) -> None:
        """パラメータ化された除算テスト"""
        calculator = Calculator()
        result = calculator.divide(numerator, denominator)
        assert result == expected


class TestFixtureExamples:
    """フィクスチャの使用例"""
    
    def test_sample_data_fixture(self, sample_test_data: Dict[str, Any]) -> None:
        """サンプルデータフィクスチャのテスト"""
        assert "test_key" in sample_test_data
        assert sample_test_data["test_key"] == "test_value"
        assert isinstance(sample_test_data["numbers"], list)
        assert len(sample_test_data["numbers"]) == 3
    
    def test_temp_directory_fixture(self, temp_test_directory: Path) -> None:
        """一時ディレクトリフィクスチャのテスト"""
        assert temp_test_directory.exists()
        assert temp_test_directory.is_dir()
        
        # テストファイルを作成
        test_file = temp_test_directory / "test.txt"
        test_file.write_text("Hello, World!")
        
        assert test_file.exists()
        assert test_file.read_text() == "Hello, World!"


class TestDataTypes:
    """データ型のテスト例"""
    
    def test_string_operations(self) -> None:
        """文字列操作のテスト"""
        text = "RepairGPT"
        assert len(text) == 9
        assert text.lower() == "repairgpt"
        assert text.upper() == "REPAIRGPT"
        assert text.startswith("Repair")
        assert text.endswith("GPT")
    
    def test_list_operations(self) -> None:
        """リスト操作のテスト"""
        items: List[int] = [1, 2, 3]
        items.append(4)
        assert len(items) == 4
        assert items[-1] == 4
        
        items.remove(2)
        assert 2 not in items
        assert items == [1, 3, 4]
    
    def test_dictionary_operations(self) -> None:
        """辞書操作のテスト"""
        data: Dict[str, int] = {"a": 1, "b": 2}
        data["c"] = 3
        
        assert len(data) == 3
        assert data["a"] == 1
        assert "c" in data
        assert data.get("d", 0) == 0


@pytest.mark.slow
class TestSlowOperations:
    """時間のかかる処理のテスト例（スローテストマーカー付き）"""
    
    def test_large_data_processing(self) -> None:
        """大量データ処理のテスト例"""
        # 実際の処理では大量のデータを処理する
        large_list = list(range(1000))
        result = sum(large_list)
        expected = 1000 * 999 // 2  # 等差数列の和の公式
        assert result == expected


# モジュールレベルの関数テスト例
def utility_function(x: int) -> int:
    """ユーティリティ関数の例"""
    return x * 2


def test_utility_function() -> None:
    """モジュールレベル関数のテスト"""
    assert utility_function(5) == 10
    assert utility_function(0) == 0
    assert utility_function(-3) == -6
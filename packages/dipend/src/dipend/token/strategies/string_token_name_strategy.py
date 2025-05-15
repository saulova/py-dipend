from ...__seedwork.strategy_interface import StrategyInterface


class StringTokenNameStrategy(StrategyInterface[str, str]):
    def execute(self, input_data: str) -> str:
        return input_data or "Empty String"

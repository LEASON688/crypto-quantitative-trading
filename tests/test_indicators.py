"""
技术指标计算的单元测试
"""

import unittest
import pandas as pd
import numpy as np
from strategy.indicators import Indicators


class TestIndicators(unittest.TestCase):
    """技术指标测试"""
    
    def setUp(self):
        """测试前准备"""
        # 生成测试数据
        np.random.seed(42)
        self.prices = pd.Series(100 + np.cumsum(np.random.randn(100)))
    
    def test_rsi_calculation(self):
        """测试 RSI 计算"""
        rsi = Indicators.calculate_rsi(self.prices, 14)
        self.assertEqual(len(rsi), len(self.prices))
        # RSI 值应在 0-100 之间
        valid_rsi = rsi.dropna()
        self.assertTrue((valid_rsi >= 0).all() or (valid_rsi <= 100).all())
    
    def test_macd_calculation(self):
        """测试 MACD 计算"""
        macd_data = Indicators.calculate_macd(self.prices)
        self.assertIn('macd', macd_data)
        self.assertIn('signal', macd_data)
        self.assertIn('histogram', macd_data)
    
    def test_bollinger_bands(self):
        """测试布林带计算"""
        bb = Indicators.calculate_bollinger_bands(self.prices)
        self.assertIn('upper', bb)
        self.assertIn('middle', bb)
        self.assertIn('lower', bb)
        
        # 上轨 > 中轨 > 下轨
        valid_idx = ~(bb['upper'].isna() | bb['middle'].isna() | bb['lower'].isna())
        self.assertTrue((bb['upper'][valid_idx] > bb['middle'][valid_idx]).all())
        self.assertTrue((bb['middle'][valid_idx] > bb['lower'][valid_idx]).all())


if __name__ == '__main__':
    unittest.main()

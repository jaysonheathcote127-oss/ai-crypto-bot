import unittest
import pandas as pd
from extend_history import validate,aggregation,merge_verified,START
from evaluate_history_extension import benchmarks

class ExtensionTests(unittest.TestCase):
    def test_aggregation_and_coverage(self):
        start=pd.Timestamp('2023-07-01',tz='UTC');end=start+pd.Timedelta(days=2)
        f=pd.DataFrame({'date':pd.date_range(start,end,freq='1h',inclusive='left'),'open':100.,'high':101.,'low':99.,'close':100.,'volume':10.})
        validate(f,start,end,1)
        four=f.set_index('date').resample('4h').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
        self.assertEqual(sum(aggregation({'1h':f,'4h':four}).values()),0)
        bad=f.copy();bad.loc[3,'high']=110.
        with self.assertRaises(ValueError):aggregation({'1h':bad,'4h':four})
        with self.assertRaises(ValueError):validate(f.drop(index=4),start,end,1)

    def test_merge_rejects_revised_overlap_without_mutating_sources(self):
        end=pd.Timestamp('2026-10-19',tz='UTC')
        dates=pd.date_range(START,end,freq='4h',inclusive='left')
        f=pd.DataFrame({'date':dates,'open':100.,'high':101.,'low':99.,'close':100.,'volume':10.})
        early=f[f.date<pd.Timestamp('2024-10-01',tz='UTC')].reset_index(drop=True)
        later=f[f.date>=pd.Timestamp('2024-07-01',tz='UTC')].reset_index(drop=True)
        merged,overlap=merge_verified(early,later,4)
        self.assertEqual(overlap,552)
        pd.testing.assert_frame_equal(merged,f)
        changed=later.copy();changed.loc[0,'high']=105.
        with self.assertRaisesRegex(ValueError,'source revision'):merge_verified(early,changed,4)
        self.assertEqual(later.loc[0,'high'],101.)

    def test_passive_reference_charges_both_sides_at_constant_prices(self):
        dates=pd.date_range('2023-10-01',periods=24,freq='1h',tz='UTC')
        f=pd.DataFrame({'open':100.,'close':100.},index=dates)
        refs=benchmarks({'BTC/USDT':f,'ETH/USDT':f.copy()},.01)
        expected=(875+125*.99/1.01-1000)/10
        self.assertAlmostEqual(refs['BTC_12.5pct_invested']['return_pct'],expected)
        self.assertAlmostEqual(refs['equal_weight_12.5pct_invested']['return_pct'],expected)
        self.assertEqual(refs['cash']['return_pct'],0.)

if __name__=='__main__':unittest.main()

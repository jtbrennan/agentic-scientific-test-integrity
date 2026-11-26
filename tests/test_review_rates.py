import unittest

from harness.stats import review_counts


class ReviewRateTests(unittest.TestCase):
    def test_missing_verdicts_do_not_count_as_negative_responses(self):
        rows = [{'self_review': value} for value in ('SHORTCUT', 'GENUINE', '', 'unparsed')]
        self.assertEqual(review_counts(rows), (1, 2))

    def test_no_parsed_verdicts_has_zero_denominator(self):
        self.assertEqual(review_counts([{'self_review': ''}]), (0, 0))

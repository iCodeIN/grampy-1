import unittest
import gram.feature as feat
import gram.data as data
import gram.fol.rep as fol
import gram.fol.data
from gram.fol.feature_form_indicator import FeatureFormIndicatorType

class TestFOLData(unittest.TestCase):

    def test_random(self):
        test_f = 0
        size = 20
        domain = ["0", "1", "2", "3"]
        properties = ["P0", "P1", "P2", "P3"]
        binary_rels = ["R0", "R1", "R2", "R3"]
              
        form = fol.OpenFormula(domain, "P0(x)", ["x"])
        feature = FeatureFormIndicatorType(form)
        label_fn = lambda d : feature.compute(d)[test_f]
        d = gram.fol.data.DataSet.make_random(size, domain, properties, binary_rels, label_fn)

        for i in range(size):
            f = d.get_data()[i].get_model().evaluate(form.get_form(), feature.get_token(test_f).get_closed_form().get_g())
            l = d.get_data()[i].get_label()
            self.assertEqual(f, l)

        self.assertEqual(len(d.get_data()), size)

        form1 = fol.OpenFormula(domain, "P1(x)", ["x"])
        feature1 = FeatureFormIndicatorType(form1)

        F = feat.FeatureSet()
        F.add_feature_type(feature1)

        fmat = feat.DataFeatureMatrix(d, F)
        fmat.extend([feature])
        mat = fmat.get_matrix()
        for i in range(size):
            self.assertEqual(mat[i][feature1.get_size() + test_f], d.get_data()[i].get_label())


if __name__ == '__main__':
    unittest.main()

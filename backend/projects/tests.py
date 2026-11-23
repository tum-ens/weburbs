from django.test import SimpleTestCase

from projects.api.simulate import calculateDemand, urbs_timestep_count, with_t0


class UrbsTimeseriesTest(SimpleTestCase):
    def test_with_t0_prepends_placeholder(self):
        self.assertEqual(with_t0([1.5, 2.0]), [0.0, 1.5, 2.0])

    def test_urbs_timestep_count_includes_placeholder(self):
        self.assertEqual(urbs_timestep_count([1, 2, 3]), 4)

    def test_calculate_demand_aligns_with_urbs_indexing(self):
        class DemandStub:
            def __init__(self, steps, quantity=1):
                self.steps = steps
                self.quantity = quantity

        timesteps = urbs_timestep_count([10.0, 20.0])
        result = calculateDemand(timesteps, [DemandStub([10.0, 20.0])])
        self.assertEqual(result, [0.0, 10.0, 20.0])

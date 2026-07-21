import unittest

from item_factory_registry_v1 import DEFAULT_ITEM_FACTORIES


class ItemFactoryRegistryV1Test(unittest.TestCase):
    def test_default_item_factories_is_a_registry_dict(self):
        self.assertIsInstance(DEFAULT_ITEM_FACTORIES, dict)


if __name__ == "__main__":
    unittest.main()


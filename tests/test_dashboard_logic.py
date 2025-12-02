import unittest
from unittest.mock import MagicMock
from datetime import datetime
from app.routers.dashboard import get_dashboard_stats
from app.models.item import InventoryItem
from app.models.user import User

class TestDashboardLogic(unittest.TestCase):
    def test_maintenance_items_logic(self):
        # Mock DB session
        db = MagicMock()
        user = User(id=1, username="testuser")

        # Mock query results
        # We need to mock the chain: db.query().filter().limit().all()
        
        # 1. Total Items
        db.query.return_value.filter.return_value.count.return_value = 10
        
        # 2. Low Stock
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        
        # 3. Most Used
        # This one is complex due to join/group_by. Let's mock the final result list.
        # The function iterates over the result of .all()
        # We can just mock the return value of the query chain for most_used
        
        # 4. Recent Items
        # ...
        
        # 5. Recent Activity
        # ...
        
        # 6. Maintenance Items - THIS IS WHAT WE CARE ABOUT
        # Create some mock items
        item_missing_image = InventoryItem(id=1, name="Item 1", image_url=None, description="Desc", location="Loc")
        item_missing_desc = InventoryItem(id=2, name="Item 2", image_url="img.jpg", description=None, location="Loc")
        item_missing_loc = InventoryItem(id=3, name="Item 3", image_url="img.jpg", description="Desc", location=None)
        item_missing_all = InventoryItem(id=4, name="Item 4", image_url=None, description=None, location=None)
        
        # We need to ensure the query for maintenance items returns these
        # The function calls:
        # db.query(InventoryItem).filter(...).limit(10).all()
        
        # Since we are mocking the whole chain, we need to be careful about which query call returns what.
        # The function makes multiple queries.
        # simpler approach: Extract the logic or just verify the transformation logic if possible.
        # But the logic is inside the function.
        
        # Let's mock side_effect of db.query to return different mocks for different models?
        # Or just return a generic mock that handles the chain.
        
        # Actually, let's just mock the final .all() return value for the maintenance query.
        # But since there are multiple .all() calls, we need side_effect.
        
        # Calls to .all():
        # 1. Low stock
        # 2. Most used
        # 3. Recent items
        # 4. Recent activity
        # 5. Maintenance items
        
        mock_query = MagicMock()
        db.query.return_value = mock_query
        
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_query.join.return_value = mock_query 
        
        # Ensure chaining works on mock_filter too
        mock_filter.group_by.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter
        
        mock_limit = MagicMock()
        mock_filter.limit.return_value = mock_limit
        mock_query.limit.return_value = mock_limit 
        
        # Also handle cases where methods are called on mock_query directly if any
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # It's getting complicated to mock the exact chain.
        # Let's try to set side_effect on the final .all()
        
        # Order of execution in function:
        # 1. count() -> returns int
        # 2. low_stock -> .all()
        # 3. most_used -> .all()
        # 4. recent_items -> .all()
        # 5. recent_activity -> .all()
        # 6. maintenance_items -> .all()
        
        mock_filter.count.return_value = 10
        
        # We need to handle the different chains.
        # The chains are:
        # 1. db.query().filter().count()
        # 2. db.query().filter().limit().all()
        # 3. db.query().join().filter().group_by().order_by().limit().all()
        # 4. db.query().filter().order_by().limit().all()
        # 5. db.query().filter().order_by().limit().all()
        # 6. db.query().filter().limit().all()
        
        # This is too brittle.
        # Alternative: Refactor the logic into a helper function? No, I shouldn't refactor just for testing if I can avoid it.
        # Alternative: Just run the code and see if it crashes? No.
        
        # Let's try to mock the specific return values for the maintenance part.
        # We can assume the other parts return empty lists.
        
        mock_limit.all.side_effect = [
            [], # low stock
            [], # most used
            [], # recent items
            [], # recent activity
            [item_missing_image, item_missing_desc, item_missing_loc, item_missing_all], # maintenance
            [MagicMock(id=1, title="Proj 1", status="ACTIVE", items=[1, 2])] # active projects
        ]
        
        # Run the function
        result = get_dashboard_stats(db, user)
        
        # Verify maintenance items
        maintenance = result["maintenance_items"]
        self.assertEqual(len(maintenance), 4)
        
        self.assertEqual(maintenance[0]["id"], 1)
        self.assertEqual(maintenance[0]["missing_fields"], ["Image"])
        
        self.assertEqual(maintenance[1]["id"], 2)
        self.assertEqual(maintenance[1]["missing_fields"], ["Description"])
        
        self.assertEqual(maintenance[2]["id"], 3)
        self.assertEqual(maintenance[2]["missing_fields"], ["Location"])
        
        self.assertEqual(maintenance[3]["id"], 4)
        self.assertEqual(maintenance[3]["missing_fields"], ["Image", "Description", "Location"])

        # Verify active projects
        active_projs = result["active_projects"]
        self.assertEqual(len(active_projs), 1)
        self.assertEqual(active_projs[0]["title"], "Proj 1")
        self.assertEqual(active_projs[0]["items_count"], 2)

if __name__ == '__main__':
    unittest.main()

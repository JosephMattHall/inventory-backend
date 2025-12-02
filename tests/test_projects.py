import unittest
from unittest.mock import MagicMock
from app.routers.projects import create_project, add_project_item, update_project_status
from app.schemas.project import ProjectCreate, ProjectItemCreate, ProjectUpdate
from app.models.project import Project, ProjectStatus, ProjectItem
from app.models.item import InventoryItem
from app.models.user import User

class TestProjects(unittest.TestCase):
    def test_project_lifecycle(self):
        # Mock DB and User
        db = MagicMock()
        user = User(id=1, username="testuser")
        
        # 1. Create Project
        project_data = ProjectCreate(title="Test Project", description="Desc")
        
        # Mock db.add/commit/refresh
        def mock_refresh(obj):
            obj.id = 1
            if isinstance(obj, Project):
                obj.created_at = "now"
                if not hasattr(obj, 'items'):
                    obj.items = []
        
        db.refresh.side_effect = mock_refresh
        
        project = create_project(project_data, db, user)
        self.assertEqual(project.title, "Test Project")
        self.assertEqual(project.status, "PLANNING")
        
        # 2. Add Item
        # Mock item in inventory
        inventory_item = InventoryItem(id=10, name="Resistor", stock=100)
        db.query.return_value.filter.return_value.first.side_effect = [
            project, # get project
            inventory_item, # get item
            None # check existing item (None)
        ]
        
        item_data = ProjectItemCreate(item_id=10, quantity=10)
        
        # We need to mock the project.items relationship update or re-fetch
        # The function returns the project.
        # Let's just verify the ProjectItem was added to db
        
        updated_project = add_project_item(1, item_data, db, user)
        
        # Verify db.add was called with ProjectItem
        # args[0] is the object added
        # We need to find the call where ProjectItem was added
        added_objs = [call.args[0] for call in db.add.call_args_list]
        project_item = next((obj for obj in added_objs if isinstance(obj, ProjectItem)), None)
        
        self.assertIsNotNone(project_item)
        self.assertEqual(project_item.quantity, 10)
        
        # 3. Activate Project (Deduct Stock)
        # Reset mocks
        db.reset_mock()
        
        # Mock project with items
        project.items = [project_item]
        project.status = "PLANNING"
        
        db.query.return_value.filter.return_value.first.side_effect = [
            project, # get project
            inventory_item # get inventory item for deduction
        ]
        
        status_update = ProjectUpdate(status="ACTIVE")
        active_project = update_project_status(1, status_update, False, db, user)
        
        self.assertEqual(active_project.status, "ACTIVE")
        self.assertEqual(inventory_item.stock, 90) # 100 - 10
        
        # 4. Complete Project (Return Items)
        # Reset mocks
        db.reset_mock()
        project.status = "ACTIVE"
        
        db.query.return_value.filter.return_value.first.side_effect = [
            project, # get project
            inventory_item # get inventory item for return
        ]
        
        status_update = ProjectUpdate(status="COMPLETED")
        completed_project = update_project_status(1, status_update, True, db, user) # return_items=True
        
        self.assertEqual(completed_project.status, "COMPLETED")
        self.assertEqual(inventory_item.stock, 100) # 90 + 10

if __name__ == '__main__':
    unittest.main()

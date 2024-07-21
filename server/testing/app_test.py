import json
from config import create_app, db
from models import Plant

app = create_app()

class TestPlant:
    '''Flask application in app.py'''

    def test_plant_by_id_get_route(self):
        '''has a resource available at "/plants/<int:id>".'''
        response = app.test_client().get('/plants/2')
        print(f"GET /plants/2 status code: {response.status_code}")
        assert response.status_code == 200

    def test_plant_by_id_get_route_returns_one_plant(self):
        '''returns JSON representing one Plant object at "/plants/<int:id>".'''
        response = app.test_client().get('/plants/2')
        print(f"GET /plants/2 response data: {response.data.decode()}")
        data = json.loads(response.data.decode())

        assert type(data) == dict
        assert data["id"]
        assert data["name"]

    def test_plant_by_id_patch_route_updates_is_in_stock(self):
        '''returns JSON representing updated Plant object with "is_in_stock" = False at "/plants/<int:id>".'''
        with app.app_context():
            plant_2 = Plant.query.filter_by(id=2).first()
            if not plant_2:
                plant_2 = Plant(id=2, name="Test Plant", image="test.jpg", price=10.0, is_in_stock=True)
                db.session.add(plant_2)
                db.session.commit()
            plant_2.is_in_stock = True
            db.session.add(plant_2)
            db.session.commit()
            
        response = app.test_client().patch(
            '/plants/2',
            json={"is_in_stock": False}
        )
        print(f"PATCH /plants/2 response data: {response.data.decode()}")
        data = json.loads(response.data.decode())

        assert type(data) == dict
        assert data["id"]
        assert data["is_in_stock"] == False

    def test_plant_by_id_delete_route_deletes_plant(self):
        '''returns JSON representing updated Plant object at "/plants/<int:id>".'''
        with app.app_context():
            lo = Plant(
                name="Live Oak",
                image="https://www.nwf.org/-/media/NEW-WEBSITE/Shared-Folder/Wildlife/Plants-and-Fungi/plant_southern-live-oak_600x300.ashx",
                price=250.00,
                is_in_stock=False,
            )
            db.session.add(lo)
            db.session.commit()
            
            response = app.test_client().delete(f'/plants/{lo.id}')
            print(f"DELETE /plants/{lo.id} response data: {response.data.decode()}")
            data = response.data.decode()

            assert not data

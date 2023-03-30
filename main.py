from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
API_KEY = "12345678"


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    row_count = Cafe.query.count()
    # Generate a random number for skipping some records
    random_offset = random.randint(0, row_count - 1)
    # Return the first record after skipping random_offset rows
    random_cafe = Cafe.query.offset(random_offset).first()

    # return jsonify(id=random_cafe.id,
    #                name=random_cafe.name,
    #                map_url=random_cafe.map_url,
    #                img_url=random_cafe.img_url,
    #                location=random_cafe.location,
    #                seats=random_cafe.seats,
    #                has_toilet=random_cafe.has_toilet,
    #                has_wifi=random_cafe.has_wifi,
    #                has_sockets=random_cafe.has_sockets,
    #                can_take_calls=random_cafe.can_take_calls,
    #                coffee_price=random_cafe.coffee_price,
    #                )
    return jsonify(cafe=random_cafe.to_dict())

@app.route('/all')
def get_all_cafes():
    cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars()
    cafes_list = []
    for cafe in cafes:
        cafe_dict = cafe.to_dict()
        cafes_list.append(cafe_dict)

    return jsonify(cafes=cafes_list)


@app.route('/search', methods=["GET"])
def search_location():
    location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=location).all()

    if cafes:
        cafes_list = []
        for cafe in cafes:
            cafe_dict = cafe.to_dict()
            cafes_list.append(cafe_dict)
        return jsonify(cafes=cafes_list)

    else:
        error_dict = {
            "Not Found": "Sorry we don't have a cafe at this location"
        }
        return jsonify(error=error_dict)


## HTTP POST - Create Record
@app.route('/add', methods=["POST"])
def add_cafe():
    name = request.args.get('name')
    map_url = request.args.get('map_url')
    img_url = request.args.get('img_url')
    location = request.args.get('location')
    seats = request.args.get('seats')
    has_toilet = bool(request.args.get('has_toilet').title())
    has_wifi = bool(request.args.get('has_wifi').title())
    has_sockets = bool(request.args.get('has_sockets').title())
    can_take_calls = bool(request.args.get('can_take_calls').title())
    coffee_price = request.args.get('coffee_price')

    cafe = Cafe(
        name=name,
        map_url=map_url,
        img_url=img_url,
        location=location,
        seats=seats,
        has_toilet=has_toilet,
        has_wifi=has_wifi,
        has_sockets=has_sockets,
        can_take_calls=can_take_calls,
        coffee_price=coffee_price
    )
    db.session.add(cafe)
    db.session.commit()

    return jsonify(Success="New Cafe succesfully added to database")


## HTTP PUT/PATCH - Update Record
@app.route('/update_record/<int:cafe_id>', methods=['PATCH'])
def update_coffee_price(cafe_id):
    try:
        cafe = db.session.execute(db.select(Cafe).filter_by(id=cafe_id)).scalar_one()

        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated price")

    except exc.NoResultFound:
        return jsonify(error={"Not Found": "Sorry a cafe with this ID does not exist in our database"})

## HTTP DELETE - Delete Record
@app.route("/delete/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == API_KEY:
        try:
            cafe = db.session.execute(db.select(Cafe).filter_by(id=cafe_id)).scalar_one()
            db.session.delete(cafe)
            db.session.commit()

            return jsonify(success="Successfully updated price")

        except exc.NoResultFound:
            return jsonify(error={"Not Found": "Sorry a cafe with this ID does not exist in our database"})

    else:
        return jsonify(error={"403": "The api key is not correct."})


if __name__ == '__main__':
    app.run()

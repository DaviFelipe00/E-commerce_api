
with app.app_context():
    db.drop_all()
    db.session.commit()
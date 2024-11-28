from app import create_app

def test_config():
    #assert 'postgresql' in create_app().config['SQLALCHEMY_DATABASE_URI']
    assert 'sqlite' in  create_app(local=True).config['SQLALCHEMY_DATABASE_URI']
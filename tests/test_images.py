import pytest
from flask import session

def test_home(auth,client):
    res= client.get('/')
    assert b'All' in res.data
    assert b'Log In' in res.data
    assert b'My Images' not in res.data
    assert b'My Likes' not in res.data
    auth.login()
    res= client.get('/')
    assert b'All' in res.data
    assert b'Log Out' in res.data
    assert b'My Images' in res.data
    assert b'My Likes' in res.data
    
def test_user_imgs(auth,client):
    with client:
        auth.login()
        client.get('/')
        assert session['twitter_oauth_token']['user_id'] == "1"
        res = client.get('/'+session['twitter_oauth_token']['user_id'])
        assert res.status_code == 200
        assert b'<div class="grid-item"' in res.data
        assert b'<a class="item active" href=/'+str.encode(session['twitter_oauth_token']['user_id']) in res.data
        res = client.get('/xxx')
        assert res.status_code == 404
        assert b'<div class="grid-item"' not in res.data

def test_my_likes(auth,client):
    res = client.get('/mylikes')
    assert res.status_code==302
    assert res.headers['location'] == 'http://localhost/auth/twitter'
    auth.login()
    res = client.get('/mylikes')
    assert res.status_code==200
    assert b'<div class="grid-item"' in res.data
    assert b'<a class="item active" href=/mylikes' in res.data
        
def test_add_new(auth,client):
    res = client.post('/new')
    assert res.status_code ==302
    assert res.headers['location'] == 'http://localhost/auth/twitter'
    auth.login()
    res = client.post('/new',data = {'url':'abcd','desc':'Not an url'},follow_redirects=True)
    assert b'Url does not exist' in res.data
    assert res.status_code ==200
    res = client.post('/new',data = {'url':'https://google.com','desc':'Not an image'},follow_redirects=True)
    assert b'Not a valid image' in res.data
    assert res.status_code ==200
    res = client.post('/new',data = {'url':'https://i.ytimg.com/vi/1R-QFQGWYuc/maxresdefault.jpg','desc':'An image'},follow_redirects=True)
    assert b'Not a valid image' not in res.data
    assert res.status_code == 200
    
    
@pytest.mark.parametrize('path',('/like','/unlike'))
def test_like_unlike(auth,client,path):
    res = client.put(path)
    assert res.status_code ==302
    assert res.headers['location'] == 'http://localhost/auth/twitter'
    auth.login()
    res = client.put(path,data={'id':"1"})
    assert res.status_code == 200
    res = client.put(path,data={'id':"999"})
    assert res.status_code == 404

@pytest.mark.parametrize(('img_id','status_code'),((1,403),(2,200),(3,403)))
def test_delete(auth,client,img_id,status_code):
    auth.login()
    assert client.delete('/delete',data={'img_id':img_id}).status_code == status_code
     
    
    
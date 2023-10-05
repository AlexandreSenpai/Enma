import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.core.handler import ApiError
from enma.sync.infra.adapters.request.http.implementations.sync import RequestsAdapter, RequestResponse

class TestRequest:
    def test_success_get_request(self):
        sut = RequestsAdapter()
        response = sut.get('https://google.com')

        assert response.status_code == 200
        assert response.text != ''
    
    def test_404_page(self):
        try:
            sut = RequestsAdapter()
            sut.get('https://www.alexandre-ramos.space/teste')
            assert False
        except ApiError as err:
            assert err.status_code == 404
            
    def test_request_with_params(self):
        sut = RequestsAdapter()
        response = sut.get('https://www.alexandre-ramos.space', params={'teste': 'teste'})

        assert response.status_code == 200
        assert response.host == 'https://www.alexandre-ramos.space/?teste=teste'
    
    def test_parse_params_to_url_encode_safe(self):
        sut = RequestsAdapter()
        encoded_string = sut.parse_params_to_url_safe(params={'id': 'Hellö Wörld@'})
        
        assert encoded_string == 'id=Hell%C3%B6%20W%C3%B6rld%40'
    
    def test_parse_params_to_url_encode_safe_without_special_chars(self):
        sut = RequestsAdapter()
        encoded_string = sut.parse_params_to_url_safe(params={'id': 'HelloWorld'})

        assert encoded_string == 'id=HelloWorld'
    
    def test_response_matches_with_interface(self):
        sut = RequestsAdapter()
        response = sut.get('https://www.alexandre-ramos.space')

        assert isinstance(response, RequestResponse)
    
    def test_get_response_as_json_successfully(self):
        sut = RequestsAdapter()
        response = sut.get('https://desktop-dot-nhentai.appspot.com')

        json = response.json()

        assert isinstance(json, dict)
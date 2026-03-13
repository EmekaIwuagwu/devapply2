import os
import requests
import streamlit as st

# Allow override via env var so the same image works for both:
#   • same-container deploys  (localhost:8000 — default)
#   • split-service deploys   (BACKEND_API_URL=https://devapply-api.onrender.com)
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")


class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL

    def _get_headers(self):
        headers = {}
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def post(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=data, headers=self._get_headers())
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return None

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return None

    def put(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.put(url, json=data, headers=self._get_headers())
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return None

    def delete(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url, headers=self._get_headers())
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return None

    def login(self, username, password):
        url = f"{self.base_url}/api/auth/login"
        data = {"username": username, "password": password}
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                st.session_state.access_token = token_data["access_token"]
                st.session_state.logged_in = True
                st.session_state.user_email = username
                return True
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Login failed: {e}")
            return False


api_client = APIClient()

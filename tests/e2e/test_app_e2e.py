"""
E2E tests for the Shinoutatime Streamlit app using AppTest.
"""
import pytest
from streamlit.testing.v1 import AppTest

class TestAppE2E:
    """E2E tests for the main application"""

    @pytest.fixture
    def app(self):
        """Fixture to initialize the app"""
        at = AppTest.from_file("Home.py", default_timeout=10)
        at.run()
        return at

    def test_app_startup(self, app):
        """Test that the app starts up and displays the title"""
        assert not app.exception
        assert "しのうたタイム" in app.title[0].value

    def test_search_functionality(self, app):
        """Test search functionality"""
        # Find the search input (first text input)
        search_input = app.text_input[0]
        
        # Simulate typing "Ghost"
        search_input.set_value("Ghost").run()
        
        # Click search button (first button in the form usually, or we can find by label if possible)
        # In render_search_form, st.form_submit_button("検索") is used.
        # AppTest treats form_submit_button as button.
        search_button = [b for b in app.button if b.label == "検索"][0]
        search_button.click().run()
        
        # Check if results are filtered (assuming "Ghost" exists in the mock/real data)
        # Note: Since we are running in a test environment, we might be using real data or need to mock it.
        # For now, we check if the search query state is updated.
        assert app.session_state.search_query == "Ghost"
        
        # Check if "検索結果" message appears
        assert any("検索した結果" in markdown.value for markdown in app.markdown)

    def test_pagination(self, app):
        """Test pagination controls"""
        # Check initial display limit
        assert app.session_state.display_limit == 25
        
        # Find the "もっと見る" button (last button usually)
        # We need to be careful identifying the specific button.
        # In Home.py, render_pagination creates a button if there are more results.
        
        # Assuming there are more than 25 records, the button should exist.
        # If we can't guarantee data, we might skip this assertion or mock data.
        # For this E2E, we rely on the environment having some data.
        
        buttons = app.button
        if buttons:
            # Click the last button (usually pagination)
            buttons[-1].click().run()
            # Check if limit increased
            assert app.session_state.display_limit > 25

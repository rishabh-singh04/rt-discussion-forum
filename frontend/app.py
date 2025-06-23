import streamlit as st
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"

class SessionState:
    def __init__(self):
        self.firebase_token = None
        self.current_user = None
        self.db_user = None
        self.show_login = True
        self.page_stack = []

def initialize_session():
    if 'state' not in st.session_state:
        st.session_state.state = SessionState()

def make_authenticated_request(method, endpoint, data=None):
    headers = {"Authorization": f"Bearer {st.session_state.state.firebase_token}"} if st.session_state.state.firebase_token else {}
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(f"{BACKEND_URL}{endpoint}", headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def get_or_create_user():
    if st.session_state.state.firebase_token and not st.session_state.state.db_user:
        response = make_authenticated_request("GET", "/auth/me")
        if response and response.status_code == 200:
            st.session_state.state.db_user = response.json()
            # Ensure username is properly set
            if 'username' not in st.session_state.state.db_user:
                st.session_state.state.db_user['username'] = (
                    st.session_state.state.db_user.get('email', '').split('@')[0] or
                    f"user_{st.session_state.state.db_user.get('id', '')}"
                )

def get_username(user_id, users_mapping):
    """Extract username from user ID with fallbacks"""
    user_data = users_mapping.get(user_id)
    if not user_data:
        return "Unknown"

    # Try different possible username fields
    username = (
        user_data.get('username') or
        user_data.get('user_name') or
        user_data.get('user', {}).get('username') or
        user_data.get('email', '').split('@')[0] or
        f"user_{user_data.get('id', '')}"
    )
    return username

# Authentication Pages
def show_entry_page():
    st.title("Welcome to Discussion Forum")
    st.write("Please login or register to continue")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.session_state.state.show_login = True
            st.rerun()
    with col2:
        if st.button("Register"):
            st.session_state.state.show_login = False
            st.rerun()

def show_login_page():
    st.title("Discussion Forum - Login")

    if st.button("← Back to Main"):
        st.session_state.state.show_login = None
        st.rerun()

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            with st.spinner("Logging in..."):
                response = requests.post(
                    f"{BACKEND_URL}/auth/get-firebase-token",
                    json={"email": email, "password": password}
                )

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.state.firebase_token = token_data["firebase_token"]
                    get_or_create_user()
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")

def show_signup_page():
    st.title("Discussion Forum - Sign Up")

    if st.button("← Back to Main"):
        st.session_state.state.show_login = None
        st.rerun()

    with st.form("signup_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if password != confirm_password:
                st.error("Passwords don't match!")
                return

            with st.spinner("Creating account..."):
                response = requests.post(
                    f"{BACKEND_URL}/auth/signup",
                    json={"email": email, "username": username, "password": password}
                )

                if response.status_code == 200:
                    st.success("Account created successfully! Please log in.")
                    st.session_state.state.show_login = True
                    st.rerun()
                else:
                    error_msg = response.json().get('detail', 'Unknown error')
                    if isinstance(error_msg, list):
                        error_msg = error_msg[0]['msg'] if error_msg else 'Unknown error'
                    st.error(f"Signup failed: {error_msg}")

# Main App Pages
def show_home_page():
    st.title("Discussion Forum")
    if st.session_state.state.db_user:
        username = get_username(st.session_state.state.db_user.get('id'), {st.session_state.state.db_user.get('id'): st.session_state.state.db_user})
        st.write(f"Welcome, {username}!")

    if st.button("← Back to Entry"):
        st.session_state.state.firebase_token = None
        st.session_state.state.current_user = None
        st.session_state.state.db_user = None
        st.session_state.state.show_login = None
        st.rerun()

    # Navigation Bar
    page = st.sidebar.radio(
        "Navigation",
        ["Browse Topics", "Create Topic", "Trending Topics", "My Notifications", "Profile"],
        key="main_nav"
    )

    if page == "Browse Topics":
        show_browse_topics_page()
    elif page == "Create Topic":
        show_create_topic_page()
    elif page == "Trending Topics":
        show_trending_topics_page()
    elif page == "My Notifications":
        show_notifications_page()
    elif page == "Profile":
        show_profile_page()

def show_browse_topics_page():
    st.header("Browse Topics")

    search_query = st.text_input("Search topics")
    endpoint = f"/search?query={search_query}" if search_query else "/topics"
    response = make_authenticated_request("GET", endpoint)

    if response and response.status_code == 200:
        topics = response.json()

        if not topics:
            st.info("No topics found")
            return

        # Fetch all users to map user IDs to usernames
        users_response = make_authenticated_request("GET", "/users")
        users_mapping = {}
        if users_response and users_response.status_code == 200:
            users = users_response.json()
            users_mapping = {user['id']: user for user in users}

        # Display all topics
        for topic in topics:
            with st.container(border=True):
                st.markdown(f"### {topic.get('title', 'Untitled')}")
                st.caption(f"by {get_username(topic.get('author_id'), users_mapping)}")
                st.write(topic.get('content', ''))
                st.caption(f"Created at: {topic.get('created_at', 'Unknown')}")
                st.caption(f"Comments: {len(topic.get('comments', []))}")

                # Delete topic button (only for author or admin)
                if st.session_state.state.db_user and st.session_state.state.db_user.get('id') == topic.get('author_id'):
                    if st.button(f"Delete Topic", key=f"delete_topic_{topic.get('id')}"):
                        with st.spinner("Deleting topic..."):
                            response = make_authenticated_request("DELETE", f"/topics/{topic.get('id')}")
                            if response and response.status_code == 200:
                                st.success("Topic deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete topic")

                # View comments
                comments_response = make_authenticated_request("GET", f"/comments/{topic.get('id')}")
                if comments_response and comments_response.status_code == 200:
                    comments = comments_response.json()
                    if comments:
                        st.subheader("Comments")
                        for comment in comments:
                            with st.container(border=True):
                                st.markdown(f"**{get_username(comment.get('author_id'), users_mapping)}**: {comment.get('content', '')}")
                                st.caption(f"Posted at: {comment.get('created_at', 'Unknown')}")
                                # Delete comment button (only for author or admin)
                                if st.session_state.state.db_user and st.session_state.state.db_user.get('id') == comment.get('author_id'):
                                    if st.button("🗑️ Delete", key=f"delete_comment_{comment.get('id')}"):
                                        with st.spinner("Deleting comment..."):
                                            response = make_authenticated_request("DELETE", f"/comments/{comment.get('id')}")
                                            if response and response.status_code == 200:
                                                st.success("Comment deleted successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete comment")

                # Add comment
                with st.form(key=f"comment_form_{topic.get('id', '')}"):
                    comment_text = st.text_area("Add a comment")
                    submitted = st.form_submit_button("Post Comment")
                    if submitted and comment_text:
                        if not st.session_state.state.db_user:
                            st.error("Please log in to post comments")
                            return

                        response = make_authenticated_request(
                            "POST",
                            f"/topics/{topic.get('id')}/comments",
                            {"content": comment_text}
                        )
                        if response and response.status_code == 201:
                            st.success("Comment posted!")
                            st.rerun()
                        else:
                            st.error(f"Failed to post comment: {response.json().get('detail', 'Unknown error') if response else 'Network error'}")

def show_trending_topics_page():
    st.header("Trending Topics")

    response = make_authenticated_request("GET", "/topics")

    if response and response.status_code == 200:
        topics = response.json()

        if not topics:
            st.info("No topics found")
            return

        # Fetch all users to map user IDs to usernames
        users_response = make_authenticated_request("GET", "/users")
        users_mapping = {}
        if users_response and users_response.status_code == 200:
            users = users_response.json()
            users_mapping = {user['id']: user for user in users}

        # Display trending topics
        trending_topics = sorted(topics, key=lambda x: len(x.get('comments', [])), reverse=True)[:5]
        for topic in trending_topics:
            with st.container(border=True):
                st.markdown(f"### {topic.get('title', 'Untitled')}")
                st.caption(f"by {get_username(topic.get('author_id'), users_mapping)}")
                st.write(topic.get('content', ''))
                st.caption(f"Created at: {topic.get('created_at', 'Unknown')}")
                st.caption(f"Comments: {len(topic.get('comments', []))}")

def show_create_topic_page():
    st.header("Create New Topic")

    if not st.session_state.state.db_user:
        st.error("Please log in to create topics")
        return

    with st.form("create_topic_form"):
        title = st.text_input("Title", max_chars=100)
        content = st.text_area("Content", height=200)
        submitted = st.form_submit_button("Create Topic")

        if submitted:
            if not title or not content:
                st.error("Title and content are required")
                return

            with st.spinner("Creating topic..."):
                response = make_authenticated_request(
                    "POST",
                    "/topics",
                    {
                        "title": title,
                        "content": content,
                        "author_id": st.session_state.state.db_user.get('id')
                    }
                )

                if response and response.status_code == 201:
                    st.success("Topic created successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to create topic: {response.json().get('detail', 'Unknown error') if response else 'Network error'}")

def show_notifications_page():
    st.header("My Notifications")

    if not st.session_state.state.db_user:
        st.error("Please log in to view notifications")
        return

    response = make_authenticated_request("GET", "/notifications")
    if response and response.status_code == 200:
        notifications = response.json()
        notifications_list = notifications if isinstance(notifications, list) else notifications.get("notifications", [])

        if not notifications_list:
            st.info("No notifications yet")
            return

        for notification in notifications_list:
            with st.container():
                st.write(notification.get('message', 'No message'))
                if notification.get('topic_title'):
                    st.caption(f"Related to: {notification['topic_title']}")
                st.caption(f"Received at: {notification.get('created_at', 'Unknown')}")
                st.divider()

def show_profile_page():
    st.header("My Profile")

    if st.session_state.state.db_user:
        username = get_username(st.session_state.state.db_user.get('id'), {st.session_state.state.db_user.get('id'): st.session_state.state.db_user})
        email = st.session_state.state.db_user.get('email', 'Unknown')

        st.markdown(f"<h3 style='color: #4CAF50;'>Username: {username}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #2196F3;'>Email: {email}</p>", unsafe_allow_html=True)

        if st.button("Delete Account"):
            with st.spinner("Deleting account..."):
                response = make_authenticated_request("DELETE", f"/users/{st.session_state.state.db_user.get('id')}")
                if response and response.status_code == 204:
                    st.success("Account deleted successfully!")
                    st.session_state.state.firebase_token = None
                    st.session_state.state.current_user = None
                    st.session_state.state.db_user = None
                    st.session_state.state.show_login = None
                    st.rerun()
                else:
                    st.error("Failed to delete account")

        if st.button("Log Out"):
            st.session_state.state.firebase_token = None
            st.session_state.state.current_user = None
            st.session_state.state.db_user = None
            st.session_state.state.show_login = None
            st.rerun()
    else:
        st.error("No user information available")

# Main App Flow
def main():
    st.set_page_config(page_title="Discussion Forum", layout="wide")
    initialize_session()

    # Initialize user data if we have a token
    if st.session_state.state.firebase_token and not st.session_state.state.db_user:
        get_or_create_user()

    # Show appropriate page based on state
    if st.session_state.state.firebase_token and st.session_state.state.db_user:
        show_home_page()
    elif st.session_state.state.show_login is True:
        show_login_page()
    elif st.session_state.state.show_login is False:
        show_signup_page()
    else:
        show_entry_page()

if __name__ == "__main__":
    main()


import pyrebase

try:
    from firebase_config import firebaseConfig
except:
    from firebase.firebase_config import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()


def log_in(email, password):
    try:

        user = auth.sign_in_with_email_and_password(email, password)
        
        return 0

    except Exception as e:
        print('Login error {}'.format(e))
        return 1


def sign_up(email, password):

    try:
        
        auth.create_user_with_email_and_password(email, password)
        
        return 0

    except Exception as e:
        print('Signup error {e["message"]}'.format(e))
        return 1


. orchestra_env.sh

flask shell <<- EOM
from orchestra.webservice.auth.models import User
u = User(username="admin", password="admin", email="admin@orchestra.org")
db.session.add(u)
db.session.commit()
print("Administrator created")
EOM

mongosh -- "$MONGODB_DATABASE" <<EOF
    var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
    var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
    var admin = db.getSiblingDB('admin');
    admin.auth(rootUser, rootPassword);

    var user = '$MONGODB_USERNAME';
    var passwd = '$MONGODB_PASSWORD';

    db.createUser({user: user, pwd: passwd, roles: ["readWrite", "dbAdmin"]});
    use $MONGODB_DATABASE;
    db.auth(user, passwd);
    db.Users.insertOne({
        "_cls": "UserModel",
        "email": "blog@example.com",
        "fullname": "Blog Demo",
        "password": "$2b$12$cyQZ0g3BvPdvDIzV87hv6ulJWUtdZnj.5YHtxZ4gzIXxVvmqI7z6i",
        "role": "admin",
        "avatar": "https://res.cloudinary.com/dxzrtwxdj/image/upload/v1702007461/woweogxayzrv5jl1rce2.png"
    });
EOF

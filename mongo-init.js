db = db.getSiblingDB("flaskdb");
db.createUser({
  user: "flaskuser",
  pwd: "yourpasswpasord",
  roles: [
    {
      role: "readWrite",
      db: "flaskdb",
    },
  ],
});

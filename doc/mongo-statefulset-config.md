# MongoDB Replicaset Configuration

Assuming that the MongoDB replicas are named `mongo-#.mongo`, where `#` is a number, and the name `mongo` after the dot (`.`) is the name of the headless service, we can initialize as:

## Initialization
Choose and initialize the primary.
```javascript
rs.initiate( {
  _id: "rs0",
  members:[ { _id: 0, host: "mongo-0.mongo:27017" } ]
 });
```
Next, add the secondary members.
```javascript
rs.add("mongo-1.mongo:27017");
rs.add("mongo-2.mongo:27017");
```



## Reconfiguration
To check the status, use `rs.status()`
To reconfigure after initialization, use:
```javascript
rsconf = rs.conf()
rsconf.members = [{_id: 0, host: "mongo-0.mongo:27017"}]
rs.reconfig(rsconf, {force: true})
```

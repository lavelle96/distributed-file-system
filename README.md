# Distributed File System
A RESTful distributed NFS implemented in python that implements features such as **transparent file access, locking, caching, a directory service, file replication and authentication**.

## __Running the system__
### Prerequisites
- The system uses linux commands to open files (when reading files, it opens them in the default program for that file type for the OS).
- Mongo db is needed to run the system
## Running the scripts
- Each of the servers have a bash script in the src folder for running it
- The default ports they start on are in the config files however these can be changed for every file except for the registry server port, that has to be known by all servers.
## Order of Servers
- The database must be set up first
- Followed by the registry server
- Followed by every server except for the file servers
- The file servers can then be started 
- By this stage the system is up and running and the client program can be started by calling ```python Client.py```
## __Basic Structure__
## Database
The database used was [mongodb](https://www.mongodb.com), it is a document orientated database technology. It is very flexible and stores objects as json-like objects which makes it easy to deal with, especially using api's when json is such an easy method to pass information around.

## Client End
- A client using the file system has six options upon startup, they can read, write, create and delete files, they can also find out which files are stored on the file system by using the 'show' command and find information on the syntax of the commmands using the 'help' command.
- If the client has admin clearance, it has two more options - to add another user to the database and to list the currently registered users.
- The client does not need any information about what goes on behind these commands, except for the address of the *Registry Server*, this is the server that stores the whereabouts of each other server in the system. This address will be constant throughout the lifetime of the system.
- For example to read a file, the syntax is as as simple as *read <file_name>* and everything else is handled under the hood.

## Servers
### Registry Server
- Keeps track of which server are online
- One json stucture in database, entry structure:
```python
{
    'dir_name':
    'dir_port':
    'dir_load': (used to decide which file server will handle the request)
}
```
- When a server comes online it sends a post request to the registry server and that server is added to the database.
- Has a **thread** that routinely checks the state of servers, if a server goes down, the registry server will find out and remove it from the database. Each server has an endpoint to allow requests for its current state (whether or not it is still alive) to accommodate this. That same endpoint also allows servers to be shut down with a delete request.
- Also provides load balancing for all servers except the file servers (this balancing is handled by the directory server). So for example if something is looking for the address of a directory server and there are two directory servers online, the address of the server that has handled the least amount of requests will be returned 

### File Server
- The file servers are completely stateless
- Endpoint for file manipulation: 
  - Get - Reading a file
  - Post - Writing/Creating a file, also sends this request on to the directory server so that it is replicated across all file servers that support the file.
  - Delete - Deleting a file, provides the same **replication** functionality as the post.

### Directory Server
- The directory server provides a lot of functionality for managing the files servers
- Has two json file structures stored in the database:
  - Active nodes: Keeps track of the address of the file servers that are online, which files they’re supporting and the load on that file server. Structure:
  ```python
  {
    'port':
    'file_names': []
    'load':
  }
  ```
  - File map: Keeps track of the files that exist in the file system, the amount of file servers each is supported by and the associated addresses of those file servers. The version of the file is also stored. 
  Structure:
  ```python
  {
    'file_name':
    'num_nodes':
    'ports':
    'file_version':
  }  
  ```
- Has an endpoint for overall management of specific files:
  - **Get** - Gets the port of a specified file, if more than one server support the file, the address of the server with the lesser load will be returned
  - **Post** - Creates or updates a file in the database, this request is sent by a file server after a file server updates or creates a file to ensure consistency in the database and also to allow **replication** of the changes across other file servers that are supporting that file. When the directory server receives this request it sends a write request on to all file servers that support the file.
  - **Delete** - Deletes a file from the database and deletes it from every node that supports it (used in a similar fashion to the post request).
- Also has an endpoint that handles keeping track of which file servers exist.
  - **Post** - File servers post to this endpoint with the files that they support when they come online, this information is then stored in the database.
  - **Delete** - Deletes a file server from the directory servers database, usually sent by the file server before it goes down but also sent when the registry server notices a file server is down.
- Another endpoint is used to get all the files that the directory server controls
  - **Get** - returns all files in the database.
- The last unique endpoint of the directory server manages returning the version for a given file.
  - **Get** - returns the version of the specified file.

### Locking Server
- Has one json file structure stored in a database, this stores the filenames of files that have been locked before or are currently locked, in these objects it also stores whether or not the file is locked and the queue containing the addresses of those looking to lock the file. Here is the basic structure: 
```python 
{
    'file_name':
    'is_locked':
    'lock_holders': [queue of client ids]
}
```
- Has one unique endpoint to manage the ownership of locks
  - **Get** - If a user is looking to lock a file, it sends a get request. If the file doesn't exist in the db, it is added and the lock for that file is returned. If the file exists and is unlocked,  the lock is returned if the the queue is empty or the user is top of the queue (with each request session a uuid is given the whoever requests a lock to identify users in the queue). If the file exists and is locked, the user is added to the end of the queue.
  - **Post** - Allows a user to release a lock it had previously obtained. In order to identify the user correctly, the user must provide the uuid that was given to them in their request to obtain the lock.

### Cache Server (runs locally on the clients machine)
- Is run on the client's machine locally, doing this allows us to use the API technology that is used across the project.
- Has one json file structure stored in a database that keeps track of the the files in the cache along with the version number of those files and a timestamp of when it was added to the cache or when it was last used. Structure:
```python
{
    'file_name':
    'file_version':
    'timestamp':
}
```
- Has one unique endpoint to manage addition and retrieval from the cache
  - **Get** - Returns the file from the cache if it exists in the cache and is up to date with the latest version of the file, the latest version of the file is retrieved by requesting it from the directory server.
  - **Post** - Adds a file to the cache, if the cache is full it replaces the file that was least recently used (this is decided by the time stamps that are stored in the db that indicate when the file was last used).

### Authentication Server
- Server to ensure clients that use the file server are validated
- Two modes of access - user mode and admin mode, database object structure:
```python
{
  'username':
  'password':
  'privilege':
}
```
- Admins can add new users and list currently validated users
- Has three unique endpoints
- The first is one that manages user logins
  - **Get** - Returns true if provided username and password is valid
- The second handles auth requests for single users
  - **Get** - Returns true if provided username and password have admin clearance
  - **Post** - Adds user to database if correct admin details are provided
- The third handles the admin request for multiple users
  - **Get** - Returns a list of the currently registered clients if the admin details provided are valid

## Features
### Replication
Replication of files across different file servers is mostly managed by the the directory server. When a file server changes or deletes a file, it sends the details of those changes onto the directory server who sends them on again to every file server who supports the given file.

It is also import that when one of the file servers that supports the file goes down, access to the file is still available. This is done by letting the directory server know as soon as possible that the file server has gone down. This is managed by the registry server who constantly checks the status of the servers in the system.

### Locking
I chose to lock files when they are opened with write privileges. This means that when a client opens a file with write privileges, another client cant access that file until the lock has been released by the first client.

### Caching
When the cache is full, the method I chose to choose a file to remove from the cache is LRU. This means that the file that was the least recently used is removed.

### Authentication
The system has one root admin, the credentials of that admin are hardcoded into the config.py file. At the birth of the system, he is the only one who can insert new users into the database.



